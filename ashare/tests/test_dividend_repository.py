import pytest
from datetime import date
from decimal import Decimal
from ashare.models.dividend import Dividend
from ashare.models.dividend_repository import DividendRepository

@pytest.fixture
def db_path(tmp_path):
    """创建临时数据库文件路径"""
    return str(tmp_path / "test_dividends.db")

@pytest.fixture
def repo(db_path):
    """创建 DividendRepository 实例"""
    return DividendRepository(db_path)

@pytest.fixture
def sample_dividend():
    """创建测试用的分红送股数据"""
    return Dividend(
        ts_code="000001.SZ",
        end_date=date(2022, 12, 31),
        ann_date=date(2023, 4, 15),
        div_proc="实施",
        stk_div=Decimal("0"),
        stk_bo_rate=Decimal("0"),
        stk_co_rate=Decimal("0"),
        cash_div=Decimal("2.28"),
        cash_div_tax=Decimal("2.28"),
        record_date=date(2023, 5, 20),
        ex_date=date(2023, 5, 21),
        pay_date=date(2023, 5, 22),
        div_listdate=None,
        imp_ann_date=date(2023, 5, 15),
        base_date=date(2023, 5, 20),
        base_share=Decimal("19406")
    )

@pytest.fixture
def sample_dividends():
    """创建多个测试用的分红送股数据"""
    return [
        Dividend(
            ts_code="000001.SZ",
            end_date=date(2022, 12, 31),
            ann_date=date(2023, 4, 15),
            div_proc="实施",
            stk_div=Decimal("0"),
            stk_bo_rate=Decimal("0"),
            stk_co_rate=Decimal("0"),
            cash_div=Decimal("2.28"),
            cash_div_tax=Decimal("2.28"),
            record_date=date(2023, 5, 20),
            ex_date=date(2023, 5, 21),
            pay_date=date(2023, 5, 22),
            div_listdate=None,
            imp_ann_date=date(2023, 5, 15),
            base_date=date(2023, 5, 20),
            base_share=Decimal("19406")
        ),
        Dividend(
            ts_code="000001.SZ",
            end_date=date(2021, 12, 31),
            ann_date=date(2022, 4, 15),
            div_proc="实施",
            stk_div=Decimal("0"),
            stk_bo_rate=Decimal("0"),
            stk_co_rate=Decimal("0"),
            cash_div=Decimal("2.08"),
            cash_div_tax=Decimal("2.08"),
            record_date=date(2022, 5, 20),
            ex_date=date(2022, 5, 21),
            pay_date=date(2022, 5, 22),
            div_listdate=None,
            imp_ann_date=date(2022, 5, 15),
            base_date=date(2022, 5, 20),
            base_share=Decimal("19406")
        )
    ]

def test_save_and_find_by_code_and_end_date(repo, sample_dividend):
    """测试保存和按代码年度查询分红数据"""
    # 保存数据
    repo.save(sample_dividend)
    
    # 查询并验证
    found = repo.find_by_code_and_end_date(
        sample_dividend.ts_code,
        sample_dividend.end_date
    )
    assert found is not None
    assert found.ts_code == sample_dividend.ts_code
    assert found.end_date == sample_dividend.end_date
    assert found.cash_div == sample_dividend.cash_div
    assert found.ex_date == sample_dividend.ex_date

def test_save_many_and_find_by_code(repo, sample_dividends):
    """测试批量保存和按代码查询"""
    # 批量保存
    repo.save_many(sample_dividends)
    
    # 查询并验证
    found = repo.find_by_code(sample_dividends[0].ts_code)
    assert len(found) == 2
    assert found[0].end_date > found[1].end_date  # 验证降序排序
    assert found[0].cash_div == Decimal("2.28")
    assert found[1].cash_div == Decimal("2.08")

def test_find_by_ex_date(repo, sample_dividends):
    """测试按除权除息日查询"""
    # 保存测试数据
    repo.save_many(sample_dividends)
    
    # 查询指定除权除息日的数据
    found = repo.find_by_ex_date(date(2023, 5, 21))
    assert len(found) == 1
    assert found[0].ts_code == "000001.SZ"
    assert found[0].cash_div == Decimal("2.28")

def test_update_dividend(repo, sample_dividend):
    """测试更新分红数据"""
    # 先保存原始数据
    repo.save(sample_dividend)
    
    # 修改数据并保存
    updated_dividend = Dividend(
        **{**sample_dividend.__dict__, 
           "cash_div": Decimal("2.38"),
           "cash_div_tax": Decimal("2.38")}
    )
    repo.save(updated_dividend)
    
    # 查询并验证
    found = repo.find_by_code_and_end_date(
        sample_dividend.ts_code,
        sample_dividend.end_date
    )
    assert found.cash_div == Decimal("2.38")
    assert found.cash_div_tax == Decimal("2.38")

def test_not_found(repo):
    """测试查询不存在的数据"""
    found = repo.find_by_code_and_end_date("999999.XX", date(2023, 12, 31))
    assert found is None

def test_find_by_code_not_found(repo):
    """测试查询不存在的股票代码"""
    found = repo.find_by_code("999999.XX")
    assert len(found) == 0

def test_find_by_ex_date_not_found(repo):
    """测试查询不存在的除权除息日"""
    found = repo.find_by_ex_date(date(2099, 1, 1))
    assert len(found) == 0