from datetime import date, timedelta
from decimal import Decimal
import pytest
from ashare.models.stock_trader import StockTrader, TradeAction
from ashare.models.daily_indicator import DailyIndicator
from ashare.models.daily_quote import DailyQuote
from ashare.models.dividend import Dividend
from ashare.models.financial_report import FinancialReport, FinancialIndicators

@pytest.fixture
def base_date():
    return date(2023, 1, 1)

@pytest.fixture
def sample_financial_reports(base_date):
    reports = []
    for i in range(5):
        report_date = base_date - timedelta(days=365 * i)
        indicators = FinancialIndicators(
            opincome_of_ebt=Decimal('0.8'),
            investincome_of_ebt=Decimal('0.1'),
            n_op_profit_of_ebt=Decimal('0.1'),
            tax_to_ebt=Decimal('0.25'),
            dtprofit_to_profit=Decimal('0.95'),
            salescash_to_or=Decimal('0.9'),
            ocf_to_or=Decimal('0.2'),
            ocf_to_opincome=Decimal('0.8'),
            capitalized_to_da=Decimal('0.3'),
            debt_to_assets=Decimal('0.5'),
            assets_to_eqt=Decimal('2.0'),
            dp_assets_to_eqt=Decimal('1.8'),
            ca_to_assets=Decimal('0.4'),
            nca_to_assets=Decimal('0.6'),
            tbassets_to_totalassets=Decimal('0.7'),
            int_to_talcap=Decimal('0.05'),
            eqt_to_talcapital=Decimal('0.5'),
            currentdebt_to_debt=Decimal('0.3'),
            longdeb_to_debt=Decimal('0.7'),
            ocf_to_shortdebt=Decimal('1.2'),
            debt_to_eqt=Decimal('1.0'),
            eqt_to_debt=Decimal('1.0'),
            eqt_to_interestdebt=Decimal('1.2'),
            tangibleasset_to_debt=Decimal('1.5'),
            tangasset_to_intdebt=Decimal('1.6'),
            tangibleasset_to_netdebt=Decimal('2.0'),
            ocf_to_debt=Decimal('0.3'),
            ocf_to_interestdebt=Decimal('0.35'),
            ocf_to_netdebt=Decimal('0.4'),
            ebit_to_interest=Decimal('5.0'),
            longdebt_to_workingcapital=Decimal('0.8'),
            ebitda_to_debt=Decimal('0.4'),
            turn_days=Decimal('105'),
            roa_yearly=Decimal('0.08'),
            roa_dp=Decimal('0.07'),
            fixed_assets=Decimal('3000000000'),
            profit_prefin_exp=Decimal('1900000000'),
            non_op_profit=Decimal('100000000'),
            op_to_ebt=Decimal('0.8'),
            nop_to_ebt=Decimal('0.2'),
            ocf_to_profit=Decimal('1.1'),
            cash_to_liqdebt=Decimal('0.6'),
            cash_to_liqdebt_withinterest=Decimal('0.5'),
            op_to_liqdebt=Decimal('1.2'),
            op_to_debt=Decimal('0.4'),
            roic_yearly=Decimal('0.1'),
            total_fa_trun=Decimal('0.8'),
            profit_to_op=Decimal('0.75'),
            q_opincome=Decimal('500000000'),
            q_investincome=Decimal('50000000'),
            q_dtprofit=Decimal('450000000'),
            q_eps=Decimal('0.25'),
            q_netprofit_margin=Decimal('0.15'),
            q_gsprofit_margin=Decimal('0.3'),
            q_exp_to_sales=Decimal('0.15'),
            q_profit_to_gr=Decimal('0.15'),
            q_saleexp_to_gr=Decimal('0.08'),
            q_adminexp_to_gr=Decimal('0.05'),
            q_finaexp_to_gr=Decimal('0.02'),
            q_impair_to_gr_ttm=Decimal('0.01'),
            q_gc_to_gr=Decimal('0.7'),
            q_op_to_gr=Decimal('0.2'),
            q_roe=Decimal('0.15'),
            q_dt_roe=Decimal('0.14'),
            q_npta=Decimal('0.07'),
            q_opincome_to_ebt=Decimal('0.8'),
            q_investincome_to_ebt=Decimal('0.1'),
            q_dtprofit_to_profit=Decimal('0.95'),
            q_salescash_to_or=Decimal('0.9'),
            q_ocf_to_sales=Decimal('0.2'),
            q_ocf_to_or=Decimal('0.2'),
            basic_eps_yoy=Decimal('0.1'),
            dt_eps_yoy=Decimal('0.1'),
            cfps_yoy=Decimal('0.15'),
            op_yoy=Decimal('0.2'),
            ebt_yoy=Decimal('0.18'),
            netprofit_yoy=Decimal('0.15'),
            dt_netprofit_yoy=Decimal('0.14'),
            ocf_yoy=Decimal('0.12'),
            roe_yoy=Decimal('0.02'),
            bps_yoy=Decimal('0.1'),
            assets_yoy=Decimal('0.15'),
            eqt_yoy=Decimal('0.12'),
            tr_yoy=Decimal('0.18'),
            or_yoy=Decimal('0.18'),
            q_gr_yoy=Decimal('0.18'),
            q_gr_qoq=Decimal('0.05'),
            q_sales_yoy=Decimal('0.18'),
            q_sales_qoq=Decimal('0.05'),
            q_op_yoy=Decimal('0.2'),
            q_op_qoq=Decimal('0.05'),
            q_profit_yoy=Decimal('0.15'),
            q_profit_qoq=Decimal('0.04'),
            q_netprofit_yoy=Decimal('0.15'),
            q_netprofit_qoq=Decimal('0.04'),
            equity_yoy=Decimal('0.12'),
            rd_exp=Decimal('100000000'),
            update_flag="1",
            ts_code='000001.SZ',
            ann_date=report_date,
            end_date=report_date,
            eps=Decimal('1.0'),
            dt_eps=Decimal('1.0'),
            total_revenue_ps=Decimal('10.0'),
            revenue_ps=Decimal('10.0'),
            capital_rese_ps=Decimal('2.0'),
            surplus_rese_ps=Decimal('1.0'),
            undist_profit_ps=Decimal('3.0'),
            extra_item=Decimal('0.0'),
            profit_dedt=Decimal('1000000000'),
            gross_margin=Decimal('0.3'),
            current_ratio=Decimal('2.0'),
            quick_ratio=Decimal('1.5'),
            cash_ratio=Decimal('0.5'),
            invturn_days=Decimal('60'),
            arturn_days=Decimal('45'),
            inv_turn=Decimal('6.0'),
            ar_turn=Decimal('8.0'),
            ca_turn=Decimal('2.0'),
            fa_turn=Decimal('1.5'),
            assets_turn=Decimal('0.8'),
            op_income=Decimal('2000000000'),
            valuechange_income=Decimal('0'),
            interst_income=Decimal('10000000'),
            daa=Decimal('100000000'),
            ebit=Decimal('1800000000'),
            ebitda=Decimal('2000000000'),
            fcff=Decimal('1500000000'),
            fcfe=Decimal('1300000000'),
            current_exint=Decimal('1000000000'),
            noncurrent_exint=Decimal('2000000000'),
            interestdebt=Decimal('1500000000'),
            netdebt=Decimal('1000000000'),
            tangible_asset=Decimal('5000000000'),
            working_capital=Decimal('2000000000'),
            networking_capital=Decimal('1500000000'),
            invest_capital=Decimal('4000000000'),
            retained_earnings=Decimal('2000000000'),
            diluted2_eps=Decimal('1.0'),
            bps=Decimal('5.0'),
            ocfps=Decimal('2.0'),
            retainedps=Decimal('2.0'),
            cfps=Decimal('2.0'),
            ebit_ps=Decimal('1.8'),
            fcff_ps=Decimal('1.5'),
            fcfe_ps=Decimal('1.3'),
            netprofit_margin=Decimal('0.15'),
            grossprofit_margin=Decimal('0.3'),
            cogs_of_sales=Decimal('0.7'),
            expense_of_sales=Decimal('0.15'),
            profit_to_gr=Decimal('0.15'),
            saleexp_to_gr=Decimal('0.08'),
            adminexp_of_gr=Decimal('0.05'),
            finaexp_of_gr=Decimal('0.02'),
            impai_ttm=Decimal('0.01'),
            gc_of_gr=Decimal('0.7'),
            op_of_gr=Decimal('0.2'),
            ebit_of_gr=Decimal('0.18'),
            roe=Decimal('15.0'),
            roe_waa=Decimal('15.0'),
            roe_dt=Decimal('15.0'),
            roa=Decimal('8.0'),
            npta=Decimal('7.0'),
            roic=Decimal('10.0'),
            roe_yearly=Decimal('15.0'),
            roa2_yearly=Decimal('8.0'),
            roe_avg=Decimal('15.0'),
        )
        report = FinancialReport(
            ts_code='000001.SZ',
            end_type='4',  # 年报
            income_statement={},  # 利润表
            balance_sheet={},  # 资产负债表
            cash_flow_statement={},  # 现金流量表
            report_date=report_date,
            report_type="1",  # 年报
            financial_indicators=indicators
        )
        reports.append(report)
    return reports

