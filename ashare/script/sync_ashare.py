# 导入同步服务
import os
from ashare.models.sync_service import SyncService

if __name__ == '__main__':    
    # 创建同步服务实例
    sync_svc = SyncService('./ashare_stock.db', os.getenv('TUSHARE_TOKEN'))
    
    # 调用同步步骤函数
    sync_svc.sync_all()
