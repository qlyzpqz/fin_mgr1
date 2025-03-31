from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class DailyQuote:
    """A股日行情数据"""
    ts_code: str                # TS代码
    trade_date: date           # 交易日期
    open: Decimal             # 开盘价
    high: Decimal             # 最高价
    low: Decimal              # 最低价
    close: Decimal            # 收盘价
    pre_close: Decimal        # 昨收价
    change: Decimal           # 涨跌额
    pct_chg: Decimal         # 涨跌幅 (%)
    vol: Decimal              # 成交量 (手)
    amount: Decimal           # 成交额 (千元)