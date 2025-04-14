import os
import pytest
from datetime import date
from decimal import Decimal
from ashare.models.daily_quote_fetcher import DailyQuoteFetcher
from ashare.models.daily_quote import DailyQuote

class TestDailyQuoteFetcher:
    @pytest.fixture
    def fetcher(self):
        api_token = os.getenv('TUSHARE_TOKEN')
        if not api_token:
            pytest.skip('需要设置 TUSHARE_TOKEN 环境变量')
        return DailyQuoteFetcher(api_token)

    def test_convert_date(self, fetcher):
        """测试日期转换方法"""
        test_date = date(2023, 1, 1)
        assert fetcher._convert_date(test_date) == '20230101'

    def test_convert_decimal(self, fetcher):
        """测试数值转换为Decimal方法"""
        # 测试正常数值转换
        assert fetcher._convert_decimal(10.5) == Decimal('10.5')
        
        # 测试空值转换
        assert fetcher._convert_decimal(None) is None
        
        # 测试NaN值转换
        assert fetcher._convert_decimal(float('nan')) is None

    def test_fetch_daily_quotes(self, fetcher):
        """测试获取日行情数据"""
        # 获取平安银行（000001.SZ）2023年第一个交易周的数据
        quotes = fetcher.fetch_daily_quotes(
            ts_codes='000001.SZ',
            start_date=date(2023, 1, 3),  # 2023年1月3日是那周的第一个交易日
            end_date=date(2023, 1, 6)
        )

        # 基本检查
        assert isinstance(quotes, list)
        assert len(quotes) > 0

        # 检查第一条数据
        first_quote = quotes[0]
        assert isinstance(first_quote, DailyQuote)
        
        # 检查数据类型
        assert isinstance(first_quote.ts_code, str)
        assert isinstance(first_quote.trade_date, date)
        assert isinstance(first_quote.open, Decimal)
        assert isinstance(first_quote.high, Decimal)
        assert isinstance(first_quote.low, Decimal)
        assert isinstance(first_quote.close, Decimal)
        assert isinstance(first_quote.pre_close, Decimal)
        assert isinstance(first_quote.change, Decimal)
        assert isinstance(first_quote.pct_chg, Decimal)
        assert isinstance(first_quote.vol, Decimal)
        assert isinstance(first_quote.amount, Decimal)

        # 检查数据有效性
        assert first_quote.ts_code == '000001.SZ'
        assert first_quote.open > Decimal('0')
        assert first_quote.high >= first_quote.low
        assert first_quote.vol >= Decimal('0')
        assert first_quote.amount >= Decimal('0')

        # 检查数据连续性
        trade_dates = [q.trade_date for q in quotes]
        assert len(trade_dates) == len(set(trade_dates))  # 确保没有重复日期
        assert trade_dates == sorted(trade_dates, reverse=True)  # 确保日期是降序的