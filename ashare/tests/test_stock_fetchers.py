import os
import pytest
from datetime import date
from ashare.models.stock_fetchers import AShareFetcher
from ashare.models.stock import Stock

class TestAShareFetcher:
    @pytest.fixture
    def fetcher(self):
        api_token = os.getenv('TUSHARE_TOKEN')
        print("api_toke=", api_token)
        if not api_token:
            pytest.skip('需要设置 TUSHARE_TOKEN 环境变量')
        return AShareFetcher(api_token)

    def test_convert_date(self, fetcher):
        assert fetcher._convert_date('20230101') == date(2023, 1, 1)
        assert fetcher._convert_date(None) is None
        assert fetcher._convert_date('') is None

    def test_fetch_stock_list(self, fetcher):
        stocks = fetcher.fetch_stock_list()
        
        assert isinstance(stocks, list)
        assert len(stocks) > 0
        
        first_stock = stocks[0]
        print(first_stock)
        assert isinstance(first_stock, Stock)
        assert isinstance(first_stock.ts_code, str)
        assert isinstance(first_stock.symbol, str)
        assert isinstance(first_stock.name, str)
        
        if first_stock.list_date:
            assert isinstance(first_stock.list_date, date)
        if first_stock.delist_date:
            assert isinstance(first_stock.delist_date, date)

        assert first_stock.ts_code
        assert first_stock.symbol
        assert first_stock.name