import sqlite3
from typing import List, Optional
from datetime import date
from .financial_report import (
    FinancialReport,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    FinancialIndicators
)

class FinancialReportRepository:
    """财务报告仓库类"""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS financial_reports (
                    ts_code TEXT NOT NULL,
                    report_date DATE NOT NULL,
                    ann_date DATE,
                    report_type TEXT NOT NULL,
                    end_type TEXT NOT NULL,
                    income_statement TEXT,
                    balance_sheet TEXT,
                    cash_flow_statement TEXT,
                    financial_indicators TEXT,
                    PRIMARY KEY (ts_code, report_date, report_type)
                )
            ''')

    def save(self, report: FinancialReport) -> None:
        """保存财务报告"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO financial_reports (
                    ts_code, report_date, ann_date, report_type, end_type,
                    income_statement, balance_sheet,
                    cash_flow_statement, financial_indicators
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.ts_code,
                report.report_date.isoformat(),
                report.ann_date.isoformat() if report.ann_date else None,
                report.report_type,
                report.end_type,
                report.income_statement.to_json() if report.income_statement else None,
                report.balance_sheet.to_json() if report.balance_sheet else None,
                report.cash_flow_statement.to_json() if report.cash_flow_statement else None,
                report.financial_indicators.to_json() if report.financial_indicators else None
            ))

    def save_many(self, reports: List[FinancialReport]) -> None:
        """批量保存财务报告"""
        with sqlite3.connect(self.db_path) as conn:
            for report in reports:
                conn.execute('''
                    INSERT OR REPLACE INTO financial_reports (
                        ts_code, report_date, ann_date, report_type, end_type,
                        income_statement, balance_sheet,
                        cash_flow_statement, financial_indicators
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    report.ts_code,
                    report.report_date.isoformat(),
                    report.ann_date.isoformat() if report.ann_date else None,
                    report.report_type,
                    report.end_type,
                    report.income_statement.to_json() if report.income_statement else None,
                    report.balance_sheet.to_json() if report.balance_sheet else None,
                    report.cash_flow_statement.to_json() if report.cash_flow_statement else None,
                    report.financial_indicators.to_json() if report.financial_indicators else None
                ))
            conn.commit()

    def get(self, ts_code: str, report_date: date, report_type: str) -> Optional[FinancialReport]:
        """获取财务报告"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT ts_code, report_date, ann_date, report_type, end_type,
                       income_statement, balance_sheet, cash_flow_statement, 
                       financial_indicators
                FROM financial_reports 
                WHERE ts_code = ? AND report_date = ? AND report_type = ?
            ''', (ts_code, report_date.isoformat(), report_type))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            return FinancialReport(
                ts_code=row[0],
                report_date=date.fromisoformat(row[1]),
                ann_date=date.fromisoformat(row[2]) if row[2] else None,
                report_type=row[3],
                end_type=row[4],
                income_statement=IncomeStatement.from_json(row[5]) if row[5] else None,
                balance_sheet=BalanceSheet.from_json(row[6]) if row[6] else None,
                cash_flow_statement=CashFlowStatement.from_json(row[7]) if row[7] else None,
                financial_indicators=FinancialIndicators.from_json(row[8]) if row[8] else None
            )
    
    def get_all(self, ts_code: str) -> List[FinancialReport]:
        """获取指定股票代码的所有财务报告"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT ts_code, report_date, ann_date, report_type, end_type,
                       income_statement, balance_sheet, cash_flow_statement, 
                       financial_indicators 
                FROM financial_reports 
                WHERE ts_code = ?''', (ts_code,))
            return [
                FinancialReport(
                    ts_code=row[0],
                    report_date=date.fromisoformat(row[1]),
                    ann_date=date.fromisoformat(row[2]) if row[2] else None,
                    report_type=row[3],
                    end_type=row[4],
                    income_statement=IncomeStatement.from_json(row[5]) if row[5] else None,
                    balance_sheet=BalanceSheet.from_json(row[6]) if row[6] else None,
                    cash_flow_statement=CashFlowStatement.from_json(row[7]) if row[7] else None,
                    financial_indicators=FinancialIndicators.from_json(row[8]) if row[8] else None
                )
                for row in cursor.fetchall()
            ]
    
    def delete(self, ts_code: str, report_date: date, report_type: str) -> bool:
        """删除财务报告"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM financial_reports 
                WHERE ts_code = ? AND report_date = ? AND report_type = ?
            ''', (ts_code, report_date.isoformat(), report_type))
            return cursor.rowcount > 0