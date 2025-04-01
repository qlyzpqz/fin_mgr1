from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class TradeRecord:
    """股票交易记录"""
    ts_code: str           # TS代码
    trade_date: date       # 交易日期
    trade_price: Decimal   # 交易价格
    trade_shares: Decimal  # 交易数量
    trade_type: str        # 交易类型：buy-买入, sell-卖出
    trade_amount: Decimal  # 交易金额
    commission: Decimal    # 手续费
    tax: Decimal          # 印花税和其他税费