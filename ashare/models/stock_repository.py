import sqlite3
from datetime import datetime
from typing import List, Optional
from .stock import Stock

class StockRepository:
    """股票数据仓库，负责股票数据的存储和读取"""
    
    def __init__(self, db_path: str):
        """
        初始化股票数据仓库
        
        Args:
            db_path: SQLite数据库文件路径
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stocks (
                    ts_code TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    area TEXT,
                    industry TEXT,
                    fullname TEXT,
                    enname TEXT,
                    cnspell TEXT,
                    market TEXT,
                    exchange TEXT,
                    curr_type TEXT,
                    list_status TEXT,
                    list_date TEXT,
                    delist_date TEXT,
                    is_hs TEXT,
                    act_name TEXT,
                    act_ent_type TEXT
                )
            ''')
            conn.commit()
    
    def save(self, stock: Stock) -> None:
        """
        保存股票信息到数据库
        
        Args:
            stock: Stock对象
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO stocks (
                    ts_code, symbol, name, area, industry, fullname, enname,
                    cnspell, market, exchange, curr_type, list_status,
                    list_date, delist_date, is_hs, act_name, act_ent_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stock.ts_code, stock.symbol, stock.name, stock.area,
                stock.industry, stock.fullname, stock.enname, stock.cnspell,
                stock.market, stock.exchange, stock.curr_type, stock.list_status,
                stock.list_date.isoformat() if stock.list_date else None,
                stock.delist_date.isoformat() if stock.delist_date else None,
                stock.is_hs, stock.act_name, stock.act_ent_type
            ))
    
    def save_many(self, stocks: List[Stock]) -> None:
        """
        批量保存股票信息
        
        Args:
            stocks: Stock对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO stocks (
                    ts_code, symbol, name, area, industry, fullname, enname,
                    cnspell, market, exchange, curr_type, list_status,
                    list_date, delist_date, is_hs, act_name, act_ent_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                (stock.ts_code, stock.symbol, stock.name, stock.area,
                 stock.industry, stock.fullname, stock.enname, stock.cnspell,
                 stock.market, stock.exchange, stock.curr_type, stock.list_status,
                 stock.list_date.isoformat() if stock.list_date else None,
                 stock.delist_date.isoformat() if stock.delist_date else None,
                 stock.is_hs, stock.act_name, stock.act_ent_type)
                for stock in stocks
            ])
    
    def find_by_ts_code(self, ts_code: str) -> Optional[Stock]:
        """
        根据股票代码查询股票信息
        
        Args:
            ts_code: 股票代码
            
        Returns:
            Stock对象，如果未找到返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM stocks WHERE ts_code = ?', (ts_code,))
            row = cursor.fetchone()
            if row:
                return self._row_to_stock(row)
        return None
    
    def find_all(self) -> List[Stock]:
        """
        获取所有股票信息
        
        Returns:
            Stock对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM stocks')
            return [self._row_to_stock(row) for row in cursor.fetchall()]
    
    def find_by_industry(self, industry: str) -> List[Stock]:
        """
        根据行业查询股票列表
        
        Args:
            industry: 行业名称
            
        Returns:
            Stock对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM stocks WHERE industry = ?', (industry,))
            return [self._row_to_stock(row) for row in cursor.fetchall()]
    
    def _row_to_stock(self, row: tuple) -> Stock:
        """将数据库行转换为Stock对象"""
        return Stock(
            ts_code=row[0],
            symbol=row[1],
            name=row[2],
            area=row[3],
            industry=row[4],
            fullname=row[5],
            enname=row[6],
            cnspell=row[7],
            market=row[8],
            exchange=row[9],
            curr_type=row[10],
            list_status=row[11],
            list_date=datetime.fromisoformat(row[12]).date() if row[12] else None,
            delist_date=datetime.fromisoformat(row[13]).date() if row[13] else None,
            is_hs=row[14],
            act_name=row[15],
            act_ent_type=row[16]
        )