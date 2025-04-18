import time
from typing import List
from decimal import Decimal
from enum import Enum
from datetime import date

from pandas.tseries.offsets import YearBegin

from ashare.tests.test_stock_repository import repo
from .financial_report import FinancialReport
from .daily_indicator import DailyIndicator
from .daily_quote import DailyQuote
from .dividend import Dividend
from datetime import timedelta
import logging
from ashare.logger.setup_logger import get_logger

class TradeAction(Enum):
    """交易动作枚举"""
    BUY = "买入"
    SELL = "卖出"
    HOLD = "持有"

class StockTrader:
    """股票交易决策类"""
    
    def __init__(self, 
                 daily_indicators: List[DailyIndicator],
                 daily_quotes: List[DailyQuote],
                 dividends: List[Dividend],
                 financial_reports: List[FinancialReport],
                 target_date: date,
                 discount_rate: float = 0.05,  # 折现率默认5%
                 risk_free_rate: float = 0.05):  # 无风险收益率默认3%
        # 筛选目标日期之前的数据
        self.target_date = target_date
        self.daily_indicators = sorted(
            [ind for ind in daily_indicators if ind.trade_date <= target_date],
            key=lambda x: x.trade_date, 
            reverse=True
        )
        self.daily_quotes = sorted(
            [quote for quote in daily_quotes if quote.trade_date <= target_date],
            key=lambda x: x.trade_date, 
            reverse=True
        )
        self.dividends = sorted(
            [div for div in dividends if div.ann_date and div.ann_date <= target_date],
            key=lambda x: x.ann_date, 
            reverse=True
        )
        self.financial_reports = sorted(
            [report for report in financial_reports if report.report_date <= target_date and report.ann_date < target_date and report.end_type=="4" and report.financial_indicators and report.income_statement and report.cash_flow_statement],
            key=lambda x: x.report_date, 
            reverse=True
        )
        self.discount_rate = discount_rate
        self.risk_free_rate = risk_free_rate
        self.logger = get_logger()
        self.logger.info("初始化 StockTrader")

    def _check_roe_condition(self) -> bool:
        """检查ROE条件"""
        if len(self.financial_reports) < 5:
            return False
            
        # 获取最近5个年报
        annual_reports = [
            report for report in self.financial_reports
            if report.end_type == "4"
        ][:5]
        
        if len(annual_reports) < 5:
            return False
        
        # 打印每个年报的ROE
        self.logger.info(f"ROE: {[report.financial_indicators.roe for report in annual_reports]}")
            
        # 检查ROE是否都大于20%
        return all(
            report.financial_indicators.roe >= Decimal('20.0')
            for report in annual_reports
        )

    def _check_pe_percentile(self) -> float:
        """计算当前PE在历史分位数的位置"""
        if not self.daily_indicators:
            return 1.0
            
        # 获取最近5年的PE数据
        # five_years_ago = self.target_date.replace(year=self.target_date.year - 5)
        # TODO
        five_years_ago = self.target_date - timedelta(days=5*365)
        historical_pe = [
            ind.pe for ind in self.daily_indicators
            if ind.trade_date >= five_years_ago and ind.pe > 0
        ]
        
        if not historical_pe:
            return 1.0
        
        # 打印PE数据
        # self.logger.info(f"PE: {[ind.pe for ind in self.daily_indicators]}")

        current_pe = self.daily_indicators[0].pe
        pe_below_current = sum(1 for pe in historical_pe if pe <= current_pe)
        
        pe_percentile = pe_below_current / len(historical_pe)
        # print(f"target_date={self.target_date}, Current PE: {current_pe}, PE percentile: {pe_percentile}")
        
        return pe_percentile

    def _calculate_growth_rate(self, historical_fcff: List[float]) -> float:
        """计算历史现金流增长率
        
        Args:
            historical_fcff: 按时间倒序排列的历史现金流数据
            
        Returns:
            float: 计算得出的增长率，如果无法计算则返回0
        """
        growth_rates = []
        for i in range(len(historical_fcff)-1):
            if historical_fcff[i+1] > 0:  # 避免除以0
                rate = (historical_fcff[i] / historical_fcff[i+1]) - 1
                growth_rates.append(rate)
                
        if not growth_rates:
            return 0.0
        
        predicate_growth_rate = sum(growth_rates) / len(growth_rates)
        self.logger.info(f"Growth rates: {growth_rates}, Predicate growth rate: {predicate_growth_rate}")
            
        return predicate_growth_rate

    def _calculate_dcf_ratio(self) -> float:
        """计算DCF估值与当前市值的比率"""
        if not self.financial_reports or not self.daily_quotes:
            self.logger.info("No financial reports or daily quotes found, dcf_ratio=1.0")
            return 1.0
            
        # 获取最近的财务数据
        latest_report = self.financial_reports[0]
        latest_indicator = self.daily_indicators[0]
        
        if not latest_report.income_statement:
            self.logger.info("No income statement found, dcf_ratio=1.0")
            return 1.0
        
        income_item_name = '净利润(不含少数股东损益)'
        # 使用自由现金流进行估值
        if not latest_report.income_statement.get(income_item_name):
            self.logger.info(f"No income statement item {income_item_name} found, dcf_ratio=1.0")
            return 1.0

        # 获取历史现金流数据
        historical_fcff = []
        for report in self.financial_reports:
            fcff = report.calculate_fcff()
            historical_fcff.append(float(fcff if fcff else 0))
            if len(historical_fcff) >= 5:  # 只取最近5年数据
                break
                
        if len(historical_fcff) < 2:  # 至少需要2个数据点才能计算增长率
            self.logger.info("Not enough historical data, dcf_ratio=1.0")
            return 1.0
            
        # 打印historical_fcff
        self.logger.info(f"Historical FCFF: {historical_fcff}")
        
        # 计算增长率
        growth_rate = self._calculate_growth_rate(historical_fcff)
        
        fcff = float(latest_report.calculate_fcff())
        
        # 计算未来5年现金流现值
        kYearCount = 3
        present_value = 0
        for i in range(1, kYearCount):
            future_cf = fcff * (1 + growth_rate) ** i
            present_value += future_cf / (1 + self.discount_rate) ** i
        
        terminal_value_pv = fcff * (1 + growth_rate) ** kYearCount / self.risk_free_rate / (1 + self.discount_rate) ** kYearCount
        
        total_value = present_value + terminal_value_pv
        current_market_value = float(latest_indicator.total_mv * 10000) # 万元转为元
        ratio = current_market_value / total_value
        self.logger.info(f"fcff: {fcff:,.2f}, growth_rate: {growth_rate:.2%}, risk_free_rate={self.risk_free_rate:.2%}, discount_rate={self.discount_rate:.2%}, present_value: {present_value:,.2f}, terminal_value_pv: {terminal_value_pv:,.2f}, current_market_value={current_market_value:,.2f}, total_value: {total_value:,.2f}, ratio: {ratio:.2f}")
        return ratio

    def get_action(self) -> TradeAction:
        """获取交易决策"""
        # 计算各个指标
        roe_qualified = self._check_roe_condition()
        pe_percentile = self._check_pe_percentile()
        dcf_ratio = self._calculate_dcf_ratio()
        
        # 打印指标
        self.logger.info(f"ROE条件: {roe_qualified}")
        self.logger.info(f"PE分位数: {pe_percentile}")
        self.logger.info(f"市值 / DCF估值: {dcf_ratio}")
        
        # 买入条件
        if (roe_qualified and 
            # pe_percentile <= 0.15 and
            dcf_ratio <= 0.5):
            self.logger.info(f"日期：{self.target_date}, 买入")
            return TradeAction.BUY
            
        # 卖出条件
        if (not roe_qualified
            # pe_percentile >= 0.85
            or dcf_ratio >= 1.3):  # dcf_ratio <= 0.8 相当于 1/dcf_ratio >= 1.2
            self.logger.info(f"日期：{self.target_date}, 卖出")
            return TradeAction.SELL
            
        # 其他情况持有
        self.logger.info(f"日期：{self.target_date}, 观望")
        return TradeAction.HOLD