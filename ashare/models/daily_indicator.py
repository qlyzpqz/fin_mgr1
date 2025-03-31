from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class DailyIndicator:
    """A股每日指标数据"""
    ts_code: str                # TS代码
    trade_date: date           # 交易日期
    close: Decimal             # 收盘价
    turnover_rate: Decimal     # 换手率
    turnover_rate_f: Decimal   # 换手率（自由流通股）
    volume_ratio: Decimal      # 量比
    pe: Decimal               # 市盈率
    pe_ttm: Decimal          # 市盈率TTM
    pb: Decimal              # 市净率
    ps: Decimal              # 市销率
    ps_ttm: Decimal         # 市销率TTM
    dv_ratio: Decimal       # 股息率
    dv_ttm: Decimal        # 股息率TTM
    total_share: Decimal    # 总股本
    float_share: Decimal    # 流通股本
    free_share: Decimal    # 自由流通股本
    total_mv: Decimal      # 总市值
    circ_mv: Decimal       # 流通市值