from typing import List, Optional
import pandas as pd
from ashare.models.stock import Stock  # 修改这行，去掉多余的 .ashare
from datetime import datetime, date
import tushare as ts
import logging

from ashare.models.tushare_api import TushareAPI

class AShareFetcher():
    def __init__(self, api_token: str):
        self.api = TushareAPI(api_token)
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化 AShareFetcher")

    def _convert_date(self, date_str: str) -> Optional[date]:
        """转换日期字符串为date对象"""
        if not date_str:
            return None
        return datetime.strptime(str(date_str), '%Y%m%d').date()

    def fetch_stock_list(self) -> List[Stock]:
        df = self.api.stock_basic(exchange='', list_status='L', 
                                fields='ts_code,symbol,name,area,industry,fullname,enname,cnspell,market,exchange,curr_type,list_status,list_date,delist_date,is_hs,act_name,act_ent_type')
        self.logger.info(f"获取到 {len(df)} 只股票")
        return [
            Stock(
                ts_code=row['ts_code'],
                symbol=row['symbol'],
                name=row['name'],
                area=row['area'],
                industry=row['industry'],
                fullname=row['fullname'],
                enname=row['enname'],
                cnspell=row['cnspell'],
                market=row['market'],
                exchange=row['exchange'],
                curr_type=row['curr_type'],
                list_status=row['list_status'],
                list_date=self._convert_date(row['list_date']),
                delist_date=self._convert_date(row['delist_date']),
                is_hs=row['is_hs'],
                act_name=row['act_name'],
                act_ent_type=row['act_ent_type'],
            )
            for _, row in df.iterrows()
        ]