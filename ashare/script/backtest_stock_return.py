from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple
import pandas as pd

from ashare.models.sync_service import SyncService
from ashare.models.stock_trader import StockTrader, TradeAction
from ashare.models.stock_repository import StockRepository
from ashare.models.daily_quote_repository import DailyQuoteRepository
from ashare.models.daily_indicator_repository import DailyIndicatorRepository
from ashare.models.dividend_repository import DividendRepository
from ashare.models.financial_report_repository import FinancialReportRepository
from ashare.tests.test_sync_service import tushare_token
import os

class StockBacktester:
    def __init__(self, 
                 stock_code: str,
                 start_date: date,
                 end_date: date,
                 initial_capital: float = 1000000.0):  # 默认100万初始资金
        self.stock_code = stock_code
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.stock_position = 0
        
        # 初始化数据仓库
        self.db_path = 'ashare_stock.db'
        self.stock_repo = StockRepository(db_path=self.db_path)
        self.quote_repo = DailyQuoteRepository(db_path=self.db_path)
        self.indicator_repo = DailyIndicatorRepository(db_path=self.db_path)
        self.dividend_repo = DividendRepository(db_path=self.db_path)
        self.financial_repo = FinancialReportRepository(db_path=self.db_path)
        
        # 同步数据
        self._sync_data()
        
        # 加载回测期间的数据
        self._load_data()
        
    def _sync_data(self):
        """同步股票数据"""
        tushare_token = os.getenv('TUSHARE_TOKEN')
        sync_service = SyncService(db_path=self.db_path, tushare_token='your_tushare_token')
        sync_service.sync_all()
        
    def _load_data(self):
        """加载回测所需的数据"""
        self.daily_quotes = self.quote_repo.get_quotes_by_date_range(
            self.stock_code
        )
        self.daily_indicators = self.indicator_repo.get_indicators_by_date_range(
            self.stock_code
        )
        self.dividends = self.dividend_repo.get_dividends_by_code(self.stock_code)
        self.financial_reports = self.financial_repo.get_reports_by_code(self.stock_code)
        
    def _get_price(self, trade_date: date) -> Decimal:
        """获取指定日期的收盘价"""
        for quote in self.daily_quotes:
            if quote.trade_date == trade_date:
                return quote.close
        return Decimal('0')
        
    def run(self) -> pd.DataFrame:
        """运行回测"""
        results = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # 创建交易决策器
            trader = StockTrader(
                daily_indicators=self.daily_indicators,
                daily_quotes=self.daily_quotes,
                dividends=self.dividends,
                financial_reports=self.financial_reports,
                target_date=current_date
            )
            
            # 获取交易决策
            action = trader.get_action()
            price = self._get_price(current_date)
            
            # 执行交易
            if price > 0:  # 确保有效的交易价格
                if action == TradeAction.BUY and self.stock_position == 0:
                    # 全仓买入
                    shares = int(self.current_capital / float(price) / 100) * 100  # 按手（100股）取整
                    cost = float(price) * shares
                    if cost <= self.current_capital:
                        self.stock_position = shares
                        self.current_capital -= cost
                        
                elif action == TradeAction.SELL and self.stock_position > 0:
                    # 全仓卖出
                    proceeds = float(price) * self.stock_position
                    self.current_capital += proceeds
                    self.stock_position = 0
            
            # 记录当日结果
            total_value = self.current_capital + self.stock_position * float(price)
            results.append({
                'date': current_date,
                'action': action.value,
                'price': float(price),
                'position': self.stock_position,
                'cash': self.current_capital,
                'total_value': total_value,
                'return_rate': (total_value / self.initial_capital - 1) * 100  # 收益率(%)
            })
            
            current_date += timedelta(days=1)
            
        return pd.DataFrame(results)

def main():
    # 设置回测参数
    stock_code = '000001.SZ'  # 平安银行
    start_date = date(2022, 1, 1)
    end_date = date(2022, 12, 31)
    initial_capital = 1000000.0  # 100万初始资金
    
    # 创建回测器并运行
    backtester = StockBacktester(stock_code, start_date, end_date, initial_capital)
    results = backtester.run()
    
    # 输出回测结果
    print(f"\n回测结果 - {stock_code}")
    print(f"回测期间: {start_date} 至 {end_date}")
    print(f"初始资金: {initial_capital:,.2f}")
    print(f"期末总值: {results.iloc[-1]['total_value']:,.2f}")
    print(f"总收益率: {results.iloc[-1]['return_rate']:.2f}%")
    
    # 保存详细结果到CSV
    results.to_csv(f'backtest_{stock_code}_{start_date}_{end_date}.csv', index=False)
    
if __name__ == '__main__':
    main()