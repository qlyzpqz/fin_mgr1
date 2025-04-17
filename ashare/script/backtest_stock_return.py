from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple
import pandas as pd

from ashare.models import return_calculator
from ashare.models.sync_service import SyncService
from ashare.models.stock_trader import StockTrader, TradeAction
from ashare.models.stock_repository import StockRepository
from ashare.models.daily_quote_repository import DailyQuoteRepository
from ashare.models.daily_indicator_repository import DailyIndicatorRepository
from ashare.models.dividend_repository import DividendRepository
from ashare.models.financial_report_repository import FinancialReportRepository
from ashare.models.return_calculator import ReturnCalculator
import os
import logging
from ashare.script.setup_log import setup_logging

from ashare.models.trade_record import TradeRecord

class StockBacktester:
    def __init__(self, 
                 start_date: date,
                 end_date: date,
                 initial_capital: float = 1000000.0):  # 默认100万初始资金
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = Decimal(initial_capital)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"初始化 StockBacktester, 回测期间: {start_date} 至 {end_date}, 初始资金: {initial_capital}")
        
        # 初始化数据仓库
        self.db_path = 'backtest_ashare_stock.db'
        self.stock_repo = StockRepository(db_path=self.db_path)
        self.quote_repo = DailyQuoteRepository(db_path=self.db_path)
        self.indicator_repo = DailyIndicatorRepository(db_path=self.db_path)
        self.dividend_repo = DividendRepository(db_path=self.db_path)
        self.financial_repo = FinancialReportRepository(db_path=self.db_path)
        
        # 同步数据
        self._sync_data()

    def _sync_data(self):
        """同步股票数据"""
        self.logger.info("开始同步数据")
        tushare_token = os.getenv('TUSHARE_TOKEN') or ""
        sync_service = SyncService(db_path=self.db_path, tushare_token=tushare_token, ts_codes=["600519.SH", "000568.SZ", "000858.SZ", "000333.SZ"])
        sync_service.sync_all()
        
    def _load_data(self, stock_code: str):
        """加载指定股票的回测所需数据"""
        # 获取股票信息和上市日期
        self.logger.info(f"开始加载股票数据: {stock_code}")
        stock = self.stock_repo.find_by_ts_code(stock_code)
        if not stock:
            raise ValueError(f"股票代码 {stock_code} 不存在")
        self.list_date = stock.list_date
        self.stock_code = stock_code
        
        self.daily_quotes = self.quote_repo.find_by_code(stock_code)
        self.daily_indicators = self.indicator_repo.find_by_code(stock_code)
        self.dividends = self.dividend_repo.find_by_code(stock_code)
        self.financial_reports = self.financial_repo.get_all(stock_code)
        self.trades = []
        
    def _get_price(self, current_date: date) -> float:
        """获取指定日期的收盘价"""
        quote = next((q for q in self.daily_quotes if q.trade_date == current_date), None)
        if quote:
            self.logger.info(f"获取 {self.stock_code} 在 {current_date} 的收盘价: {quote.close}")
            return (float(quote.open) + float(quote.close)) / 2.0
        else:
            return -1.0
        
    def backtest_stock(self, stock_code: str) -> pd.DataFrame:
        """对单只股票进行回测"""
        # 加载股票数据
        self._load_data(stock_code)
        
        results = []
        current_date = self.start_date
        if current_date < self.list_date:
            current_date = self.list_date
        
        while current_date <= self.end_date:
            self.logger.info(f"正在回测 {stock_code} 的 {current_date} 日数据")
            price = self._get_price(current_date)
            
            if price < 0:
                current_date += timedelta(days=1)
                continue
            
            # 创建交易决策器
            trader = StockTrader(
                daily_indicators=self.daily_indicators,
                daily_quotes=self.daily_quotes,
                dividends=self.dividends,
                financial_reports=self.financial_reports,
                target_date=current_date
            )
            
            yesterday_date = current_date - timedelta(days=1)
            yesterday_return_calculator = ReturnCalculator(self.trades, self.daily_quotes, self.dividends)
            yesterday_position = yesterday_return_calculator.calculate_position_shares(yesterday_date)
            yesterday_capital = self.initial_capital + yesterday_return_calculator.calculate_net_cash_flow_value(yesterday_date)
            today_position = yesterday_position
            today_capital = yesterday_capital
        
            # 获取交易决策
            action = trader.get_action()
            if action == TradeAction.BUY:
                # 全仓买入
                shares = int(yesterday_capital / Decimal(price) / 100) * 100  # 按手（100股）取整
                cost = Decimal(price) * shares
                if shares > 0:
                    self.trades.append(TradeRecord(
                        ts_code=stock_code,
                        trade_date=current_date,
                        trade_price=Decimal(price),
                        trade_shares=Decimal(shares),
                        trade_type='buy',
                        trade_amount=cost,
                        commission=Decimal(0),
                        tax=Decimal(0)
                    ))
                    today_position += shares
                    today_capital -= cost
            elif action == TradeAction.SELL and yesterday_position > 0:
                # 全仓卖出
                proceeds = Decimal(price) * yesterday_position
                self.trades.append(TradeRecord(
                        ts_code=stock_code,
                        trade_date=current_date,
                        trade_price=Decimal(price),
                        trade_shares=Decimal(yesterday_position),
                        trade_type='sell',
                        trade_amount=proceeds,
                        commission=Decimal(0),
                        tax=Decimal(0)
                    ))
                today_position += 0
                today_capital += proceeds
            
            today_return_calculator = ReturnCalculator(self.trades, self.daily_quotes, self.dividends)
            results.append({
                'date': current_date,
                'price': price,
                'yesterday_position': float(yesterday_position),
                'yesterday_capital': float(yesterday_capital),
                'today_position': today_return_calculator.calculate_position_shares(current_date),
                'today_capital': float(today_capital),
                'init_capital': float(self.initial_capital),
                'net_cash_flow_value': float(today_return_calculator.calculate_net_cash_flow_value(current_date)),
                'final_value': float(today_return_calculator.get_final_value(current_date)),
                'total_value': float(self.initial_capital + today_return_calculator.calculate_net_cash_flow_value(current_date) + today_return_calculator.get_final_value(current_date)),
                'return_rate': today_return_calculator.calculate_annualized_return(current_date) * 100,
            })
            
            current_date += timedelta(days=1)
        
        return_calculator = ReturnCalculator(self.trades, self.daily_quotes, self.dividends)
        cash_flows = return_calculator.get_cash_flows(self.end_date)
        print(cash_flows)
        
        for trade in self.trades:
            print(trade)
        
        return pd.DataFrame(results)
        
    def run(self) -> Dict[str, pd.DataFrame]:
        """运行所有股票的回测"""
        results = {}
        stocks = self.stock_repo.find_all()
        
        for stock in stocks:
            self.logger.info(f"开始回测股票: {stock.ts_code}--{stock.name}")
            print(f"正在回测股票: {stock.ts_code}--{stock.name}")
            df = self.backtest_stock(stock.ts_code)
            results[stock.ts_code] = df
            
            # 输出回测结果
            print(f"\n回测结果 - {stock.ts_code}")
            print(f"回测期间: {self.start_date} 至 {self.end_date}")
            print(f"初始资金: {self.initial_capital:,.2f}")
            print(f"期末总值: {df.iloc[-1]['total_value']:,.2f}")
            print(f"总收益率: {df.iloc[-1]['return_rate']:.2f}%")
            print("-" * 50)
            
            self.logger.info(f"回测结果 - {stock.ts_code}")
            self.logger.info(f"回测期间: {self.start_date} 至 {self.end_date}")
            self.logger.info(f"初始资金: {self.initial_capital:,.2f}")
            self.logger.info(f"期末总值: {df.iloc[-1]['total_value']:,.2f}")
            self.logger.info(f"总收益率: {df.iloc[-1]['return_rate']:.2f}%")
            self.logger.info("-" * 50)  
            
            # 保存详细结果到CSV
            df.to_csv(f'backtest_{stock.ts_code}_{self.start_date}_{self.end_date}.csv', index=False)
                
        return results

def main():
    # 设置回测参数
    start_date = date(2010, 1, 1)
    end_date = date.today() - timedelta(days=1)
    initial_capital = 1000000.0  # 100万初始资金
    
    # 创建回测器并运行
    backtester = StockBacktester(start_date, end_date, initial_capital)
    results = backtester.run()

if __name__ == '__main__':
    setup_logging()
    main()
