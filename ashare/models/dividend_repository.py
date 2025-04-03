import sqlite3
from datetime import datetime, date
from typing import List, Optional
from .dividend import Dividend
from decimal import Decimal

class DividendRepository:
    """A股分红送股数据仓库"""
    
    def __init__(self, db_path: str):
        """
        初始化数据仓库
        
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
                CREATE TABLE IF NOT EXISTS dividends (
                    ts_code TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    ann_date TEXT,
                    div_proc TEXT,
                    stk_div DECIMAL(20,4),
                    stk_bo_rate DECIMAL(20,4),
                    stk_co_rate DECIMAL(20,4),
                    cash_div DECIMAL(20,4),
                    cash_div_tax DECIMAL(20,4),
                    record_date TEXT,
                    ex_date TEXT,
                    pay_date TEXT,
                    div_listdate TEXT,
                    imp_ann_date TEXT,
                    base_date TEXT,
                    base_share DECIMAL(20,4),
                    PRIMARY KEY (ts_code, end_date)
                )
            ''')
            # 创建索引以提升查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_dividends_ex_date ON dividends(ex_date)')
            conn.commit()
    
    def save(self, dividend: Dividend) -> None:
        """
        保存分红送股数据
        
        Args:
            dividend: Dividend对象
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO dividends VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                dividend.ts_code,
                dividend.end_date.isoformat() if dividend.end_date else None,
                dividend.ann_date.isoformat() if dividend.ann_date else None,
                dividend.div_proc,
                float(dividend.stk_div),
                float(dividend.stk_bo_rate),
                float(dividend.stk_co_rate),
                float(dividend.cash_div),
                float(dividend.cash_div_tax),
                dividend.record_date.isoformat() if dividend.record_date else None,
                dividend.ex_date.isoformat() if dividend.ex_date else None,
                dividend.pay_date.isoformat() if dividend.pay_date else None,
                dividend.div_listdate.isoformat() if dividend.div_listdate else None,
                dividend.imp_ann_date.isoformat() if dividend.imp_ann_date else None,
                dividend.base_date.isoformat() if dividend.base_date else None,
                float(dividend.base_share)
            ))
    
    def save_many(self, dividends: List[Dividend]) -> None:
        """
        批量保存分红送股数据
        
        Args:
            dividends: Dividend对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO dividends VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', [
                (
                    div.ts_code,
                    div.end_date.isoformat() if div.end_date else None,
                    div.ann_date.isoformat() if div.ann_date else None,
                    div.div_proc,
                    float(div.stk_div),
                    float(div.stk_bo_rate),
                    float(div.stk_co_rate),
                    float(div.cash_div),
                    float(div.cash_div_tax),
                    div.record_date.isoformat() if div.record_date else None,
                    div.ex_date.isoformat() if div.ex_date else None,
                    div.pay_date.isoformat() if div.pay_date else None,
                    div.div_listdate.isoformat() if div.div_listdate else None,
                    div.imp_ann_date.isoformat() if div.imp_ann_date else None,
                    div.base_date.isoformat() if div.base_date else None,
                    float(div.base_share)
                )
                for div in dividends
            ])
    
    def find_by_code_and_end_date(self, ts_code: str, end_date: date) -> Optional[Dividend]:
        """
        查询指定股票在指定年度的分红送股数据
        
        Args:
            ts_code: 股票代码
            end_date: 分红年度截止日
            
        Returns:
            Dividend对象，如果未找到返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM dividends WHERE ts_code = ? AND end_date = ?',
                (ts_code, end_date.isoformat())
            )
            row = cursor.fetchone()
            return self._row_to_dividend(row) if row else None
    
    def find_by_code(self, ts_code: str) -> List[Dividend]:
        """
        查询指定股票的所有分红送股数据
        
        Args:
            ts_code: 股票代码
            
        Returns:
            Dividend对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM dividends WHERE ts_code = ? ORDER BY end_date DESC',
                (ts_code,)
            )
            return [self._row_to_dividend(row) for row in cursor.fetchall()]
    
    def find_by_ex_date(self, ex_date: date) -> List[Dividend]:
        """
        查询指定除权除息日的所有分红送股数据
        
        Args:
            ex_date: 除权除息日
            
        Returns:
            Dividend对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM dividends WHERE ex_date = ? ORDER BY ts_code',
                (ex_date.isoformat(),)
            )
            return [self._row_to_dividend(row) for row in cursor.fetchall()]
    
    def _row_to_dividend(self, row: tuple) -> Dividend:
        """将数据库行转换为Dividend对象"""
        return Dividend(
            ts_code=row[0],
            end_date=datetime.fromisoformat(row[1]).date() if row[1] else None,
            ann_date=datetime.fromisoformat(row[2]).date() if row[2] else None,
            div_proc=row[3],
            stk_div=Decimal(str(row[4])),
            stk_bo_rate=Decimal(str(row[5])),
            stk_co_rate=Decimal(str(row[6])),
            cash_div=Decimal(str(row[7])),
            cash_div_tax=Decimal(str(row[8])),
            record_date=datetime.fromisoformat(row[9]).date() if row[9] else None,
            ex_date=datetime.fromisoformat(row[10]).date() if row[10] else None,
            pay_date=datetime.fromisoformat(row[11]).date() if row[11] else None,
            div_listdate=datetime.fromisoformat(row[12]).date() if row[12] else None,
            imp_ann_date=datetime.fromisoformat(row[13]).date() if row[13] else None,
            base_date=datetime.fromisoformat(row[14]).date() if row[14] else None,
            base_share=Decimal(str(row[15]))
        )