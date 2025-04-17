import os
import pytest
from datetime import datetime, timedelta
from ..models.sync_task_repository import SyncTaskRepository
from ..models.sync_type import SyncType

@pytest.fixture
def db_path(tmp_path):
    """创建临时数据库文件"""
    db_file = tmp_path / "test_sync.db"
    yield str(db_file)
    # 测试结束后删除数据库文件
    # if os.path.exists(db_file):
    #     os.remove(db_file)

@pytest.fixture
def repository(db_path):
    """创建仓库实例"""
    return SyncTaskRepository(db_path)

def test_get_task_not_exists(repository):
    """测试获取不存在的同步任务"""
    task = repository.get_task(SyncType.STOCK_LIST)
    assert task is None

def test_update_and_get_task(repository):
    """测试更新和获取同步任务"""
    # 更新同步时间
    repository.update_sync_time(SyncType.STOCK_LIST)
    
    # 获取同步任务
    task = repository.get_task(SyncType.STOCK_LIST)
    
    # 验证结果
    assert task is not None
    assert task.sync_type == SyncType.STOCK_LIST
    assert task.last_sync_time is not None
    assert isinstance(task.last_sync_time, datetime)
    # 验证时间在最近1秒内
    assert datetime.now() - task.last_sync_time < timedelta(seconds=1)

def test_update_existing_task(repository):
    """测试更新已存在的同步任务"""
    # 首次更新
    repository.update_sync_time(SyncType.DAILY_QUOTE)
    first_task = repository.get_task(SyncType.DAILY_QUOTE)
    first_sync_time = first_task.last_sync_time
    
    # 等待一小段时间
    import time
    time.sleep(0.1)
    
    # 再次更新
    repository.update_sync_time(SyncType.DAILY_QUOTE)
    second_task = repository.get_task(SyncType.DAILY_QUOTE)
    second_sync_time = second_task.last_sync_time
    
    # 验证时间已更新
    assert second_sync_time > first_sync_time

def test_multiple_sync_types(repository):
    """测试多个同步类型"""
    # 更新不同类型的同步任务
    repository.update_sync_time(SyncType.STOCK_LIST)
    repository.update_sync_time(SyncType.DAILY_QUOTE)
    repository.update_sync_time(SyncType.FINANCIAL_REPORT)
    
    # 验证每个类型都能正确获取
    for sync_type in [SyncType.STOCK_LIST, SyncType.DAILY_QUOTE, SyncType.FINANCIAL_REPORT]:
        task = repository.get_task(sync_type)
        assert task is not None
        assert task.sync_type == sync_type
        assert task.last_sync_time is not None