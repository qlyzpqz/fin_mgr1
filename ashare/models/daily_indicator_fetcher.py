from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
import tushare as ts
import pandas as pd
import math
from .daily_indicator import DailyIndicator

class DailyIndicatorFetcher:
    def __init__(self, api_token: str):
        self.api = ts.pro_api(api_token)

    def _convert_date(self, date_obj: date) -> str:
        """将date对象转换为tushare所需的日期字符串格式"""
        return date_obj.strftime('%Y%m%d')

    def _convert_decimal(self, value) -> Optional[Decimal]:
        """
        将数值转换为Decimal类型
        
        Args:
            value: 要转换的值
            
        Returns:
            转换后的Decimal值，如果输入为None或NaN则返回None
        """
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        return Decimal(str(value))

    def fetch_daily_indicators(self, ts_code: str, 
                             start_date: date, 
                             end_date: date) -> List[DailyIndicator]:
        """
        获取指定股票在给定日期范围内的每日指标数据
        
        Args:
            ts_code: 股票代码，如：'000001.SZ'
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[DailyIndicator]: 每日指标数据列表
        """
        # 转换日期格式
        start_date_str = self._convert_date(start_date)
        end_date_str = self._convert_date(end_date)
        
        # 调用tushare API获取数据
        df = self.api.daily_basic(
            ts_code=ts_code,
            start_date=start_date_str,
            end_date=end_date_str,
            fields='ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,'
                  'pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,'
                  'free_share,total_mv,circ_mv'
        )
        
        # 转换为DailyIndicator对象列表
        indicators = []
        for _, row in df.iterrows():
            indicator = DailyIndicator(
                ts_code=row['ts_code'],
                trade_date=datetime.strptime(str(row['trade_date']), '%Y%m%d').date(),
                close=self._convert_decimal(row['close']),
                turnover_rate=self._convert_decimal(row['turnover_rate']),
                turnover_rate_f=self._convert_decimal(row['turnover_rate_f']),
                volume_ratio=self._convert_decimal(row['volume_ratio']),
                pe=self._convert_decimal(row['pe']),
                pe_ttm=self._convert_decimal(row['pe_ttm']),
                pb=self._convert_decimal(row['pb']),
                ps=self._convert_decimal(row['ps']),
                ps_ttm=self._convert_decimal(row['ps_ttm']),
                dv_ratio=self._convert_decimal(row['dv_ratio']),
                dv_ttm=self._convert_decimal(row['dv_ttm']),
                total_share=self._convert_decimal(row['total_share']),
                float_share=self._convert_decimal(row['float_share']),
                free_share=self._convert_decimal(row['free_share']),
                total_mv=self._convert_decimal(row['total_mv']),
                circ_mv=self._convert_decimal(row['circ_mv'])
            )
            indicators.append(indicator)
            
        return indicators