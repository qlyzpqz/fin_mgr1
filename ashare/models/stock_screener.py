from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from ashare.models.daily_indicator import DailyIndicator
from ashare.models.daily_quote import DailyQuote
from ashare.models.dividend import Dividend
from ashare.models.financial_report import FinancialReport

class BaseStockScreener(ABC):
    """股票筛选基类"""
    
    def __init__(self, 
                 daily_indicators: List[DailyIndicator],
                 daily_quotes: List[DailyQuote],
                 dividends: List[Dividend],
                 financial_reports: List[FinancialReport]):
        self.daily_indicators = daily_indicators
        self.daily_quotes = daily_quotes
        self.dividends = dividends
        self.financial_reports = financial_reports

    @abstractmethod
    def validate(self) -> bool:
        """
        验证股票是否符合筛选条件
        
        Returns:
            bool: 是否符合筛选条件
        """
        pass