@pytest.fixture
def sample_daily_indicators(base_date):
    indicators = []
    for i in range(1000):  # 约4年的交易日数据
        trade_date = base_date - timedelta(days=i)
        indicator = DailyIndicator(
            trade_date=trade_date,
            ts_code='000001.SZ',
            close=Decimal('10.0'),
            turnover_rate=Decimal('2.0'),
            turnover_rate_f=Decimal('2.0'),
            volume_ratio=Decimal('1.0'),
            pe=Decimal('20.0'),
            pe_ttm=Decimal('20.0'),
            pb=Decimal('2.0'),
            ps=Decimal('2.0'),
            ps_ttm=Decimal('2.0'),
            dv_ratio=Decimal('2.0'),
            dv_ttm=Decimal('2.0'),
            total_share=Decimal('1000000000'),
            float_share=Decimal('800000000'),
            free_share=Decimal('700000000'),
            total_mv=Decimal('10000000000'),
            circ_mv=Decimal('8000000000')
        )
        indicators.append(indicator)
    return indicators

@pytest.fixture
def sample_daily_quotes(base_date):
    quotes = []
    quote = DailyQuote(
        trade_date=base_date,
        ts_code='000001.SZ',
        open=Decimal('10.0'),
        high=Decimal('10.5'),
        low=Decimal('9.8'),
        close=Decimal('10.2'),
        pre_close=Decimal('10.0'),
        change=Decimal('0.2'),
        pct_chg=Decimal('2.0'),
        vol=Decimal('1000000'),
        amount=Decimal('10200000'),
    )
    quotes.append(quote)
    return quotes

