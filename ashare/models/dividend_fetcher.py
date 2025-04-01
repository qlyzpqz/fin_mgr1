from typing import List
from datetime import datetime
from decimal import Decimal
import tushare as ts
import pandas as pd
from .dividend import Dividend

class DividendFetcher:
    def __init__(self, api_token: str):
        self.api = ts.pro_api(api_token)

    def _convert_date(self, date_str: str) -> datetime.date:
        """转换日期字符串为date对象"""
        if not date_str or pd.isna(date_str):
            return None
        return datetime.strptime(str(date_str), '%Y%m%d').date()

    def _convert_decimal(self, value) -> Decimal:
        """将数值转换为Decimal类型"""
        return Decimal(str(value)) if pd.notna(value) else Decimal('0')

    def fetch_dividends(self, ts_code: str) -> List[Dividend]:
        """
        获取指定股票的所有分红送股数据
        
        Args:
            ts_code: 股票代码，如：'000001.SZ'
            
        Returns:
            List[Dividend]: 分红送股数据列表
        """
        # 调用tushare API获取数据
        df = self.api.dividend(
            ts_code=ts_code,
            fields='ts_code,end_date,ann_date,div_proc,stk_div,stk_bo_rate,stk_co_rate,'
                  'cash_div,cash_div_tax,record_date,ex_date,pay_date,div_listdate,'
                  'imp_ann_date,base_date,base_share'
        )
        
        # 转换为Dividend对象列表
        dividends = []
        for _, row in df.iterrows():
            dividend = Dividend(
                ts_code=row['ts_code'],
                end_date=self._convert_date(row['end_date']),
                ann_date=self._convert_date(row['ann_date']),
                div_proc=row['div_proc'],
                stk_div=self._convert_decimal(row['stk_div']),
                stk_bo_rate=self._convert_decimal(row['stk_bo_rate']),
                stk_co_rate=self._convert_decimal(row['stk_co_rate']),
                cash_div=self._convert_decimal(row['cash_div']),
                cash_div_tax=self._convert_decimal(row['cash_div_tax']),
                record_date=self._convert_date(row['record_date']),
                ex_date=self._convert_date(row['ex_date']),
                pay_date=self._convert_date(row['pay_date']),
                div_listdate=self._convert_date(row['div_listdate']),
                imp_ann_date=self._convert_date(row['imp_ann_date']),
                base_date=self._convert_date(row['base_date']),
                base_share=self._convert_decimal(row['base_share'])
            )
            dividends.append(dividend)
            
        return dividends