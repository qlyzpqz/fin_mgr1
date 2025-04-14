import os
import pytest
from datetime import date
from decimal import Decimal
from ashare.models.dividend_fetcher import DividendFetcher
from ashare.models.dividend import Dividend

class TestDividendFetcher:
    @pytest.fixture
    def fetcher(self):
        api_token = os.getenv('TUSHARE_TOKEN')
        if not api_token:
            pytest.skip('需要设置 TUSHARE_TOKEN 环境变量')
        return DividendFetcher(api_token)

    def test_convert_date(self, fetcher):
        """测试日期转换方法"""
        assert fetcher._convert_date('20230101') == date(2023, 1, 1)
        assert fetcher._convert_date(None) is None
        assert fetcher._convert_date('') is None

    def test_convert_decimal(self, fetcher):
        """测试数值转换方法"""
        assert fetcher._convert_decimal(10.5) == Decimal('10.5')
        assert fetcher._convert_decimal(None) == None
        assert fetcher._convert_decimal(float('nan')) == None

    def test_fetch_dividends(self, fetcher):
        """测试获取分红送股数据"""
        # 获取平安银行的分红数据
        dividends = fetcher.fetch_dividends('000001.SZ')

        print(dividends)

        # 基本检查
        assert isinstance(dividends, list)
        assert len(dividends) > 0

        # 检查第一条数据
        first_dividend = dividends[0]
        assert isinstance(first_dividend, Dividend)

        # 检查数据类型
        assert isinstance(first_dividend.ts_code, str)
        assert isinstance(first_dividend.cash_div, Decimal) or first_dividend.cash_div is None
        assert isinstance(first_dividend.stk_bo_rate, Decimal) or first_dividend.stk_bo_rate is None
        assert isinstance(first_dividend.stk_co_rate, Decimal) or first_dividend.stk_co_rate is None
        assert isinstance(first_dividend.base_share, Decimal) or first_dividend.base_share is None

        # 检查数据有效性
        assert first_dividend.ts_code == '000001.SZ'
        assert first_dividend.cash_div >= Decimal('0')
        assert first_dividend.stk_bo_rate is None or first_dividend.stk_bo_rate >= Decimal('0')
        assert first_dividend.stk_co_rate is None or first_dividend.stk_co_rate >= Decimal('0')
        
        # 检查日期字段
        if first_dividend.ex_date:
            assert isinstance(first_dividend.ex_date, date)
        if first_dividend.pay_date:
            assert isinstance(first_dividend.pay_date, date)

        # 检查分红进度
        assert first_dividend.div_proc in ['预案', '实施', '不分配', '报废']

        # 检查数据排序（按公告日期降序）
        ann_dates = [d.ann_date for d in dividends if d.ann_date]
        if len(ann_dates) > 1:
            assert ann_dates == sorted(ann_dates, reverse=True)