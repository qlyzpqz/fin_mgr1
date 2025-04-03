import os
import pytest
from datetime import date
from ashare.models.stock import Stock
from ashare.models.stock_repository import StockRepository

@pytest.fixture
def db_path(tmp_path):
    """创建临时数据库文件路径"""
    return str(tmp_path / "test_stocks.db")

@pytest.fixture
def repo(db_path):
    """创建 StockRepository 实例"""
    return StockRepository(db_path)

@pytest.fixture
def sample_stock():
    """创建测试用的股票数据"""
    return Stock(
        ts_code="000001.SZ",
        symbol="000001",
        name="平安银行",
        area="深圳",
        industry="银行",
        fullname="平安银行股份有限公司",
        enname="Ping An Bank Co., Ltd.",
        cnspell="PAYH",
        market="主板",
        exchange="SZSE",
        curr_type="CNY",
        list_status="L",
        list_date=date(1991, 4, 3),
        delist_date=None,
        is_hs="S",
        act_name="平安银行",
        act_ent_type="1"
    )

@pytest.fixture
def sample_stocks():
    """创建多个测试用的股票数据"""
    return [
        Stock(
            ts_code="000001.SZ",
            symbol="000001",
            name="平安银行",
            area="深圳",
            industry="银行",
            fullname="平安银行股份有限公司",
            enname="Ping An Bank Co., Ltd.",
            cnspell="PAYH",
            market="主板",
            exchange="SZSE",
            curr_type="CNY",
            list_status="L",
            list_date=date(1991, 4, 3),
            delist_date=None,
            is_hs="S",
            act_name="平安银行",
            act_ent_type="1"
        ),
        Stock(
            ts_code="601398.SH",
            symbol="601398",
            name="工商银行",
            area="北京",
            industry="银行",
            fullname="中国工商银行股份有限公司",
            enname="Industrial and Commercial Bank of China Limited",
            cnspell="GSYH",
            market="主板",
            exchange="SSE",
            curr_type="CNY",
            list_status="L",
            list_date=date(2006, 10, 27),
            delist_date=None,
            is_hs="S",
            act_name="工商银行",
            act_ent_type="1"
        )
    ]

def test_save_and_find_by_ts_code(repo, sample_stock):
    """测试保存和按代码查询股票"""
    # 保存股票数据
    repo.save(sample_stock)
    
    # 查询并验证
    found = repo.find_by_ts_code(sample_stock.ts_code)
    assert found is not None
    assert found.ts_code == sample_stock.ts_code
    assert found.name == sample_stock.name
    assert found.list_date == sample_stock.list_date

def test_save_many_and_find_all(repo, sample_stocks):
    """测试批量保存和查询所有股票"""
    # 批量保存
    repo.save_many(sample_stocks)
    
    # 查询所有并验证
    all_stocks = repo.find_all()
    assert len(all_stocks) == len(sample_stocks)
    
    # 验证每个股票的数据
    for stock in sample_stocks:
        found = next((s for s in all_stocks if s.ts_code == stock.ts_code), None)
        assert found is not None
        assert found.name == stock.name
        assert found.industry == stock.industry

def test_find_by_industry(repo, sample_stocks):
    """测试按行业查询股票"""
    # 保存测试数据
    repo.save_many(sample_stocks)
    
    # 查询银行业股票
    bank_stocks = repo.find_by_industry("银行")
    assert len(bank_stocks) == 2
    assert all(stock.industry == "银行" for stock in bank_stocks)

def test_update_stock(repo, sample_stock):
    """测试更新股票信息"""
    # 先保存原始数据
    repo.save(sample_stock)
    
    # 修改数据
    updated_stock = Stock(
        **{**sample_stock.__dict__, "name": "平安银行-更新"}
    )
    repo.save(updated_stock)
    
    # 查询并验证
    found = repo.find_by_ts_code(sample_stock.ts_code)
    assert found.name == "平安银行-更新"

def test_not_found(repo):
    """测试查询不存在的股票"""
    found = repo.find_by_ts_code("999999.XX")
    assert found is None

def test_find_by_industry_not_found(repo, sample_stocks):
    """测试查询不存在的行业"""
    repo.save_many(sample_stocks)
    stocks = repo.find_by_industry("不存在的行业")
    assert len(stocks) == 0