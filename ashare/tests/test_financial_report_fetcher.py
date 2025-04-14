import pytest
from datetime import datetime, date
from decimal import Decimal
from ashare.models.financial_report_fetcher import FinancialReportFetcher
import os
from datetime import date
from ashare.models.financial_report import (
    FinancialReport, IncomeStatement, BalanceSheet,
    CashFlowStatement, FinancialIndicators
)

@pytest.fixture
def fetcher():
    """创建 FinancialReportFetcher 实例"""
    api_token = os.getenv('TUSHARE_TOKEN') or ""
    if not api_token:
        pytest.skip('需要设置 TUSHARE_TOKEN 环境变量')
    return FinancialReportFetcher(api_token)

def test_fetch_income_statement(fetcher):
    """测试获取利润表数据"""
    # 获取平安银行2022年报数据
    statements = fetcher.fetch_income_statement(
        '000001.SZ', 
        date(2022, 1, 1), 
        date(2022, 12, 31)
    )
    
    # 验证结果
    assert len(statements) > 0
    statement = statements[0]
    assert isinstance(statement, IncomeStatement)
    assert statement.ts_code == '000001.SZ'
    assert statement.end_date >= date(2022, 1, 1)
    assert statement.end_date <= date(2022, 12, 31)
    assert isinstance(statement.total_revenue, Decimal)
    assert statement.total_revenue > 0
    print(repr(statement))

def test_fetch_balance_sheet(fetcher):
    """测试获取资产负债表数据"""
    # 获取平安银行2022年报数据
    sheets = fetcher.fetch_balance_sheet(
        '000001.SZ', 
        date(2022, 1, 1), 
        date(2022, 12, 31)
    )
    
    # 验证结果
    assert len(sheets) > 0
    sheet = sheets[0]
    assert isinstance(sheet, BalanceSheet)
    assert sheet.ts_code == '000001.SZ'
    assert sheet.end_date >= date(2022, 1, 1)
    assert sheet.end_date <= date(2022, 12, 31)
    assert isinstance(sheet.total_assets, Decimal)
    assert sheet.total_assets > 0
    print(repr(sheet))

def test_fetch_cash_flow(fetcher):
    """测试获取现金流量表数据"""
    # 获取平安银行2022年报数据
    statements = fetcher.fetch_cash_flow(
        '000001.SZ', 
        date(2022, 1, 1), 
        date(2022, 12, 31)
    )
    
    # 验证结果
    assert len(statements) > 0
    statement = statements[0]
    assert isinstance(statement, CashFlowStatement)
    assert statement.ts_code == '000001.SZ'
    assert statement.end_date >= date(2022, 1, 1)
    assert statement.end_date <= date(2022, 12, 31)
    assert isinstance(statement.n_cashflow_act, Decimal)
    print(repr(statement))

def test_fetch_financial_indicators(fetcher):
    """测试获取财务指标数据"""
    # 获取平安银行2022年报数据
    indicators = fetcher.fetch_financial_indicators(
        '000001.SZ', 
        date(2022, 1, 1), 
        date(2022, 12, 31)
    )
    
    # 验证结果
    assert len(indicators) > 0
    indicator = indicators[0]
    assert isinstance(indicator, FinancialIndicators)
    assert indicator.ts_code == '000001.SZ'
    assert indicator.end_date >= date(2022, 1, 1)
    assert indicator.end_date <= date(2022, 12, 31)
    assert isinstance(indicator.roe, Decimal)
    print(repr(indicator))

def test_fetch_financial_reports(fetcher):
    """测试获取完整财务报告"""
    # 获取平安银行2022年报数据
    reports = fetcher.fetch_financial_reports(
        '000001.SZ', 
        date(2022, 1, 1), 
        date(2022, 12, 31)
    )
    
    # 验证结果
    assert len(reports) > 0
    report = reports[0]
    assert isinstance(report, FinancialReport)
    assert report.ts_code == '000001.SZ'
    assert report.report_date >= date(2022, 1, 1)
    assert report.report_date <= date(2022, 12, 31)
    
    # 验证各报表是否正确关联
    assert report.income_statement is not None
    assert report.balance_sheet is not None
    assert report.cash_flow_statement is not None
    assert report.financial_indicators is not None
    
    # 验证关键财务数据
    assert report.income_statement.total_revenue > 0
    assert report.balance_sheet.total_assets > 0
    if report.cash_flow_statement.free_cashflow:
        assert isinstance(report.cash_flow_statement.free_cashflow, Decimal)
    if report.financial_indicators.roe:
        assert isinstance(report.financial_indicators.roe, Decimal)
    print(repr(report))

def test_date_conversion(fetcher):
    """测试日期转换方法"""
    assert fetcher._convert_date('20230101') == date(2023, 1, 1)
    assert fetcher._convert_date(None) is None

def test_decimal_conversion(fetcher):
    """测试数值转换方法"""
    assert fetcher._convert_decimal(100) == Decimal('100')
    assert fetcher._convert_decimal(3.14) == Decimal('3.14')
    assert fetcher._convert_decimal(None) is None
    assert fetcher._convert_decimal(float('nan')) is None  # 使用 float('nan') 代替字符串 "NaN"