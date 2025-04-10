from datetime import datetime
from typing import Optional
import sqlite3
from .sync_task import SyncTask
from .sync_type import SyncType

class SyncTaskRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_table()
    
    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def _execute(self, sql: str, parameters: tuple = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if parameters:
                return cursor.execute(sql, parameters)
            return cursor.execute(sql)
    
    def _init_table(self):
        self._execute("""
            CREATE TABLE IF NOT EXISTS sync_tasks (
                sync_type TEXT PRIMARY KEY,
                last_sync_time TIMESTAMP
            )
        """)
    
    def get_task(self, sync_type: SyncType) -> Optional[SyncTask]:
        result = self._execute(
            "SELECT sync_type, last_sync_time FROM sync_tasks WHERE sync_type = ?",
            (sync_type.value,)
        ).fetchone()
        
        if not result:
            return None
            
        return SyncTask(
            sync_type=sync_type,
            last_sync_time=datetime.fromisoformat(result[1]) if result[1] else None
        )
    
    def update_sync_time(self, sync_type: SyncType):
        self._execute(
            """
            INSERT INTO sync_tasks (sync_type, last_sync_time)
            VALUES (?, ?)
            ON CONFLICT(sync_type) DO UPDATE SET last_sync_time = ?
            """,
            (sync_type.value, datetime.now(), datetime.now())
        )