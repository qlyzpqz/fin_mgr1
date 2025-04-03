import sqlite3
from datetime import datetime, date
from typing import List, Optional
from .daily_quote import DailyQuote
from decimal import Decimal

class DailyQuoteRepository:
    """A股日行情数据仓库"""
    
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
                CREATE TABLE IF NOT EXISTS daily_quotes (
                    ts_code TEXT NOT NULL,
                    trade_date TEXT NOT NULL,
                    open DECIMAL(20,4),
                    high DECIMAL(20,4),
                    low DECIMAL(20,4),
                    close DECIMAL(20,4),
                    pre_close DECIMAL(20,4),
                    change DECIMAL(20,4),
                    pct_chg DECIMAL(20,4),
                    vol DECIMAL(20,4),
                    amount DECIMAL(20,4),
                    PRIMARY KEY (ts_code, trade_date)
                )
            ''')
            # 创建索引以提升查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_quotes_trade_date ON daily_quotes(trade_date)')
            conn.commit()
    
    def save(self, quote: DailyQuote) -> None:
        """
        保存日行情数据
        
        Args:
            quote: DailyQuote对象
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO daily_quotes VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                quote.ts_code,
                quote.trade_date.isoformat(),
                float(quote.open),
                float(quote.high),
                float(quote.low),
                float(quote.close),
                float(quote.pre_close),
                float(quote.change),
                float(quote.pct_chg),
                float(quote.vol),
                float(quote.amount)
            ))
    
    def save_many(self, quotes: List[DailyQuote]) -> None:
        """
        批量保存日行情数据
        
        Args:
            quotes: DailyQuote对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO daily_quotes VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', [
                (
                    quote.ts_code,
                    quote.trade_date.isoformat(),
                    float(quote.open),
                    float(quote.high),
                    float(quote.low),
                    float(quote.close),
                    float(quote.pre_close),
                    float(quote.change),
                    float(quote.pct_chg),
                    float(quote.vol),
                    float(quote.amount)
                )
                for quote in quotes
            ])
    
    def find_by_code_and_date(self, ts_code: str, trade_date: date) -> Optional[DailyQuote]:
        """
        查询指定股票在指定日期的行情数据
        
        Args:
            ts_code: 股票代码
            trade_date: 交易日期
            
        Returns:
            DailyQuote对象，如果未找到返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM daily_quotes WHERE ts_code = ? AND trade_date = ?',
                (ts_code, trade_date.isoformat())
            )
            row = cursor.fetchone()
            return self._row_to_quote(row) if row else None
    
    def find_by_code(self, ts_code: str) -> List[DailyQuote]:
        """
        查询指定股票的所有行情数据
        
        Args:
            ts_code: 股票代码
            
        Returns:
            DailyQuote对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM daily_quotes WHERE ts_code = ? ORDER BY trade_date',
                (ts_code,)
            )
            return [self._row_to_quote(row) for row in cursor.fetchall()]
    
    def find_by_date(self, trade_date: date) -> List[DailyQuote]:
        """
        查询指定日期的所有股票行情数据
        
        Args:
            trade_date: 交易日期
            
        Returns:
            DailyQuote对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM daily_quotes WHERE trade_date = ? ORDER BY ts_code',
                (trade_date.isoformat(),)
            )
            return [self._row_to_quote(row) for row in cursor.fetchall()]
    
    def _row_to_quote(self, row: tuple) -> DailyQuote:
        """将数据库行转换为DailyQuote对象"""
        return DailyQuote(
            ts_code=row[0],
            trade_date=datetime.fromisoformat(row[1]).date(),
            open=Decimal(str(row[2])),
            high=Decimal(str(row[3])),
            low=Decimal(str(row[4])),
            close=Decimal(str(row[5])),
            pre_close=Decimal(str(row[6])),
            change=Decimal(str(row[7])),
            pct_chg=Decimal(str(row[8])),
            vol=Decimal(str(row[9])),
            amount=Decimal(str(row[10]))
        )