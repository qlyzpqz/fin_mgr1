from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class Dividend:
    """A股分红送股数据"""
    ts_code: str                # TS代码
    end_date: date             # 分红年度截止日
    ann_date: date             # 公告日期
    div_proc: str              # 实施进度
    stk_div: Decimal           # 每股送转
    stk_bo_rate: Decimal       # 每股送股比例
    stk_co_rate: Decimal       # 每股转增比例
    cash_div: Decimal          # 每股分红（税后）
    cash_div_tax: Decimal      # 每股分红（税前）
    record_date: date          # 股权登记日
    ex_date: date              # 除权除息日
    pay_date: date             # 派息日
    div_listdate: date         # 红股上市日
    imp_ann_date: date         # 实施公告日
    base_date: date            # 基准日
    base_share: Decimal        # 基准股本（万）