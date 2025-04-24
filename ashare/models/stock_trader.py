import time
from typing import List
from decimal import Decimal
from enum import Enum
from datetime import date

from pandas.tseries.offsets import YearBegin

from ashare.tests.test_stock_repository import repo
from .financial_report import FinancialReport
from .daily_indicator import DailyIndicator
from .daily_quote import DailyQuote
from .dividend import Dividend
from datetime import timedelta
import logging
from ashare.logger.setup_logger import get_logger

class TradeAction(Enum):
    """交易动作枚举"""
    BUY = "买入"
    SELL = "卖出"
    HOLD = "持有"
    
class TradeActionResult:
    """交易决策结果"""
    def __init__(self, action: TradeAction, roe_debug_info: str, dcf_ratio_debug_info: str):
        self.action = action
        self.roe_debug_info = roe_debug_info
        self.dcf_ratio_debug_info = dcf_ratio_debug_info

class StockTrader:
    """股票交易决策类"""
    
    def __init__(self, 
                 daily_indicators: List[DailyIndicator],
                 daily_quotes: List[DailyQuote],
                 dividends: List[Dividend],
                 financial_reports: List[FinancialReport],
                 target_date: date,
                 discount_rate: float = 0.05,  # 折现率默认5%
                 risk_free_rate: float = 0.05):  # 无风险收益率默认3%
        # 筛选目标日期之前的数据
        self.target_date = target_date
        self.daily_indicators = sorted(
            [ind for ind in daily_indicators if ind.trade_date <= target_date],
            key=lambda x: x.trade_date, 
            reverse=True
        )
        self.daily_quotes = sorted(
            [quote for quote in daily_quotes if quote.trade_date <= target_date],
            key=lambda x: x.trade_date, 
            reverse=True
        )
        self.dividends = sorted(
            [div for div in dividends if div.ann_date and div.ann_date <= target_date],
            key=lambda x: x.ann_date, 
            reverse=True
        )
        self.financial_reports = sorted(
            [report for report in financial_reports if report.report_date <= target_date and report.ann_date < target_date and report.end_type=="4" and report.financial_indicators and report.income_statement and report.cash_flow_statement],
            key=lambda x: x.report_date, 
            reverse=True
        )
        self.discount_rate = discount_rate
        self.risk_free_rate = risk_free_rate
        self.logger = get_logger()
        self.logger.info("初始化 StockTrader")
        self.dcf_ratio_debug_info = ''
        self.roe_debug_info = ''

    def _check_roe_condition(self) -> bool:
        """检查ROE条件"""
        # 获取最近5个年报
        annual_reports = [
            report for report in self.financial_reports
            if report.end_type == "4"
        ][:5]
        
        if len(annual_reports) < 5:
            self.roe_debug_info = f"财报数据不满5年"
            return False
        
        # 打印每个年报的ROE
        self.logger.info(f"ROE: {[report.financial_indicators.roe for report in annual_reports]}")
            
        # 检查ROE是否都大于20%
        roe_condition = all(
            report.financial_indicators.roe and report.financial_indicators.roe >= Decimal('15.0')
            for report in annual_reports
        )
        if not roe_condition:
            self.roe_debug_info = f"不满足最近五年ROE>=20%"
            return False
        else:
            self.roe_debug_info = f"满足最近五年ROE>=20%"
        
        return roe_condition

    def _check_pe_percentile(self) -> float:
        """计算当前PE在历史分位数的位置"""
        if not self.daily_indicators:
            return 1.0
            
        # 获取最近5年的PE数据
        # five_years_ago = self.target_date.replace(year=self.target_date.year - 5)
        # TODO
        five_years_ago = self.target_date - timedelta(days=5*365)
        historical_pe = [
            ind.pe for ind in self.daily_indicators
            if ind.trade_date >= five_years_ago and ind.pe and ind.pe > 0
        ]
        
        if not historical_pe:
            return 1.0
        
        # 打印PE数据
        # self.logger.info(f"PE: {[ind.pe for ind in self.daily_indicators]}")

        current_pe = self.daily_indicators[0].pe
        if not current_pe:
            return 1.0
        pe_below_current = sum(1 for pe in historical_pe if pe <= current_pe)
        
        pe_percentile = pe_below_current / len(historical_pe)
        # print(f"target_date={self.target_date}, Current PE: {current_pe}, PE percentile: {pe_percentile}")
        
        return pe_percentile

    def _calculate_growth_rate(self, historical_fcff: List[float]) -> float:
        """计算历史现金流增长率，剔除异常值
        
        Args:
            historical_fcff: 按时间倒序排列的历史现金流数据
            
        Returns:
            float: 计算得出的增长率，如果无法计算则返回0
        """
        growth_rates = []
        for i in range(len(historical_fcff)-1):
            if historical_fcff[i+1] > 0:  # 避免除以0
                rate = (historical_fcff[i] / historical_fcff[i+1]) - 1
                growth_rates.append(rate)
                
        if not growth_rates:
            return 0.0
            
        # 计算增长率的均值和标准差
        mean = sum(growth_rates) / len(growth_rates)
        std = (sum((x - mean) ** 2 for x in growth_rates) / len(growth_rates)) ** 0.5
        
        # 剔除超过2个标准差的异常值
        normal_rates = [x for x in growth_rates if abs(x - mean) <= 2 * std]
        
        if not normal_rates:
            return mean
        
        # 使用正常值计算平均增长率
        avg_growth_rate = sum(normal_rates) / len(normal_rates)
        
        self.logger.info(f"原始增长率: {growth_rates}, 均值: {mean:.2%}, 标准差: {std:.2%}")
        self.logger.info(f"剔除异常后增长率: {normal_rates}, 平均增长率: {avg_growth_rate:.2%}")

        return avg_growth_rate

    def _calculate_growth_increment(self, historical_fcff: List[float]) -> float:
        """计算历史现金流平均增长量，剔除异常值
        
        Args:
            historical_fcff: 按时间倒序排列的历史现金流数据
            
        Returns:
            float: 计算得出的平均增长量，如果无法计算则返回0
        """
        if len(historical_fcff) < 2:
            return 0.0
            
        # 计算每年的增长量
        increments = []
        for i in range(len(historical_fcff)-1):
            increment = historical_fcff[i] - historical_fcff[i+1]
            increments.append(increment)
            
        if not increments:
            return 0.0
        
        # 计算增长量的均值和标准差
        mean = sum(increments) / len(increments)
        std = (sum((x - mean) ** 2 for x in increments) / len(increments)) ** 0.5
        
        # 剔除超过2个标准差的异常值
        normal_increments = [x for x in increments if abs(x - mean) <= 2 * std]
        
        if not normal_increments:
            return mean
        
        # 使用正常值计算平均增长量
        avg_increment = sum(normal_increments) / len(normal_increments)
        
        self.logger.info(f"原始增长量: {increments}, 均值: {mean:.2f}, 标准差: {std:.2f}")
        self.logger.info(f"剔除异常后增长量: {normal_increments}, 平均增长量: {avg_increment:.2f}")
            
        return avg_increment
    
    def _predict_future_fcff(self, historical_fcff: List[float], n_years: int = 3) -> List[float]:
        """使用线性规划预测未来现金流
        
        Args:
            historical_fcff: 按时间倒序排列的历史现金流数据
            n_years: 预测年数
            
        Returns:
            List[float]: 预测的未来现金流列表
        """
        if len(historical_fcff) < 2:
            return [historical_fcff[0]] * n_years if historical_fcff else [0] * n_years
            
        import numpy as np
        from sklearn.linear_model import LinearRegression
        
        # 准备训练数据
        X = np.array(range(len(historical_fcff))).reshape(-1, 1)
        y = np.array(historical_fcff[::-1])  # 转换为时间正序
        
        # 训练线性回归模型
        model = LinearRegression()
        model.fit(X, y)
        
        # 预测未来n年
        future_years = np.array(range(len(historical_fcff), len(historical_fcff) + n_years)).reshape(-1, 1)
        predictions = model.predict(future_years)
        
        # 计算模型评估指标
        r2_score = model.score(X, y)
        
        self.logger.info(f"线性回归系数: {model.coef_[0]:.2f}, 截距: {model.intercept_:.2f}")
        self.logger.info(f"模型拟合度 R²: {r2_score:.4f}")
        self.logger.info(f"未来{n_years}年现金流预测: {predictions.tolist()}")
        
        return predictions.tolist()

    def _calculate_dcf_ratio(self) -> float:
        """计算DCF估值与当前市值的比率"""
        self.dcf_ratio_debug_info = ''
        if not self.financial_reports or not self.daily_quotes:
            self.dcf_ratio_debug_info = "无财报数据或者无每日指票数据:dcf_ratio=1.0"
            self.logger.info("No financial reports or daily quotes found, dcf_ratio=1.0")
            return 1.0
            
        # 获取最近的财务数据
        latest_report = self.financial_reports[0]
        latest_indicator = self.daily_indicators[0]
        
        if not latest_report.income_statement:
            self.dcf_ratio_debug_info = "无利润表数据:dcf_ratio=1.0"
            self.logger.info("No income statement found, dcf_ratio=1.0")
            return 1.0
        
        income_item_name = '净利润(不含少数股东损益)'
        # 使用自由现金流进行估值
        if not latest_report.income_statement.get(income_item_name):
            self.dcf_ratio_debug_info = f"无利润表数据项 {income_item_name}:dcf_ratio=1.0"
            self.logger.info(f"No income statement item {income_item_name} found, dcf_ratio=1.0")
            return 1.0

        # 获取历史现金流数据
        historical_fcff = []
        for report in self.financial_reports:
            fcff = report.calculate_fcff()
            historical_fcff.append(float(fcff if fcff else 0))
            if len(historical_fcff) >= 5:  # 只取最近5年数据
                break
                
        if len(historical_fcff) < 2:  # 至少需要2个数据点才能计算增长率
            self.dcf_ratio_debug_info = "无足够的现流金历史数据|dcf_ratio=1.0"
            self.logger.info("Not enough historical data, dcf_ratio=1.0")
            return 1.0
            
        # 打印historical_fcff
        self.logger.info(f"Historical FCFF: {historical_fcff}")
        
        # 计算增长率和增长量
        growth_rate = self._calculate_growth_rate(historical_fcff) / 2
        # growth_increment = self._calculate_growth_increment(historical_fcff)
        
        fcff = float(latest_report.calculate_fcff())
        # 计算未来3年的现金流
        kYearCount = 3
        present_value = 0
        for i in range(1, kYearCount):
            future_cf = fcff * (1 + growth_rate) ** i
            present_value += future_cf / ((1 + self.discount_rate) ** i)
        future_cf = fcff * (1 + growth_rate) ** 3
        terminal_value_pv = future_cf / self.risk_free_rate / (1 + self.discount_rate) ** kYearCount
        
        # 计算未来现金流现值（使用增长量）
        # kYearCount = 3
        # present_value = 0
        # for i in range(1, kYearCount):
        #     future_cf = fcff + growth_increment * i  # 使用增长量而不是增长率
        #     present_value += future_cf / ((1 + self.discount_rate) ** i)
        
        # # 永续增长期使用增长量
        # terminal_value = fcff + growth_increment * kYearCount
        # terminal_value_pv = terminal_value / self.risk_free_rate / ((1 + self.discount_rate) ** kYearCount)
        
        # 计算未来5年现金流现值
        # kYearCount = 3
        # predicate_fcff_list = self._predict_future_fcff(historical_fcff, n_years=kYearCount)
        # present_value = 0
        # for i in range(1, kYearCount):
        #     future_cf = predicate_fcff_list[i-1]
        #     present_value += future_cf / ((1 + self.discount_rate) ** i)
        
        # terminal_value_pv = predicate_fcff_list[-1] / self.risk_free_rate / (1 + self.discount_rate) ** kYearCount
        
        total_value = present_value + terminal_value_pv
        current_market_value = float(latest_indicator.total_mv * 10000) # 万元转为元
        if total_value <= 0:
            return 1.0
        ratio = current_market_value / total_value
        self.logger.info(f"fcff: {fcff:,.2f}, growth_rate: {growth_rate:.2%} risk_free_rate={self.risk_free_rate:.2%}, discount_rate={self.discount_rate:.2%}, present_value: {present_value:,.2f}, terminal_value_pv: {terminal_value_pv:,.2f}, current_market_value={current_market_value:,.2f}, total_value: {total_value:,.2f}, ratio: {ratio:.2f}")
        # self.dcf_ratio_debug_info += f"fcff={fcff:.2f}|growth_rate={growth_rate:.2f}|growth_increment={growth_increment:.2f}|risk_free_rate={self.risk_free_rate:.2f}|discount_rate={self.discount_rate:.2f}|present_value={present_value:.2f}|terminal_value_pv={terminal_value_pv:.2f}|current_market_value={current_market_value:.2f}|total_value={total_value:.2f}|ratio={ratio:.2f}"
        # self.dcf_ratio_debug_info += f"predicate_fcff_list={predicate_fcff_list[0]}|{predicate_fcff_list[1]}|{predicate_fcff_list[2]}|risk_free_rate={self.risk_free_rate:.2f}|discount_rate={self.discount_rate:.2f}|present_value={present_value:.2f}|terminal_value_pv={terminal_value_pv:.2f}|current_market_value={current_market_value:.2f}|total_value={total_value:.2f}|ratio={ratio:.2f}"
        return ratio

    def get_action(self) -> TradeActionResult:
        """获取交易决策"""
        # 计算各个指标
        roe_qualified = self._check_roe_condition()
        pe_percentile = self._check_pe_percentile()
        dcf_ratio = self._calculate_dcf_ratio()
        
        # 打印指标
        self.logger.info(f"ROE条件: {roe_qualified}")
        self.logger.info(f"PE分位数: {pe_percentile}")
        self.logger.info(f"市值 / DCF估值: {dcf_ratio}")
        
        # 买入条件
        if (roe_qualified and 
            # pe_percentile <= 0.15 and
            dcf_ratio <= 0.5):
            self.logger.info(f"日期：{self.target_date}, 买入")
            return TradeActionResult(TradeAction.BUY, self.roe_debug_info, self.dcf_ratio_debug_info)
            
        # 卖出条件
        if (not roe_qualified
            # pe_percentile >= 0.85
            or dcf_ratio >= 1.3):  # dcf_ratio <= 0.8 相当于 1/dcf_ratio >= 1.2
            self.logger.info(f"日期：{self.target_date}, 卖出")
            return TradeActionResult(TradeAction.SELL, self.roe_debug_info, self.dcf_ratio_debug_info)
            
        # 其他情况持有
        self.logger.info(f"日期：{self.target_date}, 观望")
        return TradeActionResult(TradeAction.HOLD, self.roe_debug_info, self.dcf_ratio_debug_info)
