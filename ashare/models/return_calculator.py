from typing import List, Tuple
from datetime import date, timedelta
from decimal import Decimal
import numpy as np
from scipy.optimize import newton
from .trade_record import TradeRecord
from .daily_quote import DailyQuote
from .dividend import Dividend
import logging
from ashare.logger.setup_logger import get_logger

class ReturnCalculator:
    def __init__(self, trades: List[TradeRecord], quotes: List[DailyQuote], dividends: List[Dividend]):
        self.trades = sorted(trades, key=lambda x: x.trade_date)  # 按交易日期排序
        self.quotes = {q.trade_date: q for q in quotes}  # 转换为日期索引的字典
        self.dividends = sorted([d for d in dividends if d.div_proc == '实施'], key=lambda x: x.base_date if x.base_date else date.max)  # 按除权日排序
        self.logger = get_logger()

    def calculate_position_shares(self, current_date: date) -> Decimal:
        """计算指定日期的持仓数量（考虑送转股）"""
        shares = Decimal('0')
        
        # 将交易和送转事件合并并按日期排序
        events = []
        for trade in self.trades:
            if trade.trade_date <= current_date:
                events.append(('trade', trade.trade_date, trade))
                
        for div in self.dividends:
            if div.base_date and div.base_date <= current_date and div.div_proc=='实施':
                events.append(('dividend', div.base_date, div))
        
        # 按日期排序
        events.sort(key=lambda x: x[1])
        
        # 按时间顺序处理每个事件
        for event_type, event_date, event in events:
            if event_type == 'trade':
                if event.trade_type == 'buy':
                    shares += event.trade_shares
                else:
                    shares -= event.trade_shares
            else:  # dividend
                # 送股
                if event.stk_bo_rate:
                    shares += shares * event.stk_bo_rate
                # 转增
                if event.stk_co_rate:
                    shares += shares * event.stk_co_rate
                
        return shares
    
    def get_final_value(self, end_date: date) -> Decimal:
        """计算指定日期的最终市值"""
        shares = self.calculate_position_shares(end_date)
        if shares <= Decimal('0'):
            return Decimal('0')
        quote = self.quotes.get(end_date)
        if not quote:
            raise ValueError(f"没有找到 {end_date} 的行情数据")
        return shares * quote.close

    def get_cash_flows(self, end_date: date) -> List[Tuple[date, Decimal]]:
        """获取所有现金流（包括买入、卖出、分红）"""
        cash_flows = []
        
        # 添加交易现金流
        for trade in self.trades:
            if trade.trade_date > end_date:
                continue
            if trade.trade_type == 'buy':
                # 买入为负现金流（投入）
                amount = -(trade.trade_amount + trade.commission + trade.tax)
            else:
                # 卖出为正现金流（收回）
                amount = trade.trade_amount - trade.commission - trade.tax
            cash_flows.append((trade.trade_date, amount, '交易'))

        # 添加分红现金流
        for div in self.dividends:
            if not div.base_date or div.base_date > end_date:
                continue
            shares = self.calculate_position_shares(div.base_date)
            if shares > Decimal('0'):
                cash_flows.append((div.pay_date or div.ex_date, shares * div.cash_div, '分红'))

        return sorted(cash_flows, key=lambda x: x[0])
    
    # 计算净现金流入值
    def calculate_net_cash_flow_value(self, end_date: date) -> Decimal:
        """计算指定日期的净现金流入值"""
        cash_flows = self.get_cash_flows(end_date)
        # 确保返回值为Decimal类型
        return Decimal(sum(cf[1] for cf in cash_flows))
    
    def _get_cash_flows_with_final_value(self, end_date: date) -> List[Tuple[date, Decimal]]:
        """获取所有现金流（包括买入、卖出、分红），并添加最终市值"""
        cash_flows = self.get_cash_flows(end_date)
        final_value = self.get_final_value(end_date)
        if final_value > Decimal('0'):
            cash_flows.append((end_date, final_value))
        return sorted(cash_flows, key=lambda x: x[0])

    def _xirr(self, cash_flows: List[Tuple[date, Decimal]]) -> Decimal:
        """计算XIRR"""
        if not cash_flows:
            return Decimal('0')

        # 转换为numpy数组以便计算
        amounts = np.array([float(cf[1]) for cf in cash_flows])
        dates = np.array([(cf[0] - cash_flows[0][0]).days / 365.0 for cf in cash_flows])
        
        def xnpv(rate):
            return np.sum(amounts / (1 + rate) ** dates)

        def xnpv_deriv(rate):
            return np.sum(-dates * amounts / (1 + rate) ** (dates + 1))

        try:
            rate = newton(xnpv, x0=0.1, fprime=xnpv_deriv, maxiter=1000)
            self.logger.info(f"cash_flows={cash_flows}, XIRR: {rate}")  # Log the rate inf
            return Decimal(str(rate))
        except:
            return Decimal('0')

    def calculate_annualized_return(self, evaluation_date: date = None) -> Decimal:
        """
        使用XIRR方法计算年化收益率
        
        Args:
            evaluation_date: 评估日期，默认使用最后一个交易日
            
        Returns:
            Decimal: 年化收益率
        """
        if not self.trades:
            return Decimal('0')

        end_date = evaluation_date or max(self.quotes.keys())
        cash_flows = self._get_cash_flows_with_final_value(end_date)
        
        if not cash_flows:
            return Decimal('0')
            
        rate = self._xirr(cash_flows)
        
        return rate