@pytest.fixture
def sample_dividends(base_date):
    dividends = []
    dividend = Dividend(
        ann_date=base_date,
        ts_code='000001.SZ',
        end_date=base_date,
        div_proc='实施',
        stk_div=Decimal('0'),
        stk_bo_rate=Decimal('0'),
        stk_co_rate=Decimal('0'),
        cash_div=Decimal('1.0'),
        cash_div_tax=Decimal('1.0'),
        record_date=base_date,
        ex_date=base_date,
        pay_date=base_date,
        div_listdate=base_date,
        imp_ann_date=base_date,
        base_date=base_date,
        base_share=Decimal('1000000000')
    )
    dividends.append(dividend)
    return dividends

@pytest.fixture
def stock_trader(sample_daily_indicators, sample_daily_quotes, 
                sample_dividends, sample_financial_reports, base_date):
    return StockTrader(
        daily_indicators=sample_daily_indicators,
        daily_quotes=sample_daily_quotes,
        dividends=sample_dividends,
        financial_reports=sample_financial_reports,
        target_date=base_date
    )

def test_initialization(stock_trader, base_date):
    assert stock_trader.target_date == base_date
    assert len(stock_trader.financial_reports) > 0
    assert len(stock_trader.daily_indicators) > 0
    assert len(stock_trader.daily_quotes) > 0
    assert len(stock_trader.dividends) > 0

def test_check_roe_condition(stock_trader):
    assert stock_trader._check_roe_condition() is True

    # 测试ROE不达标的情况
    stock_trader.financial_reports[0].financial_indicators.roe = Decimal('14.0')
    assert stock_trader._check_roe_condition() is False

def test_check_pe_percentile(stock_trader):
    # 当前PE为20，设置历史PE使当前PE处于0.3分位
    for i, indicator in enumerate(stock_trader.daily_indicators):
        indicator.pe = 15.0 if i % 10 < 3 else 25.0
    
    percentile = stock_trader._check_pe_percentile()
    assert 0.29 <= percentile <= 0.31

def test_calculate_dcf_ratio(stock_trader):
    # 使用示例数据计算DCF比率
    ratio = stock_trader._calculate_dcf_ratio()
    assert ratio > 0

def test_get_action_buy(stock_trader):
    # 设置有利的买入条件
    # 1. ROE > 15%（已满足）
    # 2. PE处于低位
    for i, indicator in enumerate(stock_trader.daily_indicators):
        indicator.pe = 15.0 if i == 0 else 25.0
    
    # 3. DCF比率较高
    stock_trader.daily_quotes[0].total_mv = Decimal('10000000000')  # 降低市值使DCF比率提高
    
    assert stock_trader.get_action() == TradeAction.BUY

def test_get_action_sell(stock_trader):
    # 设置卖出条件
    # 1. ROE < 15%
    stock_trader.financial_reports[0].financial_indicators.roe = Decimal('14.0')
    
    assert stock_trader.get_action() == TradeAction.SELL

def test_get_action_hold(stock_trader):
    # 设置一般持有条件
    # PE在中位
    for i, indicator in enumerate(stock_trader.daily_indicators):
        if i < len(stock_trader.daily_indicators) * 0.5:
            indicator.pe = 20
        else:
            indicator.pe = 25
    
    assert stock_trader.get_action() == TradeAction.HOLD