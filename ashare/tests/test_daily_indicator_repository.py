import pytest
from datetime import date
from decimal import Decimal
from ashare.models.daily_indicator import DailyIndicator
from ashare.models.daily_indicator_repository import DailyIndicatorRepository

@pytest.fixture
def db_path(tmp_path):
    """创建临时数据库文件路径"""
    return str(tmp_path / "test_daily_indicators.db")

@pytest.fixture
def repo(db_path):
    """创建 DailyIndicatorRepository 实例"""
    return DailyIndicatorRepository(db_path)

@pytest.fixture
def sample_indicator():
    """创建测试用的每日指标数据"""
    return DailyIndicator(
        ts_code="000001.SZ",
        trade_date=date(2023, 1, 1),
        close=Decimal("10.5"),
        turnover_rate=Decimal("2.5"),
        turnover_rate_f=Decimal("2.3"),
        volume_ratio=Decimal("1.2"),
        pe=Decimal("15.5"),
        pe_ttm=Decimal("14.8"),
        pb=Decimal("1.8"),
        ps=Decimal("2.1"),
        ps_ttm=Decimal("2.0"),
        dv_ratio=Decimal("3.5"),
        dv_ttm=Decimal("3.2"),
        total_share=Decimal("10000000"),
        float_share=Decimal("8000000"),
        free_share=Decimal("7000000"),
        total_mv=Decimal("105000000"),
        circ_mv=Decimal("84000000")
    )

@pytest.fixture
def sample_indicators():
    """创建多个测试用的每日指标数据"""
    return [
        DailyIndicator(
            ts_code="000001.SZ",
            trade_date=date(2023, 1, 1),
            close=Decimal("10.5"),
            turnover_rate=Decimal("2.5"),
            turnover_rate_f=Decimal("2.3"),
            volume_ratio=Decimal("1.2"),
            pe=Decimal("15.5"),
            pe_ttm=Decimal("14.8"),
            pb=Decimal("1.8"),
            ps=Decimal("2.1"),
            ps_ttm=Decimal("2.0"),
            dv_ratio=Decimal("3.5"),
            dv_ttm=Decimal("3.2"),
            total_share=Decimal("10000000"),
            float_share=Decimal("8000000"),
            free_share=Decimal("7000000"),
            total_mv=Decimal("105000000"),
            circ_mv=Decimal("84000000")
        ),
        DailyIndicator(
            ts_code="000001.SZ",
            trade_date=date(2023, 1, 2),
            close=Decimal("10.8"),
            turnover_rate=Decimal("2.8"),
            turnover_rate_f=Decimal("2.5"),
            volume_ratio=Decimal("1.3"),
            pe=Decimal("15.8"),
            pe_ttm=Decimal("15.0"),
            pb=Decimal("1.9"),
            ps=Decimal("2.2"),
            ps_ttm=Decimal("2.1"),
            dv_ratio=Decimal("3.4"),
            dv_ttm=Decimal("3.1"),
            total_share=Decimal("10000000"),
            float_share=Decimal("8000000"),
            free_share=Decimal("7000000"),
            total_mv=Decimal("108000000"),
            circ_mv=Decimal("86400000")
        )
    ]

def test_save_and_find_by_code_and_date(repo, sample_indicator):
    """测试保存和按代码日期查询指标"""
    # 保存数据
    repo.save(sample_indicator)
    
    # 查询并验证
    found = repo.find_by_code_and_date(
        sample_indicator.ts_code,
        sample_indicator.trade_date
    )
    assert found is not None
    assert found.ts_code == sample_indicator.ts_code
    assert found.trade_date == sample_indicator.trade_date
    assert found.close == sample_indicator.close
    assert found.pe == sample_indicator.pe

def test_save_many_and_find_by_code(repo, sample_indicators):
    """测试批量保存和按代码查询"""
    # 批量保存
    repo.save_many(sample_indicators)
    
    # 查询并验证
    found = repo.find_by_code(sample_indicators[0].ts_code)
    assert len(found) == 2
    assert found[0].trade_date < found[1].trade_date
    assert found[0].close == Decimal("10.5")
    assert found[1].close == Decimal("10.8")

def test_find_by_date(repo, sample_indicators):
    """测试按日期查询"""
    # 保存测试数据
    repo.save_many(sample_indicators)
    
    # 查询指定日期的数据
    found = repo.find_by_date(date(2023, 1, 1))
    assert len(found) == 1
    assert found[0].ts_code == "000001.SZ"
    assert found[0].close == Decimal("10.5")

def test_update_indicator(repo, sample_indicator):
    """测试更新指标数据"""
    # 先保存原始数据
    repo.save(sample_indicator)
    
    # 修改数据并保存
    updated_indicator = DailyIndicator(
        **{**sample_indicator.__dict__, 
           "close": Decimal("11.0"),
           "pe": Decimal("16.0")}
    )
    repo.save(updated_indicator)
    
    # 查询并验证
    found = repo.find_by_code_and_date(
        sample_indicator.ts_code,
        sample_indicator.trade_date
    )
    assert found.close == Decimal("11.0")
    assert found.pe == Decimal("16.0")

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