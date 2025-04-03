import pytest
from datetime import date
from decimal import Decimal
from ashare.models.daily_quote import DailyQuote
from ashare.models.daily_quote_repository import DailyQuoteRepository

@pytest.fixture
def db_path(tmp_path):
    """创建临时数据库文件路径"""
    return str(tmp_path / "test_daily_quotes.db")

@pytest.fixture
def repo(db_path):
    """创建 DailyQuoteRepository 实例"""
    return DailyQuoteRepository(db_path)

@pytest.fixture
def sample_quote():
    """创建测试用的日行情数据"""
    return DailyQuote(
        ts_code="000001.SZ",
        trade_date=date(2023, 1, 1),
        open=Decimal("10.50"),
        high=Decimal("11.20"),
        low=Decimal("10.30"),
        close=Decimal("10.85"),
        pre_close=Decimal("10.45"),
        change=Decimal("0.40"),
        pct_chg=Decimal("3.83"),
        vol=Decimal("1234567"),
        amount=Decimal("13456.78")
    )

@pytest.fixture
def sample_quotes():
    """创建多个测试用的日行情数据"""
    return [
        DailyQuote(
            ts_code="000001.SZ",
            trade_date=date(2023, 1, 1),
            open=Decimal("10.50"),
            high=Decimal("11.20"),
            low=Decimal("10.30"),
            close=Decimal("10.85"),
            pre_close=Decimal("10.45"),
            change=Decimal("0.40"),
            pct_chg=Decimal("3.83"),
            vol=Decimal("1234567"),
            amount=Decimal("13456.78")
        ),
        DailyQuote(
            ts_code="000001.SZ",
            trade_date=date(2023, 1, 2),
            open=Decimal("10.85"),
            high=Decimal("11.50"),
            low=Decimal("10.80"),
            close=Decimal("11.20"),
            pre_close=Decimal("10.85"),
            change=Decimal("0.35"),
            pct_chg=Decimal("3.23"),
            vol=Decimal("987654"),
            amount=Decimal("11234.56")
        )
    ]

def test_save_and_find_by_code_and_date(repo, sample_quote):
    """测试保存和按代码日期查询行情"""
    # 保存数据
    repo.save(sample_quote)
    
    # 查询并验证
    found = repo.find_by_code_and_date(
        sample_quote.ts_code,
        sample_quote.trade_date
    )
    assert found is not None
    assert found.ts_code == sample_quote.ts_code
    assert found.trade_date == sample_quote.trade_date
    assert found.open == sample_quote.open
    assert found.close == sample_quote.close
    assert found.vol == sample_quote.vol

def test_save_many_and_find_by_code(repo, sample_quotes):
    """测试批量保存和按代码查询"""
    # 批量保存
    repo.save_many(sample_quotes)
    
    # 查询并验证
    found = repo.find_by_code(sample_quotes[0].ts_code)
    assert len(found) == 2
    assert found[0].trade_date < found[1].trade_date
    assert found[0].close == Decimal("10.85")
    assert found[1].close == Decimal("11.20")

def test_find_by_date(repo, sample_quotes):
    """测试按日期查询"""
    # 保存测试数据
    repo.save_many(sample_quotes)
    
    # 查询指定日期的数据
    found = repo.find_by_date(date(2023, 1, 1))
    assert len(found) == 1
    assert found[0].ts_code == "000001.SZ"
    assert found[0].close == Decimal("10.85")

def test_update_quote(repo, sample_quote):
    """测试更新行情数据"""
    # 先保存原始数据
    repo.save(sample_quote)
    
    # 修改数据并保存
    updated_quote = DailyQuote(
        **{**sample_quote.__dict__, 
           "close": Decimal("11.00"),
           "change": Decimal("0.55"),
           "pct_chg": Decimal("5.26")}
    )
    repo.save(updated_quote)
    
    # 查询并验证
    found = repo.find_by_code_and_date(
        sample_quote.ts_code,
        sample_quote.trade_date
    )
    assert found.close == Decimal("11.00")
    assert found.change == Decimal("0.55")
    assert found.pct_chg == Decimal("5.26")

def test_not_found(repo):
    """测试查询不存在的数据"""
    found = repo.find_by_code_and_date("999999.XX", date(2023, 1, 1))
    assert found is None

def test_find_by_code_not_found(repo):
    """测试查询不存在的股票代码"""
    found = repo.find_by_code("999999.XX")
    assert len(found) == 0

def test_find_by_date_not_found(repo):
    """测试查询不存在的日期"""
    found = repo.find_by_date(date(2099, 1, 1))
    assert len(found) == 0