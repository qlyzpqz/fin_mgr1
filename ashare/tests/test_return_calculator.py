from datetime import date
from decimal import Decimal
import pytest
from ashare.models.return_calculator import ReturnCalculator
from ashare.models.trade_record import TradeRecord
from ashare.models.daily_quote import DailyQuote
from ashare.models.dividend import Dividend

class TestReturnCalculator:
    @pytest.fixture
    def sample_trades(self):
        """样例交易记录"""
        return [
            TradeRecord(
                ts_code='000001.SZ',
                trade_date=date(2022, 1, 4),
                trade_price=Decimal('10.0'),
                trade_shares=Decimal('1000'),
                trade_type='buy',
                trade_amount=Decimal('10000'),
                commission=Decimal('5'),
                tax=Decimal('0')
            ),
            TradeRecord(
                ts_code='000001.SZ',
                trade_date=date(2022, 6, 30),
                trade_price=Decimal('12.0'),
                trade_shares=Decimal('500'),
                trade_type='sell',
                trade_amount=Decimal('6000'),
                commission=Decimal('3'),
                tax=Decimal('6')
            )
        ]

    @pytest.fixture
    def sample_quotes(self):
        """样例行情数据"""
        return [
            DailyQuote(
                ts_code='000001.SZ',
                trade_date=date(2022, 1, 4),
                open=Decimal('10.0'),
                high=Decimal('10.2'),
                low=Decimal('9.8'),
                close=Decimal('10.0'),
                pre_close=Decimal('9.9'),
                change=Decimal('0.1'),
                pct_chg=Decimal('1.01'),
                vol=Decimal('100000'),
                amount=Decimal('1000000')
            ),
            DailyQuote(
                ts_code='000001.SZ',
                trade_date=date(2022, 6, 30),
                open=Decimal('11.8'),
                high=Decimal('12.1'),
                low=Decimal('11.7'),
                close=Decimal('12.0'),
                pre_close=Decimal('11.9'),
                change=Decimal('0.1'),
                pct_chg=Decimal('0.84'),
                vol=Decimal('80000'),
                amount=Decimal('950000')
            )
        ]

    @pytest.fixture
    def sample_dividends(self):
        """样例分红数据"""
        return [
            Dividend(
                ts_code='000001.SZ',
                end_date=date(2022, 12, 31),
                ann_date=date(2022, 4, 1),
                div_proc='实施',
                stk_div=Decimal('0'),
                stk_bo_rate=Decimal('0.2'),  # 每10股送2股
                stk_co_rate=Decimal('0.3'),  # 每10股转增3股
                cash_div=Decimal('0.5'),     # 每10股派5元
                cash_div_tax=Decimal('0.5'),
                record_date=date(2022, 4, 15),
                ex_date=date(2022, 4, 16),
                pay_date=date(2022, 4, 20),
                div_listdate=date(2022, 4, 21),
                imp_ann_date=date(2022, 4, 14),
                base_date=date(2022, 4, 15),
                base_share=Decimal('10000')
            )
        ]

    def test_calculate_position_shares(self, sample_trades, sample_quotes, sample_dividends):
        """测试持仓数量计算"""
        calculator = ReturnCalculator(sample_trades, sample_quotes, sample_dividends)
        
        # 买入后、除权前的持仓
        shares = calculator.calculate_position_shares(date(2022, 4, 15))
        assert shares == Decimal('1000')
        
        # 除权后的持仓
        shares = calculator.calculate_position_shares(date(2022, 4, 16))
        assert shares == Decimal('1560')  # 1000 * 1.2 * 1.3
        
        # 卖出后的持仓
        shares = calculator.calculate_position_shares(date(2022, 6, 30))
        assert shares == Decimal('1060')  # 1560 - 500

    def test_calculate_annualized_return(self, sample_trades, sample_quotes, sample_dividends):
        """测试年化收益率计算"""
        calculator = ReturnCalculator(sample_trades, sample_quotes, sample_dividends)
        
        # 计算到卖出日期的收益率
        rate = calculator.calculate_annualized_return(date(2022, 6, 30))
        assert isinstance(rate, Decimal)
        assert rate > Decimal('0')  # 由于有分红和股价上涨，收益率应为正

    def test_empty_trades(self):
        """测试空交易记录"""
        calculator = ReturnCalculator([], [], [])
        assert calculator.calculate_annualized_return() == Decimal('0')

    def test_invalid_evaluation_date(self, sample_trades, sample_quotes, sample_dividends):
        """测试无效的评估日期"""
        calculator = ReturnCalculator(sample_trades, sample_quotes, sample_dividends)
        
        with pytest.raises(ValueError):
            calculator.calculate_annualized_return(date(2030, 1, 1))  # 日期无行情数据

    def test_get_cash_flows(self, sample_trades, sample_quotes, sample_dividends):
        """测试现金流计算"""
        calculator = ReturnCalculator(sample_trades, sample_quotes, sample_dividends)
        
        # 获取到最后一个交易日的现金流
        cash_flows = calculator._get_cash_flows_with_final_value(date(2022, 6, 30))
        
        # 检查现金流列表基本属性
        assert isinstance(cash_flows, list)
        assert len(cash_flows) == 4  # 买入、分红、卖出、最终市值
        
        # 检查现金流按日期排序
        dates = [cf[0] for cf in cash_flows]
        assert dates == sorted(dates)
        
        # 检查买入现金流（第一笔）
        assert cash_flows[0][0] == date(2022, 1, 4)  # 买入日期
        buy_amount = -(Decimal('10000') + Decimal('5') + Decimal('0'))  # 买入金额+手续费+税费
        assert cash_flows[0][1] == buy_amount
        
        # 检查分红现金流（第二笔）
        assert cash_flows[1][0] == date(2022, 4, 20)  # 派息日
        dividend_amount = Decimal('1000') * Decimal('0.5')  # 持股数 * 每股分红
        assert cash_flows[1][1] == dividend_amount
        
        # 检查卖现现金流（第三笔）
        assert cash_flows[2][0] == date(2022, 6, 30)  # 卖出日期
        sell_amount = Decimal('6000') - Decimal('3') - Decimal('6')  # 卖出金额-手续费-税费
        assert cash_flows[2][1] == sell_amount
        
        # 检查最终市值现金流（第四笔）
        assert cash_flows[3][0] == date(2022, 6, 30)  # 评估日期
        final_shares = Decimal('1060')  # 最终持仓
        final_value = final_shares * Decimal('12.0')  # 持仓数 * 收盘价
        assert cash_flows[3][1] == final_value

    def test_get_cash_flows_empty_position(self, sample_trades, sample_quotes, sample_dividends):
        """测试空仓时的现金流计算"""
        # 创建一个全部卖出的交易记录
        trades = [
            TradeRecord(
                ts_code='000001.SZ',
                trade_date=date(2022, 1, 4),
                trade_price=Decimal('10.0'),
                trade_shares=Decimal('1000'),
                trade_type='buy',
                trade_amount=Decimal('10000'),
                commission=Decimal('5'),
                tax=Decimal('0')
            ),
            TradeRecord(
                ts_code='000001.SZ',
                trade_date=date(2022, 1, 5),
                trade_price=Decimal('11.0'),
                trade_shares=Decimal('1000'),
                trade_type='sell',
                trade_amount=Decimal('11000'),
                commission=Decimal('5.5'),
                tax=Decimal('11')
            )
        ]
        
        calculator = ReturnCalculator(trades, sample_quotes, [])
        cash_flows = calculator.get_cash_flows(date(2022, 6, 30))
        
        # 应该只有买入和卖出两笔现金流
        assert len(cash_flows) == 2
        assert cash_flows[0][1] < Decimal('0')  # 买入为负
        assert cash_flows[1][1] > Decimal('0')  # 卖出为正

    def test_get_cash_flows_before_trades(self, sample_trades, sample_quotes, sample_dividends):
        """测试早于交易的日期"""
        calculator = ReturnCalculator(sample_trades, sample_quotes, sample_dividends)
        cash_flows = calculator.get_cash_flows(date(2022, 1, 3))
        
        # 不应该有任何现金流
        assert len(cash_flows) == 0

    def test_xirr_simple_case(self):
        """测试简单情况下的XIRR计算"""
        calculator = ReturnCalculator([], [], [])
        
        # 投资10000，一年后获得11000
        cash_flows = [
            (date(2022, 1, 1), Decimal('-10000')),
            (date(2023, 1, 1), Decimal('11000'))
        ]
        
        rate = calculator._xirr(cash_flows)
        print("\ntest_xirr_simple_case.rate=", rate, "\n")
        assert abs(rate - Decimal('0.1')) < Decimal('0.001')  # 应该接近10%

    def test_xirr_multiple_flows(self):
        """测试多笔现金流的XIRR计算"""
        calculator = ReturnCalculator([], [], [])
        
        # 模拟定投场景
        cash_flows = [
            (date(2022, 1, 1), Decimal('-1000')),   # 首次投资
            (date(2022, 4, 1), Decimal('-1000')),   # 第二次投资
            (date(2022, 7, 1), Decimal('-1000')),   # 第三次投资
            (date(2022, 10, 1), Decimal('-1000')),  # 第四次投资
            (date(2023, 1, 1), Decimal('4400'))     # 最终价值
        ]
        
        rate = calculator._xirr(cash_flows)
        print("\ntest_xirr_multiple_flows.rate=", rate, "\n")
        assert rate > Decimal('0')  # 收益率应该为正
        assert rate < Decimal('0.2')  # 收益率应该合理

    def test_xirr_with_dividend(self):
        """测试带分红的XIRR计算"""
        calculator = ReturnCalculator([], [], [])
        
        cash_flows = [
            (date(2022, 1, 1), Decimal('-10000')),  # 买入
            (date(2022, 7, 1), Decimal('300')),     # 分红
            (date(2023, 1, 1), Decimal('10500'))    # 最终价值
        ]
        
        rate = calculator._xirr(cash_flows)
        assert rate > Decimal('0.07')  # 考虑分红后收益率应该高于7%
        assert rate < Decimal('0.09')  # 收益率应该合理

    def test_xirr_empty_flows(self):
        """测试空现金流"""
        calculator = ReturnCalculator([], [], [])
        assert calculator._xirr([]) == Decimal('0')

    def test_xirr_single_flow(self):
        """测试单笔现金流"""
        calculator = ReturnCalculator([], [], [])
        cash_flows = [(date(2022, 1, 1), Decimal('-1000'))]
        assert calculator._xirr(cash_flows) == Decimal('0')

    def test_xirr_negative_return(self):
        """测试亏损情况的XIRR计算"""
        calculator = ReturnCalculator([], [], [])
        
        cash_flows = [
            (date(2022, 1, 1), Decimal('-10000')),  # 买入
            (date(2023, 1, 1), Decimal('9000'))     # 亏损卖出
        ]
        
        rate = calculator._xirr(cash_flows)
        assert rate < Decimal('0')  # 收益率应该为负
        assert abs(rate - Decimal('-0.1')) < Decimal('0.001')  # 应该接近-10%