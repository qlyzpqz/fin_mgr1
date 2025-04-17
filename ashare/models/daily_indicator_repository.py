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
    
    def _convert_float(self, value) -> Optional[float]:
        """
        将值转换为float类型，如果值为None则返回None
        
        Args:
            value: 要转换的值
            
        Returns:
            转换后的float值或None
        """
        return float(value) if value is not None else None
    
    def save_many(self, indicators: List[DailyIndicator]) -> None:
        """批量保存每日指标数据"""
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
                    self._convert_float(ind.close),
                    self._convert_float(ind.turnover_rate),
                    self._convert_float(ind.turnover_rate_f),
                    self._convert_float(ind.volume_ratio),
                    self._convert_float(ind.pe),
                    self._convert_float(ind.pe_ttm),
                    self._convert_float(ind.pb),
                    self._convert_float(ind.ps),
                    self._convert_float(ind.ps_ttm),
                    self._convert_float(ind.dv_ratio),
                    self._convert_float(ind.dv_ttm),
                    self._convert_float(ind.total_share),
                    self._convert_float(ind.float_share),
                    self._convert_float(ind.free_share),
                    self._convert_float(ind.total_mv),
                    self._convert_float(ind.circ_mv)
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
        def to_decimal(value) -> Optional[Decimal]:
            """将值转换为Decimal，处理None值的情况"""
            return Decimal(str(value)) if value is not None else None
            
        return DailyIndicator(
            ts_code=row[0],
            trade_date=datetime.fromisoformat(row[1]).date(),
            close=to_decimal(row[2]),
            turnover_rate=to_decimal(row[3]),
            turnover_rate_f=to_decimal(row[4]),
            volume_ratio=to_decimal(row[5]),
            pe=to_decimal(row[6]),
            pe_ttm=to_decimal(row[7]),
            pb=to_decimal(row[8]),
            ps=to_decimal(row[9]),
            ps_ttm=to_decimal(row[10]),
            dv_ratio=to_decimal(row[11]),
            dv_ttm=to_decimal(row[12]),
            total_share=to_decimal(row[13]),
            float_share=to_decimal(row[14]),
            free_share=to_decimal(row[15]),
            total_mv=to_decimal(row[16]),
            circ_mv=to_decimal(row[17])
        )