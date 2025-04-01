import os
import pytest
from datetime import date
from decimal import Decimal
from ashare.models.daily_indicator_fetcher import DailyIndicatorFetcher
from ashare.models.daily_indicator import DailyIndicator

class TestDailyIndicatorFetcher:
    @pytest.fixture
    def fetcher(self):
        api_token = os.getenv('TUSHARE_TOKEN')
        if not api_token:
            pytest.skip('需要设置 TUSHARE_TOKEN 环境变量')
        return DailyIndicatorFetcher(api_token)

    def test_convert_date(self, fetcher):
        """测试日期转换方法"""
        test_date = date(2023, 1, 1)
        assert fetcher._convert_date(test_date) == '20230101'

    def test_convert_decimal(self, fetcher):
        """测试数值转换为Decimal方法"""
        assert fetcher._convert_decimal(10.5) == Decimal('10.5')
        assert fetcher._convert_decimal(None) == Decimal('0')
        assert fetcher._convert_decimal(float('nan')) == Decimal('0')

    def test_fetch_daily_indicators(self, fetcher):
        """测试获取每日指标数据"""
        # 获取平安银行（000001.SZ）2023年第一个交易周的数据
        indicators = fetcher.fetch_daily_indicators(
            ts_code='000001.SZ',
            start_date=date(2023, 1, 3),
            end_date=date(2023, 1, 6)
        )

        # 基本检查
        assert isinstance(indicators, list)
        assert len(indicators) > 0

        # 检查第一条数据
        first_indicator = indicators[0]
        assert isinstance(first_indicator, DailyIndicator)
        
        # 检查数据类型
        assert isinstance(first_indicator.ts_code, str)
        assert isinstance(first_indicator.trade_date, date)
        assert isinstance(first_indicator.close, Decimal)
        assert isinstance(first_indicator.turnover_rate, Decimal)
        assert isinstance(first_indicator.pe, Decimal)
        assert isinstance(first_indicator.pb, Decimal)
        assert isinstance(first_indicator.total_mv, Decimal)
        assert isinstance(first_indicator.circ_mv, Decimal)

        # 检查数据有效性
        assert first_indicator.ts_code == '000001.SZ'
        assert first_indicator.close > Decimal('0')
        assert first_indicator.turnover_rate >= Decimal('0')
        assert first_indicator.total_share > Decimal('0')
        assert first_indicator.float_share > Decimal('0')
        assert first_indicator.total_mv >= first_indicator.circ_mv

        # 检查数据连续性
        trade_dates = [ind.trade_date for ind in indicators]
        assert len(trade_dates) == len(set(trade_dates))  # 确保没有重复日期
        assert trade_dates == sorted(trade_dates, reverse=True)  # 确保日期是降序的