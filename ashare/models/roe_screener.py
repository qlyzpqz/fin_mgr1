from typing import List
from ashare.models.stock_screener import BaseStockScreener
from ashare.models.daily_indicator import DailyIndicator
from ashare.models.daily_quote import DailyQuote
from ashare.models.dividend import Dividend
from ashare.models.financial_report import FinancialReport

class ROEScreener(BaseStockScreener):
    """净资产收益率(ROE)筛选器"""
    
    def __init__(self, 
                 daily_indicators: List[DailyIndicator],
                 daily_quotes: List[DailyQuote],
                 dividends: List[Dividend],
                 financial_reports: List[FinancialReport],
                 min_roe: float = 15.0):
        super().__init__(daily_indicators, daily_quotes, dividends, financial_reports)
        self.min_roe = min_roe

    def validate(self) -> bool:
        """
        验证股票是否满足连续5年ROE大于指定值的条件
        
        Returns:
            bool: 是否满足条件
        """
        if len(self.financial_reports) < 5:
            return False
            
        # 按年份排序财务报告
        sorted_reports = sorted(
            self.financial_reports,
            key=lambda x: x.end_date,
            reverse=True
        )
        
        # 获取最近5个年报的ROE
        annual_reports = [
            report for report in sorted_reports
            if report.report_type == 1  # 假设1表示年报
        ][:5]
        
        # 检查是否有足够的年报数据
        if len(annual_reports) < 5:
            return False
            
        # 检查连续5年的ROE是否都大于指定值
        return all(
            report.roe >= self.min_roe
            for report in annual_reports
        )