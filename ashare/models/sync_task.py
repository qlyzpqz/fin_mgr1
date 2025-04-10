from dataclasses import dataclass
from datetime import datetime
from .sync_type import SyncType

@dataclass
class SyncTask:
    """数据同步任务"""
    sync_type: SyncType           # 同步类型
    last_sync_time: datetime      # 最后同步时间
    
    def need_sync(self) -> bool:
        """检查是否需要同步"""
        if not self.last_sync_time:
            return True
        next_sync_time = self.last_sync_time + self.sync_type.interval
        return datetime.now() >= next_sync_time