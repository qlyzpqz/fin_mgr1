import sqlite3
from datetime import datetime
from datetime import date
from typing import List, Optional
from .daily_indicator import DailyIndicator
from decimal import Decimal

class DailyIndicatorRepository:
    """A股每日指标数据仓库"""
    
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
                CREATE TABLE IF NOT EXISTS daily_indicators (
                    ts_code TEXT NOT NULL,
                    trade_date TEXT NOT NULL,
                    close DECIMAL(20,4),
                    turnover_rate DECIMAL(20,4),
                    turnover_rate_f DECIMAL(20,4),
                    volume_ratio DECIMAL(20,4),
                    pe DECIMAL(20,4),
                    pe_ttm DECIMAL(20,4),
                    pb DECIMAL(20,4),
                    ps DECIMAL(20,4),
                    ps_ttm DECIMAL(20,4),
                    dv_ratio DECIMAL(20,4),
                    dv_ttm DECIMAL(20,4),
                    total_share DECIMAL(20,4),
                    float_share DECIMAL(20,4),
                    free_share DECIMAL(20,4),
                    total_mv DECIMAL(20,4),
                    circ_mv DECIMAL(20,4),
                    PRIMARY KEY (ts_code, trade_date)
                )
            ''')
            # 创建索引以提升查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_date ON daily_indicators(trade_date)')
            conn.commit()
    
    def save(self, indicator: DailyIndicator) -> None:
        """
        保存每日指标数据
        
        Args:
            indicator: DailyIndicator对象
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO daily_indicators VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                indicator.ts_code,
                indicator.trade_date.isoformat(),
                float(indicator.close),
                float(indicator.turnover_rate),
                float(indicator.turnover_rate_f),
                float(indicator.volume_ratio),
                float(indicator.pe),
                float(indicator.pe_ttm),
                float(indicator.pb),
                float(indicator.ps),
                float(indicator.ps_ttm),
                float(indicator.dv_ratio),
                float(indicator.dv_ttm),
                float(indicator.total_share),
                float(indicator.float_share),
                float(indicator.free_share),
                float(indicator.total_mv),
                float(indicator.circ_mv)
            ))
    
    def save_many(self, indicators: List[DailyIndicator]) -> None:
        """
        批量保存每日指标数据
        
        Args:
            indicators: DailyIndicator对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO daily_indicators VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', [
                (
                    ind.ts_code,
                    ind.trade_date.isoformat(),
                    float(ind.close),
                    float(ind.turnover_rate),
                    float(ind.turnover_rate_f),
                    float(ind.volume_ratio),
                    float(ind.pe),
                    float(ind.pe_ttm),
                    float(ind.pb),
                    float(ind.ps),
                    float(ind.ps_ttm),
                    float(ind.dv_ratio),
                    float(ind.dv_ttm),
                    float(ind.total_share),
                    float(ind.float_share),
                    float(ind.free_share),
                    float(ind.total_mv),
                    float(ind.circ_mv)
                )
                for ind in indicators
            ])
    
    def find_by_code_and_date(self, ts_code: str, trade_date: date) -> Optional[DailyIndicator]:
        """
        查询指定股票在指定日期的指标数据
        
        Args:
            ts_code: 股票代码
            trade_date: 交易日期
            
        Returns:
            DailyIndicator对象，如果未找到返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM daily_indicators WHERE ts_code = ? AND trade_date = ?',
                (ts_code, trade_date.isoformat())
            )
            row = cursor.fetchone()
            return self._row_to_indicator(row) if row else None
    
    def find_by_code(self, ts_code: str) -> List[DailyIndicator]:
        """
        查询指定股票的所有指标数据
        
        Args:
            ts_code: 股票代码
            
        Returns:
            DailyIndicator对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM daily_indicators WHERE ts_code = ? ORDER BY trade_date',
                (ts_code,)
            )
            return [self._row_to_indicator(row) for row in cursor.fetchall()]
    
    def find_by_date(self, trade_date: date) -> List[DailyIndicator]:
        """
        查询指定日期的所有股票指标数据
        
        Args:
            trade_date: 交易日期
            
        Returns:
            DailyIndicator对象列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM daily_indicators WHERE trade_date = ? ORDER BY ts_code',
                (trade_date.isoformat(),)
            )
            return [self._row_to_indicator(row) for row in cursor.fetchall()]
    
    def _row_to_indicator(self, row: tuple) -> DailyIndicator:
        """将数据库行转换为DailyIndicator对象"""
        return DailyIndicator(
            ts_code=row[0],
            trade_date=datetime.fromisoformat(row[1]).date(),
            close=Decimal(str(row[2])),
            turnover_rate=Decimal(str(row[3])),
            turnover_rate_f=Decimal(str(row[4])),
            volume_ratio=Decimal(str(row[5])),
            pe=Decimal(str(row[6])),
            pe_ttm=Decimal(str(row[7])),
            pb=Decimal(str(row[8])),
            ps=Decimal(str(row[9])),
            ps_ttm=Decimal(str(row[10])),
            dv_ratio=Decimal(str(row[11])),
            dv_ttm=Decimal(str(row[12])),
            total_share=Decimal(str(row[13])),
            float_share=Decimal(str(row[14])),
            free_share=Decimal(str(row[15])),
            total_mv=Decimal(str(row[16])),
            circ_mv=Decimal(str(row[17]))
        )