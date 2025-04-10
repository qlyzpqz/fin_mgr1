from enum import Enum
from datetime import timedelta

class SyncType(Enum):
    STOCK_LIST = ("stock_list", timedelta(days=7))         # 股票列表每周更新
    DAILY_INDICATOR = ("daily_indicator", timedelta(days=1)) # 每日指标每天更新
    DAILY_QUOTE = ("daily_quote", timedelta(days=1))       # 每日行情每天更新
    DIVIDEND = ("dividend", timedelta(days=1))             # 分红记录每周更新
    FINANCIAL_REPORT = ("financial_report", timedelta(days=7))  # 财报数据每季度更新
    
    def __init__(self, value: str, interval: timedelta):
        self._value_ = value
        self.interval = interval