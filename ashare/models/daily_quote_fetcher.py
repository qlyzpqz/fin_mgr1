from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
import tushare as ts
import pandas as pd
from .daily_quote import DailyQuote

class DailyQuoteFetcher:
    def __init__(self, api_token: str):
        self.api = ts.pro_api(api_token)

    def _convert_date(self, date_obj: date) -> str:
        """将date对象转换为tushare所需的日期字符串格式"""
        return date_obj.strftime('%Y%m%d')

    def _convert_decimal(self, value) -> Decimal:
        """将数值转换为Decimal类型"""
        return Decimal(str(value)) if pd.notna(value) else Decimal('0')

    def fetch_daily_quotes(self, ts_codes: str, 
                          start_date: date, 
                          end_date: date) -> List[DailyQuote]:
        """
        获取指定股票在给定日期范围内的日行情数据
        
        Args:
            ts_codes: 单个股票代码 如：'000001.SZ'
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[DailyQuote]: 日行情数据列表
        """ 
        # 转换日期格式
        start_date_str = self._convert_date(start_date)
        end_date_str = self._convert_date(end_date)
        
        # 调用tushare API获取数据
        df = self.api.daily(
            ts_code=ts_codes,
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        # 转换为DailyQuote对象列表
        quotes = []
        for _, row in df.iterrows():
            quote = DailyQuote(
                ts_code=row['ts_code'],
                trade_date=datetime.strptime(str(row['trade_date']), '%Y%m%d').date(),
                open=self._convert_decimal(row['open']),
                high=self._convert_decimal(row['high']),
                low=self._convert_decimal(row['low']),
                close=self._convert_decimal(row['close']),
                pre_close=self._convert_decimal(row['pre_close']),
                change=self._convert_decimal(row['change']),
                pct_chg=self._convert_decimal(row['pct_chg']),
                vol=self._convert_decimal(row['vol']),
                amount=self._convert_decimal(row['amount'])
            )
            quotes.append(quote)
            
        return quotes