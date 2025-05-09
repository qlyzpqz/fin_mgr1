from typing import Dict, Type

from pandas.io.sql import re
from tushare import stock
from .sync_type import SyncType
from .sync_task_repository import SyncTaskRepository
from .stock_fetchers import AShareFetcher
from .daily_quote_fetcher import DailyQuoteFetcher
from .dividend_fetcher import DividendFetcher
from .financial_report_fetcher import FinancialReportFetcher
from .stock_repository import StockRepository
from .daily_indicator_fetcher import DailyIndicatorFetcher
from .daily_indicator_repository import DailyIndicatorRepository
from datetime import date, timedelta
from .daily_quote_repository import DailyQuoteRepository
from .dividend_repository import DividendRepository
from .financial_report_repository import FinancialReportRepository
import logging

class BaseSync:
    def __init__(self, db_path: str, tushare_token: str):
        self.db_path = db_path
        self.tushare_token = tushare_token
        self.logger = logging.getLogger(__name__)
        
    def _filter_stocks(self, stock_list: list, ts_codes: list[str] = None) -> list:
        """过滤股票列表
        
        Args:
            stock_list: 原始股票列表
            ts_codes: 需要保留的股票代码列表
            
        Returns:
            过滤后的股票列表
        """
        if not ts_codes:
            return stock_list
        return [stock for stock in stock_list if stock.ts_code in ts_codes]
    
    def fetch_and_save(self, ts_codes: list[str] = None):
        """获取数据并保存"""
        raise NotImplementedError

class StockListSync(BaseSync):
    def fetch_and_save(self, ts_codes: list[str] = None):
        """获取股票列表数据并保存"""
        self.logger.info("获取股票列表数据并保存")
        fetcher = AShareFetcher(self.tushare_token)
        stock_list = fetcher.fetch_stock_list()
        filtered_stock_list = self._filter_stocks(stock_list, ts_codes)
        repository = StockRepository(self.db_path)
        repository.save_many(filtered_stock_list)

class DailyQuoteSync(BaseSync):
    def fetch_and_save(self, ts_codes: list[str] = None):
        """获取每日行情数据并保存"""
        self.logger.info("获取每日行情数据并保存")
        stock_repo = StockRepository(self.db_path)
        stock_list = stock_repo.find_all()
        filtered_stock_list = self._filter_stocks(stock_list, ts_codes)
        fetcher = DailyQuoteFetcher(self.tushare_token)
        yesterday = date.today() - timedelta(days=1)
        for stock in filtered_stock_list:
            daily_quotes = fetcher.fetch_daily_quotes(stock.ts_code, stock.list_date, yesterday)
            repository = DailyQuoteRepository(self.db_path)
            repository.save_many(daily_quotes)

class DailyIndicatorSync(BaseSync):
    def fetch_and_save(self, ts_codes: list[str] = None):
        """获取每日指标数据并保存"""
        self.logger.info("获取每日指标数据并保存")
        stock_repo = StockRepository(self.db_path)
        stock_list = stock_repo.find_all()
        filtered_stock_list = self._filter_stocks(stock_list, ts_codes)
        fetcher = DailyIndicatorFetcher(self.tushare_token)
        yesterday = date.today() - timedelta(days=1)
        for stock in filtered_stock_list:
            daily_indicators = fetcher.fetch_daily_indicators(stock.ts_code, stock.list_date, yesterday)
            repository = DailyIndicatorRepository(self.db_path)
            repository.save_many(daily_indicators)

class DividendSync(BaseSync):
    def fetch_and_save(self, ts_codes: list[str] = None):
        """获取分红数据并保存"""
        self.logger.info("获取分红数据并保存")
        stock_repo = StockRepository(self.db_path)
        stock_list = stock_repo.find_all()
        filtered_stock_list = self._filter_stocks(stock_list, ts_codes)
        fetcher = DividendFetcher(self.tushare_token)
        yesterday = date.today() - timedelta(days=1)
        for stock in filtered_stock_list:
            dividends = fetcher.fetch_dividends(stock.ts_code)
            repository = DividendRepository(self.db_path)
            repository.save_many(dividends)

class FinancialReportSync(BaseSync):        
    def fetch_and_save(self, ts_codes: list[str] = None):
        """获取财报数据并保存"""
        self.logger.info("获取财报数据并保存")
        stock_repo = StockRepository(self.db_path)
        stock_list = stock_repo.find_all()
        filtered_stock_list = self._filter_stocks(stock_list, ts_codes)
        fetcher = FinancialReportFetcher(self.tushare_token)
        yesterday = date.today() - timedelta(days=1)
        for stock in filtered_stock_list:
            reports = fetcher.fetch_financial_reports(stock.ts_code, stock.list_date, yesterday)
            self.logger.info(f"获取财报数据并保存 {stock.ts_code}: reports\n: {repr(reports)}")
            repository = FinancialReportRepository(self.db_path)
            repository.save_many(reports)

class SyncService:
    def __init__(self, db_path: str, tushare_token: str, ts_codes: list[str] = None):
        self.sync_task_repo = SyncTaskRepository(db_path)
        self.ts_codes = ts_codes
        self._fetcher_map = {
            SyncType.STOCK_LIST: StockListSync(db_path, tushare_token),
            SyncType.DAILY_INDICATOR: DailyIndicatorSync(db_path, tushare_token),
            SyncType.DAILY_QUOTE: DailyQuoteSync(db_path, tushare_token),
            SyncType.DIVIDEND: DividendSync(db_path, tushare_token),  # 更新这行
            SyncType.FINANCIAL_REPORT: FinancialReportSync(db_path, tushare_token)  # 更新这行
        }
    
    def sync(self, sync_type: SyncType):
        """执行指定类型的同步任务"""
        task = self.sync_task_repo.get_task(sync_type)
        
        if not task or task.need_sync():
            fetcher = self._fetcher_map.get(sync_type)
            if not fetcher:
                raise ValueError(f"未找到{sync_type.value}对应的数据获取器")
                
            # 执行数据同步
            fetcher.fetch_and_save(self.ts_codes)
            
            # 更新同步时间
            self.sync_task_repo.update_sync_time(sync_type)
    
    def sync_all(self):
        """执行所有同步任务"""
        for sync_type in SyncType:
            self.sync(sync_type)
        # self.sync(SyncType.FINANCIAL_REPORT)