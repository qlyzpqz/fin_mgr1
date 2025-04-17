from datetime import date, timedelta
from decimal import Decimal
import pytest
from ashare.models.stock_trader import StockTrader, TradeAction
from ashare.models.daily_indicator import DailyIndicator
from ashare.models.daily_quote import DailyQuote
from ashare.models.dividend import Dividend
from ashare.models.financial_report import FinancialReport, FinancialIndicators
from ashare.models.sync_service import SyncService
from ashare.models.stock_repository import StockRepository
from ashare.models.daily_indicator_repository import DailyIndicatorRepository
from ashare.models.daily_quote_repository import DailyQuoteRepository
from ashare.models.dividend_repository import DividendRepository
from ashare.models.financial_report_repository import FinancialReportRepository
import os
import logging
from datetime import datetime

@pytest.fixture
def base_date():
    return date(2025, 4, 20)

@pytest.fixture
def db_path():
    return './test_stock_trader.db'

@pytest.fixture
def sync_data(db_path, base_date):
    """同步茅台数据"""
    # 创建同步服务实例
    sync_svc = SyncService(db_path, os.getenv('TUSHARE_TOKEN'), ["600519.SH"])
    
    # 执行同步
    sync_svc.sync_all()
    
    # 从数据库读取同步的数据
    stock_repo = StockRepository(db_path)
    daily_indicator_repo = DailyIndicatorRepository(db_path)
    daily_quote_repo = DailyQuoteRepository(db_path)
    dividend_repo = DividendRepository(db_path)
    financial_report_repo = FinancialReportRepository(db_path)
    
    # 获取茅台的所有数据
    stock = stock_repo.find_by_ts_code("600519.SH")
    daily_indicators = daily_indicator_repo.find_by_code("600519.SH")
    daily_quotes = daily_quote_repo.find_by_code("600519.SH")
    dividends = dividend_repo.find_by_code("600519.SH")
    financial_reports = financial_report_repo.get_all("600519.SH")
    
    return {
        'daily_indicators': daily_indicators,
        'daily_quotes': daily_quotes,
        'dividends': dividends,
        'financial_reports': financial_reports
    }

@pytest.fixture
def stock_trader(sync_data, base_date):
    """使用实际数据创建股票交易对象"""
    return StockTrader(
        daily_indicators=sync_data['daily_indicators'],
        daily_quotes=sync_data['daily_quotes'],
        dividends=sync_data['dividends'],
        financial_reports=sync_data['financial_reports'],
        target_date=base_date
    )

def test_initialization(stock_trader, base_date):
    """测试初始化"""
    assert stock_trader.target_date == base_date
    assert len(stock_trader.financial_reports) > 0
    assert len(stock_trader.daily_indicators) > 0
    assert len(stock_trader.daily_quotes) > 0
    assert len(stock_trader.dividends) > 0
    assert stock_trader.daily_indicators[0].ts_code == "600519.SH"

def test_check_roe_condition(stock_trader):
    """测试ROE条件检查"""
    # 茅台的ROE应该大于15%
    assert stock_trader._check_roe_condition() is True

def test_check_pe_percentile(stock_trader):
    """测试PE百分位检查"""
    percentile = stock_trader._check_pe_percentile()
    # 确保返回的是一个0到1之间的数值
    assert 0 <= percentile <= 1

def test_calculate_dcf_ratio(stock_trader):
    """测试DCF比率计算"""
    ratio = stock_trader._calculate_dcf_ratio()
    # 确保返回的是一个正数
    assert ratio > 0

def test_get_action(stock_trader):
    """测试获取交易动作"""
    action = stock_trader.get_action()
    # 确保返回的是有效的交易动作
    assert action in [TradeAction.BUY, TradeAction.SELL, TradeAction.HOLD]

def teardown_module(module):
    """测试完成后清理测试数据库"""
    if os.path.exists('./test_ashare_stock.db'):
        os.remove('./test_ashare_stock.db')