import os
import pytest
from datetime import datetime, date
from unittest.mock import Mock, patch
from ..models.sync_service import SyncService
from ..models.sync_type import SyncType
from ..models.sync_task import SyncTask

@pytest.fixture
def db_path():
    """创建临时数据库文件"""
    db_file = "./test_sync.db"
    yield str(db_file)
    # 测试结束后删除数据库文件
    if os.path.exists(db_file):
        os.remove(db_file)

@pytest.fixture
def tushare_token():
    """获取测试用的 tushare token"""
    api_token = os.getenv('TUSHARE_TOKEN')
    print("api_toke=", api_token)
    if not api_token:
        pytest.skip('需要设置 TUSHARE_TOKEN 环境变量')
    return api_token

@pytest.fixture
def sync_service(db_path, tushare_token):
    """创建 SyncService 实例"""
    return SyncService(db_path, tushare_token,ts_codes=['002001.SZ'])

def test_sync_stock_list(sync_service):
    """测试同步股票列表"""
    # 执行同步
    sync_service.sync(SyncType.STOCK_LIST)
    
    # 验证同步任务已记录
    task = sync_service.sync_task_repo.get_task(SyncType.STOCK_LIST)
    assert task is not None
    assert isinstance(task.last_sync_time, datetime)

def test_sync_with_invalid_type(sync_service):
    """测试使用无效的同步类型"""
    with pytest.raises(ValueError) as exc_info:
        # 通过修改枚举值来模拟无效的同步类型
        invalid_type = Mock()
        invalid_type.value = "INVALID_TYPE"
        sync_service.sync(invalid_type)
    
    assert "未找到" in str(exc_info.value)

def test_sync_all(sync_service):
    """测试同步所有数据"""
    # 执行所有同步任务
    sync_service.sync_all()
    
    # 验证所有类型的任务都已执行
    for sync_type in SyncType:
        task = sync_service.sync_task_repo.get_task(sync_type)
        assert task is not None
        assert isinstance(task.last_sync_time, datetime)

def test_sync_when_need_sync(sync_service):
    """测试需要同步时的情况"""
    # 模拟一个需要同步的任务
    old_time = datetime(2000, 1, 1)
    sync_service.sync_task_repo.update_sync_time(SyncType.STOCK_LIST)
    
    # 执行同步
    sync_service.sync(SyncType.STOCK_LIST)
    
    # 验证同步时间已更新
    task = sync_service.sync_task_repo.get_task(SyncType.STOCK_LIST)
    assert task.last_sync_time > old_time

def test_sync_when_no_need_sync(sync_service):
    """测试不需要同步时的情况"""
    # 先执行一次同步
    sync_service.sync(SyncType.STOCK_LIST)
    first_sync_time = sync_service.sync_task_repo.get_task(SyncType.STOCK_LIST).last_sync_time
    
    # Mock SyncTask.need_sync 方法返回 False
    with patch('ashare.models.sync_task.SyncTask.need_sync', return_value=False):
        # 再次执行同步
        sync_service.sync(SyncType.STOCK_LIST)
        
        # 验证同步时间没有更新
        second_sync_time = sync_service.sync_task_repo.get_task(SyncType.STOCK_LIST).last_sync_time
        assert second_sync_time == first_sync_time

def test_sync_with_error(sync_service):
    """测试同步出错的情况"""
    # Mock fetch_and_save 方法抛出异常
    with patch.dict(sync_service._fetcher_map, {
        SyncType.STOCK_LIST: Mock(fetch_and_save=Mock(side_effect=Exception("同步出错")))
    }):
        with pytest.raises(Exception) as exc_info:
            sync_service.sync(SyncType.STOCK_LIST)
        
        assert "同步出错" in str(exc_info.value)
        
        # 验证同步时间没有更新
        task = sync_service.sync_task_repo.get_task(SyncType.STOCK_LIST)
        assert task is None