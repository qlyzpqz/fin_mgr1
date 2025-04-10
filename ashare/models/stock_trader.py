from typing import List
from decimal import Decimal
from enum import Enum
from datetime import date
from .financial_report import FinancialReport
from .daily_indicator import DailyIndicator
from .daily_quote import DailyQuote
from .dividend import Dividend

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
                 discount_rate: float = 0.1,  # 折现率默认10%
                 risk_free_rate: float = 0.03):  # 无风险收益率默认3%
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
            [div for div in dividends if div.ann_date <= target_date],
            key=lambda x: x.ann_date, 
            reverse=True
        )
        self.financial_reports = sorted(
            [report for report in financial_reports if report.report_date <= target_date and report.end_type=="4" ],
            key=lambda x: x.report_date, 
            reverse=True
        )
        self.discount_rate = discount_rate
        self.risk_free_rate = risk_free_rate

    def _check_roe_condition(self) -> bool:
        """检查ROE条件"""
        if len(self.financial_reports) < 5:
            return False
            
        # 获取最近5个年报
        annual_reports = [
            report for report in self.financial_reports
            if report.end_type == "4"  # 年报
        ][:5]
        
        if len(annual_reports) < 5:
            return False
            
        # 检查ROE是否都大于15%
        return all(
            report.financial_indicators.roe >= Decimal('15.0')
            for report in annual_reports
        )

    def _check_pe_percentile(self) -> float:
        """计算当前PE在历史分位数的位置"""
        if not self.daily_indicators:
            return 1.0
            
        # 获取最近5年的PE数据
        five_years_ago = date.today().replace(year=date.today().year - 5)
        historical_pe = [
            ind.pe for ind in self.daily_indicators
            if ind.trade_date >= five_years_ago and ind.pe > 0
        ]
        
        if not historical_pe:
            return 1.0
            
        current_pe = self.daily_indicators[0].pe
        pe_below_current = sum(1 for pe in historical_pe if pe <= current_pe)
        
        return pe_below_current / len(historical_pe)

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
            
        return sum(growth_rates) / len(growth_rates)

    def _calculate_dcf_ratio(self) -> float:
        """计算DCF估值与当前市值的比率"""
        if not self.financial_reports or not self.daily_quotes:
            return 1.0
            
        # 获取最近的财务数据
        latest_report = self.financial_reports[0]
        latest_indicator = self.daily_indicators[0]
        
        # 使用自由现金流进行估值
        if not latest_report.financial_indicators.fcff:
            return 1.0

        # 获取历史现金流数据
        historical_fcff = []
        for report in self.financial_reports:
            if report.financial_indicators.fcff:
                historical_fcff.append(float(report.financial_indicators.fcff))
            if len(historical_fcff) >= 5:  # 只取最近5年数据
                break
                
        if len(historical_fcff) < 2:  # 至少需要2个数据点才能计算增长率
            return 1.0
            
        # 计算增长率
        growth_rate = self._calculate_growth_rate(historical_fcff)
        
        fcff = float(latest_report.financial_indicators.fcff)
        
        # 计算未来5年现金流现值
        present_value = 0
        for i in range(1, 6):
            future_cf = fcff * (1 + growth_rate) ** i
            present_value += future_cf / (1 + self.discount_rate) ** i
            
        # 永续增长价值（假设永续增长率为3%）
        # terminal_value = (fcff * (1 + growth_rate) ** 5 * (1 + 0.03)) / (self.discount_rate - 0.03)
        # terminal_value_pv = terminal_value / (1 + self.discount_rate) ** 5
        terminal_value_pv = fcff * (1 + growth_rate) ** 5 / self.risk_free_rate / (1 + self.discount_rate) ** 5
        
        total_value = present_value + terminal_value_pv
        current_market_value = float(latest_indicator.total_mv)
        
        print(f"fcff: {fcff}, growth_rate: {growth_rate}, risk_free_rate={self.risk_free_rate}, discount_rate={self.discount_rate}, present_value: {present_value}, terminal_value_pv: {terminal_value_pv}, total_value: {total_value}")
        return current_market_value / total_value

    def get_action(self) -> TradeAction:
        """获取交易决策"""
        # 计算各个指标
        roe_qualified = self._check_roe_condition()
        pe_percentile = self._check_pe_percentile()
        dcf_ratio = self._calculate_dcf_ratio()
        
        # 打印指标
        print(f"ROE条件: {roe_qualified}")
        print(f"PE分位数: {pe_percentile}")
        print(f"市值比 / DCF估值: {dcf_ratio}")
        
        # 买入条件
        if (roe_qualified and 
            pe_percentile <= 0.15 and 
            dcf_ratio <= 0.6):
            return TradeAction.BUY
            
        # 卖出条件
        if (not roe_qualified or 
            pe_percentile >= 0.85 or 
            dcf_ratio >= 1.2):  # dcf_ratio <= 0.8 相当于 1/dcf_ratio >= 1.2
            return TradeAction.SELL
            
        # 其他情况持有
        return TradeAction.HOLD