from dataclasses import dataclass, asdict
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
import json

@dataclass
class IncomeStatement:
    """利润表"""
    ts_code: str # TS代码
    ann_date: date # 公告日期
    f_ann_date: date # 实际公告日期
    end_date: date # 报告期
    report_type: str # 报告类型 见底部表
    comp_type: str # 公司类型(1一般工商业2银行3保险4证券)
    end_type: str # 报告期类型
    basic_eps: Decimal # 基本每股收益
    diluted_eps: Decimal # 稀释每股收益
    total_revenue: Decimal # 营业总收入
    revenue: Decimal # 营业收入
    int_income: Decimal # 利息收入
    prem_earned: Decimal # 已赚保费
    comm_income: Decimal # 手续费及佣金收入
    n_commis_income: Decimal # 手续费及佣金净收入
    n_oth_income: Decimal # 其他经营净收益
    n_oth_b_income: Decimal # 加:其他业务净收益
    prem_income: Decimal # 保险业务收入
    out_prem: Decimal # 减:分出保费
    une_prem_reser: Decimal # 提取未到期责任准备金
    reins_income: Decimal # 其中:分保费收入
    n_sec_tb_income: Decimal # 代理买卖证券业务净收入
    n_sec_uw_income: Decimal # 证券承销业务净收入
    n_asset_mg_income: Decimal # 受托客户资产管理业务净收入
    oth_b_income: Decimal # 其他业务收入
    fv_value_chg_gain: Decimal # 加:公允价值变动净收益
    invest_income: Decimal # 加:投资净收益
    ass_invest_income: Decimal # 其中:对联营企业和合营企业的投资收益
    forex_gain: Decimal # 加:汇兑净收益
    total_cogs: Decimal # 营业总成本
    oper_cost: Decimal # 减:营业成本
    int_exp: Decimal # 减:利息支出
    comm_exp: Decimal # 减:手续费及佣金支出
    biz_tax_surchg: Decimal # 减:营业税金及附加
    sell_exp: Decimal # 减:销售费用
    admin_exp: Decimal # 减:管理费用
    fin_exp: Decimal # 减:财务费用
    assets_impair_loss: Decimal # 减:资产减值损失
    prem_refund: Decimal # 退保金
    compens_payout: Decimal # 赔付总支出
    reser_insur_liab: Decimal # 提取保险责任准备金
    div_payt: Decimal # 保户红利支出
    reins_exp: Decimal # 分保费用
    oper_exp: Decimal # 营业支出
    compens_payout_refu: Decimal # 减:摊回赔付支出
    insur_reser_refu: Decimal # 减:摊回保险责任准备金
    reins_cost_refund: Decimal # 减:摊回分保费用
    other_bus_cost: Decimal # 其他业务成本
    operate_profit: Decimal # 营业利润
    non_oper_income: Decimal # 加:营业外收入
    non_oper_exp: Decimal # 减:营业外支出
    nca_disploss: Decimal # 其中:减:非流动资产处置净损失
    total_profit: Decimal # 利润总额
    income_tax: Decimal # 所得税费用
    n_income: Decimal # 净利润(含少数股东损益)
    n_income_attr_p: Decimal # 净利润(不含少数股东损益)
    minority_gain: Decimal # 少数股东损益
    oth_compr_income: Decimal # 其他综合收益
    t_compr_income: Decimal # 综合收益总额
    compr_inc_attr_p: Decimal # 归属于母公司(或股东)的综合收益总额
    compr_inc_attr_m_s: Decimal # 归属于少数股东的综合收益总额
    ebit: Decimal # 息税前利润
    ebitda: Decimal # 息税折旧摊销前利润
    insurance_exp: Decimal # 保险业务支出
    undist_profit: Decimal # 年初未分配利润
    distable_profit: Decimal # 可分配利润
    rd_exp: Decimal # 研发费用
    fin_exp_int_exp: Decimal # 财务费用:利息费用
    fin_exp_int_inc: Decimal # 财务费用:利息收入
    transfer_surplus_rese: Decimal # 盈余公积转入
    transfer_housing_imprest: Decimal # 住房周转金转入
    transfer_oth: Decimal # 其他转入
    adj_lossgain: Decimal # 调整以前年度损益
    withdra_legal_surplus: Decimal # 提取法定盈余公积
    withdra_legal_pubfund: Decimal # 提取法定公益金
    withdra_biz_devfund: Decimal # 提取企业发展基金
    withdra_rese_fund: Decimal # 提取储备基金
    withdra_oth_ersu: Decimal # 提取任意盈余公积金
    workers_welfare: Decimal # 职工奖金福利
    distr_profit_shrhder: Decimal # 可供股东分配的利润
    prfshare_payable_dvd: Decimal # 应付优先股股利
    comshare_payable_dvd: Decimal # 应付普通股股利
    capit_comstock_div: Decimal # 转作股本的普通股股利
    net_after_nr_lp_correct: Decimal # 扣除非经常性损益后的净利润（更正前）
    credit_impa_loss: Decimal # 信用减值损失
    net_expo_hedging_benefits: Decimal # 净敞口套期收益
    oth_impair_loss_assets: Decimal # 其他资产减值损失
    total_opcost: Decimal # 营业总成本（二）
    amodcost_fin_assets: Decimal # 以摊余成本计量的金融资产终止确认收益
    oth_income: Decimal # 其他收益
    asset_disp_income: Decimal # 资产处置收益
    continued_net_profit: Decimal # 持续经营净利润
    end_net_profit: Decimal # 终止经营净利润
    update_flag: str # 更新标识
    
    @classmethod
    def from_json(cls, json_str: str) -> 'IncomeStatement':
        """从JSON字符串创建利润表对象"""
        data = json.loads(json_str)
        # 转换日期字段
        for date_field in ['ann_date', 'f_ann_date', 'end_date']:
            if data.get(date_field):
                data[date_field] = datetime.strptime(data[date_field], '%Y-%m-%d').date()
        
        # 转换Decimal字段
        for key, value in data.items():
            if isinstance(value, (str, int, float)) and key not in ['ts_code', 'report_type', 'comp_type', 'end_type', 'update_flag']:
                data[key] = Decimal(str(value))
        
        return cls(**data)

    def to_json(self) -> str:
        """将利润表对象转换为JSON字符串"""
        data = asdict(self)
        # 转换日期字段
        for date_field in ['ann_date', 'f_ann_date', 'end_date']:
            if data.get(date_field):
                data[date_field] = data[date_field].isoformat()
        
        # 转换Decimal字段
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = str(value)
        
        return json.dumps(data, ensure_ascii=False)


@dataclass
class BalanceSheet:
    """资产负债表"""
    ts_code: str # TS股票代码
    ann_date: date # 公告日期
    f_ann_date: date # 实际公告日期
    end_date: date # 报告期
    report_type: str # 报表类型
    comp_type: str # 公司类型(1一般工商业2银行3保险4证券)
    end_type: str # 报告期类型
    total_share: Decimal # 期末总股本
    cap_rese: Decimal # 资本公积金
    undistr_porfit: Decimal # 未分配利润
    surplus_rese: Decimal # 盈余公积金
    special_rese: Decimal # 专项储备
    money_cap: Decimal # 货币资金
    trad_asset: Decimal # 交易性金融资产
    notes_receiv: Decimal # 应收票据
    accounts_receiv: Decimal # 应收账款
    oth_receiv: Decimal # 其他应收款
    prepayment: Decimal # 预付款项
    div_receiv: Decimal # 应收股利
    int_receiv: Decimal # 应收利息
    inventories: Decimal # 存货
    amor_exp: Decimal # 待摊费用
    nca_within_1y: Decimal # 一年内到期的非流动资产
    sett_rsrv: Decimal # 结算备付金
    loanto_oth_bank_fi: Decimal # 拆出资金
    premium_receiv: Decimal # 应收保费
    reinsur_receiv: Decimal # 应收分保账款
    reinsur_res_receiv: Decimal # 应收分保合同准备金
    pur_resale_fa: Decimal # 买入返售金融资产
    oth_cur_assets: Decimal # 其他流动资产
    total_cur_assets: Decimal # 流动资产合计
    fa_avail_for_sale: Decimal # 可供出售金融资产
    htm_invest: Decimal # 持有至到期投资
    lt_eqt_invest: Decimal # 长期股权投资
    invest_real_estate: Decimal # 投资性房地产
    time_deposits: Decimal # 定期存款
    oth_assets: Decimal # 其他资产
    lt_rec: Decimal # 长期应收款
    fix_assets: Decimal # 固定资产
    cip: Decimal # 在建工程
    const_materials: Decimal # 工程物资
    fixed_assets_disp: Decimal # 固定资产清理
    produc_bio_assets: Decimal # 生产性生物资产
    oil_and_gas_assets: Decimal # 油气资产
    intan_assets: Decimal # 无形资产
    r_and_d: Decimal # 研发支出
    goodwill: Decimal # 商誉
    lt_amor_exp: Decimal # 长期待摊费用
    defer_tax_assets: Decimal # 递延所得税资产
    decr_in_disbur: Decimal # 发放贷款及垫款
    oth_nca: Decimal # 其他非流动资产
    total_nca: Decimal # 非流动资产合计
    cash_reser_cb: Decimal # 现金及存放中央银行款项
    depos_in_oth_bfi: Decimal # 存放同业和其它金融机构款项
    prec_metals: Decimal # 贵金属
    deriv_assets: Decimal # 衍生金融资产
    rr_reins_une_prem: Decimal # 应收分保未到期责任准备金
    rr_reins_outstd_cla: Decimal # 应收分保未决赔款准备金
    rr_reins_lins_liab: Decimal # 应收分保寿险责任准备金
    rr_reins_lthins_liab: Decimal # 应收分保长期健康险责任准备金
    refund_depos: Decimal # 存出保证金
    ph_pledge_loans: Decimal # 保户质押贷款
    refund_cap_depos: Decimal # 存出资本保证金
    indep_acct_assets: Decimal # 独立账户资产
    client_depos: Decimal # 其中：客户资金存款
    client_prov: Decimal # 其中：客户备付金
    transac_seat_fee: Decimal # 其中:交易席位费
    invest_as_receiv: Decimal # 应收款项类投资
    total_assets: Decimal # 资产总计
    lt_borr: Decimal # 长期借款
    st_borr: Decimal # 短期借款
    cb_borr: Decimal # 向中央银行借款
    depos_ib_deposits: Decimal # 吸收存款及同业存放
    loan_oth_bank: Decimal # 拆入资金
    trading_fl: Decimal # 交易性金融负债
    notes_payable: Decimal # 应付票据
    acct_payable: Decimal # 应付账款
    adv_receipts: Decimal # 预收款项
    sold_for_repur_fa: Decimal # 卖出回购金融资产款
    comm_payable: Decimal # 应付手续费及佣金
    payroll_payable: Decimal # 应付职工薪酬
    taxes_payable: Decimal # 应交税费
    int_payable: Decimal # 应付利息
    div_payable: Decimal # 应付股利
    oth_payable: Decimal # 其他应付款
    acc_exp: Decimal # 预提费用
    deferred_inc: Decimal # 递延收益
    st_bonds_payable: Decimal # 应付短期债券
    payable_to_reinsurer: Decimal # 应付分保账款
    rsrv_insur_cont: Decimal # 保险合同准备金
    acting_trading_sec: Decimal # 代理买卖证券款
    acting_uw_sec: Decimal # 代理承销证券款
    non_cur_liab_due_1y: Decimal # 一年内到期的非流动负债
    oth_cur_liab: Decimal # 其他流动负债
    total_cur_liab: Decimal # 流动负债合计
    bond_payable: Decimal # 应付债券
    lt_payable: Decimal # 长期应付款
    specific_payables: Decimal # 专项应付款
    estimated_liab: Decimal # 预计负债
    defer_tax_liab: Decimal # 递延所得税负债
    defer_inc_non_cur_liab: Decimal # 递延收益-非流动负债
    oth_ncl: Decimal # 其他非流动负债
    total_ncl: Decimal # 非流动负债合计
    depos_oth_bfi: Decimal # 同业和其它金融机构存放款项
    deriv_liab: Decimal # 衍生金融负债
    depos: Decimal # 吸收存款
    agency_bus_liab: Decimal # 代理业务负债
    oth_liab: Decimal # 其他负债
    prem_receiv_adva: Decimal # 预收保费
    depos_received: Decimal # 存入保证金
    ph_invest: Decimal # 保户储金及投资款
    reser_une_prem: Decimal # 未到期责任准备金
    reser_outstd_claims: Decimal # 未决赔款准备金
    reser_lins_liab: Decimal # 寿险责任准备金
    reser_lthins_liab: Decimal # 长期健康险责任准备金
    indept_acc_liab: Decimal # 独立账户负债
    pledge_borr: Decimal # 其中:质押借款
    indem_payable: Decimal # 应付赔付款
    policy_div_payable: Decimal # 应付保单红利
    total_liab: Decimal # 负债合计
    treasury_share: Decimal # 减:库存股
    ordin_risk_reser: Decimal # 一般风险准备
    forex_differ: Decimal # 外币报表折算差额
    invest_loss_unconf: Decimal # 未确认的投资损失
    minority_int: Decimal # 少数股东权益
    total_hldr_eqy_exc_min_int: Decimal # 股东权益合计(不含少数股东权益)
    total_hldr_eqy_inc_min_int: Decimal # 股东权益合计(含少数股东权益)
    total_liab_hldr_eqy: Decimal # 负债及股东权益总计
    lt_payroll_payable: Decimal # 长期应付职工薪酬
    oth_comp_income: Decimal # 其他综合收益
    oth_eqt_tools: Decimal # 其他权益工具
    oth_eqt_tools_p_shr: Decimal # 其他权益工具(优先股)
    lending_funds: Decimal # 融出资金
    acc_receivable: Decimal # 应收款项
    st_fin_payable: Decimal # 应付短期融资款
    payables: Decimal # 应付款项
    hfs_assets: Decimal # 持有待售的资产
    hfs_sales: Decimal # 持有待售的负债
    cost_fin_assets: Decimal # 以摊余成本计量的金融资产
    fair_value_fin_assets: Decimal # 以公允价值计量且其变动计入其他综合收益的金融资产
    cip_total: Decimal # 在建工程(合计)(元)
    oth_pay_total: Decimal # 其他应付款(合计)(元)
    long_pay_total: Decimal # 长期应付款(合计)(元)
    debt_invest: Decimal # 债权投资(元)
    oth_debt_invest: Decimal # 其他债权投资(元)
    oth_eq_invest: Decimal # 其他权益工具投资(元)
    oth_illiq_fin_assets: Decimal # 其他非流动金融资产(元)
    oth_eq_ppbond: Decimal # 其他权益工具:永续债(元)
    receiv_financing: Decimal # 应收款项融资
    use_right_assets: Decimal # 使用权资产
    lease_liab: Decimal # 租赁负债
    contract_assets: Decimal # 合同资产
    contract_liab: Decimal # 合同负债
    accounts_receiv_bill: Decimal # 应收票据及应收账款
    accounts_pay: Decimal # 应付票据及应付账款
    oth_rcv_total: Decimal # 其他应收款(合计)（元）
    fix_assets_total: Decimal # 固定资产(合计)(元)
    update_flag: str # 更新标识
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BalanceSheet':
        """从JSON字符串创建资产负债表对象"""
        data = json.loads(json_str)
        # 转换日期字段
        for date_field in ['ann_date', 'f_ann_date', 'end_date']:
            if data.get(date_field):
                data[date_field] = datetime.strptime(data[date_field], '%Y-%m-%d').date()
        
        # 转换Decimal字段
        for key, value in data.items():
            if isinstance(value, (str, int, float)) and key not in ['ts_code', 'report_type', 'comp_type', 'end_type', 'update_flag']:
                data[key] = Decimal(str(value))
        
        return cls(**data)

    def to_json(self) -> str:
        """将资产负债表对象转换为JSON字符串"""
        data = asdict(self)
        # 转换日期字段
        for date_field in ['ann_date', 'f_ann_date', 'end_date']:
            if data.get(date_field):
                data[date_field] = data[date_field].isoformat()
        
        # 转换Decimal字段
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = str(value)
        
        return json.dumps(data, ensure_ascii=False)

@dataclass
class CashFlowStatement:
    """现金流量表"""
    ts_code: str # TS股票代码
    ann_date: date # 公告日期
    f_ann_date: date # 实际公告日期
    end_date: date # 报告期
    comp_type: str # 公司类型(1一般工商业2银行3保险4证券)
    report_type: str # 报表类型
    end_type: str # 报告期类型
    net_profit: Decimal # 净利润
    finan_exp: Decimal # 财务费用
    c_fr_sale_sg: Decimal # 销售商品、提供劳务收到的现金
    recp_tax_rends: Decimal # 收到的税费返还
    n_depos_incr_fi: Decimal # 客户存款和同业存放款项净增加额
    n_incr_loans_cb: Decimal # 向中央银行借款净增加额
    n_inc_borr_oth_fi: Decimal # 向其他金融机构拆入资金净增加额
    prem_fr_orig_contr: Decimal # 收到原保险合同保费取得的现金
    n_incr_insured_dep: Decimal # 保户储金净增加额
    n_reinsur_prem: Decimal # 收到再保业务现金净额
    n_incr_disp_tfa: Decimal # 处置交易性金融资产净增加额
    ifc_cash_incr: Decimal # 收取利息和手续费净增加额
    n_incr_disp_faas: Decimal # 处置可供出售金融资产净增加额
    n_incr_loans_oth_bank: Decimal # 拆入资金净增加额
    n_cap_incr_repur: Decimal # 回购业务资金净增加额
    c_fr_oth_operate_a: Decimal # 收到其他与经营活动有关的现金
    c_inf_fr_operate_a: Decimal # 经营活动现金流入小计
    c_paid_goods_s: Decimal # 购买商品、接受劳务支付的现金
    c_paid_to_for_empl: Decimal # 支付给职工以及为职工支付的现金
    c_paid_for_taxes: Decimal # 支付的各项税费
    n_incr_clt_loan_adv: Decimal # 客户贷款及垫款净增加额
    n_incr_dep_cbob: Decimal # 存放央行和同业款项净增加额
    c_pay_claims_orig_inco: Decimal # 支付原保险合同赔付款项的现金
    pay_handling_chrg: Decimal # 支付手续费的现金
    pay_comm_insur_plcy: Decimal # 支付保单红利的现金
    oth_cash_pay_oper_act: Decimal # 支付其他与经营活动有关的现金
    st_cash_out_act: Decimal # 经营活动现金流出小计
    n_cashflow_act: Decimal # 经营活动产生的现金流量净额
    oth_recp_ral_inv_act: Decimal # 收到其他与投资活动有关的现金
    c_disp_withdrwl_invest: Decimal # 收回投资收到的现金
    c_recp_return_invest: Decimal # 取得投资收益收到的现金
    n_recp_disp_fiolta: Decimal # 处置固定资产、无形资产和其他长期资产收回的现金净额
    n_recp_disp_sobu: Decimal # 处置子公司及其他营业单位收到的现金净额
    stot_inflows_inv_act: Decimal # 投资活动现金流入小计
    c_pay_acq_const_fiolta: Decimal # 购建固定资产、无形资产和其他长期资产支付的现金
    c_paid_invest: Decimal # 投资支付的现金
    n_disp_subs_oth_biz: Decimal # 取得子公司及其他营业单位支付的现金净额
    oth_pay_ral_inv_act: Decimal # 支付其他与投资活动有关的现金
    n_incr_pledge_loan: Decimal # 质押贷款净增加额
    stot_out_inv_act: Decimal # 投资活动现金流出小计
    n_cashflow_inv_act: Decimal # 投资活动产生的现金流量净额
    c_recp_borrow: Decimal # 取得借款收到的现金
    proc_issue_bonds: Decimal # 发行债券收到的现金
    oth_cash_recp_ral_fnc_act: Decimal # 收到其他与筹资活动有关的现金
    stot_cash_in_fnc_act: Decimal # 筹资活动现金流入小计
    free_cashflow: Decimal # 企业自由现金流量
    c_prepay_amt_borr: Decimal # 偿还债务支付的现金
    c_pay_dist_dpcp_int_exp: Decimal # 分配股利、利润或偿付利息支付的现金
    incl_dvd_profit_paid_sc_ms: Decimal # 其中:子公司支付给少数股东的股利、利润
    oth_cashpay_ral_fnc_act: Decimal # 支付其他与筹资活动有关的现金
    stot_cashout_fnc_act: Decimal # 筹资活动现金流出小计
    n_cash_flows_fnc_act: Decimal # 筹资活动产生的现金流量净额
    eff_fx_flu_cash: Decimal # 汇率变动对现金的影响
    n_incr_cash_cash_equ: Decimal # 现金及现金等价物净增加额
    c_cash_equ_beg_period: Decimal # 期初现金及现金等价物余额
    c_cash_equ_end_period: Decimal # 期末现金及现金等价物余额
    c_recp_cap_contrib: Decimal # 吸收投资收到的现金
    incl_cash_rec_saims: Decimal # 其中:子公司吸收少数股东投资收到的现金
    uncon_invest_loss: Decimal # 未确认投资损失
    prov_depr_assets: Decimal # 加:资产减值准备
    depr_fa_coga_dpba: Decimal # 固定资产折旧、油气资产折耗、生产性生物资产折旧
    amort_intang_assets: Decimal # 无形资产摊销
    lt_amort_deferred_exp: Decimal # 长期待摊费用摊销
    decr_deferred_exp: Decimal # 待摊费用减少
    incr_acc_exp: Decimal # 预提费用增加
    loss_disp_fiolta: Decimal # 处置固定、无形资产和其他长期资产的损失
    loss_scr_fa: Decimal # 固定资产报废损失
    loss_fv_chg: Decimal # 公允价值变动损失
    invest_loss: Decimal # 投资损失
    decr_def_inc_tax_assets: Decimal # 递延所得税资产减少
    incr_def_inc_tax_liab: Decimal # 递延所得税负债增加
    decr_inventories: Decimal # 存货的减少
    decr_oper_payable: Decimal # 经营性应收项目的减少
    incr_oper_payable: Decimal # 经营性应付项目的增加
    others: Decimal # 其他
    im_net_cashflow_oper_act: Decimal # 经营活动产生的现金流量净额(间接法)
    conv_debt_into_cap: Decimal # 债务转为资本
    conv_copbonds_due_within_1y: Decimal # 一年内到期的可转换公司债券
    fa_fnc_leases: Decimal # 融资租入固定资产
    im_n_incr_cash_equ: Decimal # 现金及现金等价物净增加额(间接法)
    net_dism_capital_add: Decimal # 拆出资金净增加额
    net_cash_rece_sec: Decimal # 代理买卖证券收到的现金净额(元)
    credit_impa_loss: Decimal # 信用减值损失
    use_right_asset_dep: Decimal # 使用权资产折旧
    oth_loss_asset: Decimal # 其他资产减值损失
    end_bal_cash: Decimal # 现金的期末余额
    beg_bal_cash: Decimal # 减:现金的期初余额
    end_bal_cash_equ: Decimal # 加:现金等价物的期末余额
    beg_bal_cash_equ: Decimal # 减:现金等价物的期初余额
    update_flag: str # 更新标志(1最新）
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CashFlowStatement':
        """从JSON字符串创建现金流量表对象"""
        data = json.loads(json_str)
        # 转换日期字段
        for date_field in ['ann_date', 'f_ann_date', 'end_date']:
            if data.get(date_field):
                data[date_field] = datetime.strptime(data[date_field], '%Y-%m-%d').date()
        
        # 转换Decimal字段
        for key, value in data.items():
            if isinstance(value, (str, int, float)) and key not in ['ts_code', 'ann_date', 'report_type', 'comp_type', 'end_type', 'update_flag']:
                data[key] = Decimal(str(value))
        
        return cls(**data)

    def to_json(self) -> str:
        """将现金流量表对象转换为JSON字符串"""
        data = asdict(self)
        # 转换日期字段
        for date_field in ['ann_date', 'f_ann_date', 'end_date']:
            if data.get(date_field):
                data[date_field] = data[date_field].isoformat()
        
        # 转换Decimal字段
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = str(value)
        
        return json.dumps(data, ensure_ascii=False)

@dataclass
class FinancialIndicators:
    """财务指标"""
    ts_code: str # TS代码
    ann_date: date # 公告日期
    end_date: date # 报告期
    eps: Decimal # 基本每股收益
    dt_eps: Decimal # 稀释每股收益
    total_revenue_ps: Decimal # 每股营业总收入
    revenue_ps: Decimal # 每股营业收入
    capital_rese_ps: Decimal # 每股资本公积
    surplus_rese_ps: Decimal # 每股盈余公积
    undist_profit_ps: Decimal # 每股未分配利润
    extra_item: Decimal # 非经常性损益
    profit_dedt: Decimal # 扣除非经常性损益后的净利润（扣非净利润）
    gross_margin: Decimal # 毛利
    current_ratio: Decimal # 流动比率
    quick_ratio: Decimal # 速动比率
    cash_ratio: Decimal # 保守速动比率
    invturn_days: Decimal # 存货周转天数
    arturn_days: Decimal # 应收账款周转天数
    inv_turn: Decimal # 存货周转率
    ar_turn: Decimal # 应收账款周转率
    ca_turn: Decimal # 流动资产周转率
    fa_turn: Decimal # 固定资产周转率
    assets_turn: Decimal # 总资产周转率
    op_income: Decimal # 经营活动净收益
    valuechange_income: Decimal # 价值变动净收益
    interst_income: Decimal # 利息费用
    daa: Decimal # 折旧与摊销
    ebit: Decimal # 息税前利润
    ebitda: Decimal # 息税折旧摊销前利润
    fcff: Decimal # 企业自由现金流量
    fcfe: Decimal # 股权自由现金流量
    current_exint: Decimal # 无息流动负债
    noncurrent_exint: Decimal # 无息非流动负债
    interestdebt: Decimal # 带息债务
    netdebt: Decimal # 净债务
    tangible_asset: Decimal # 有形资产
    working_capital: Decimal # 营运资金
    networking_capital: Decimal # 营运流动资本
    invest_capital: Decimal # 全部投入资本
    retained_earnings: Decimal # 留存收益
    diluted2_eps: Decimal # 期末摊薄每股收益
    bps: Decimal # 每股净资产
    ocfps: Decimal # 每股经营活动产生的现金流量净额
    retainedps: Decimal # 每股留存收益
    cfps: Decimal # 每股现金流量净额
    ebit_ps: Decimal # 每股息税前利润
    fcff_ps: Decimal # 每股企业自由现金流量
    fcfe_ps: Decimal # 每股股东自由现金流量
    netprofit_margin: Decimal # 销售净利率
    grossprofit_margin: Decimal # 销售毛利率
    cogs_of_sales: Decimal # 销售成本率
    expense_of_sales: Decimal # 销售期间费用率
    profit_to_gr: Decimal # 净利润/营业总收入
    saleexp_to_gr: Decimal # 销售费用/营业总收入
    adminexp_of_gr: Decimal # 管理费用/营业总收入
    finaexp_of_gr: Decimal # 财务费用/营业总收入
    impai_ttm: Decimal # 资产减值损失/营业总收入
    gc_of_gr: Decimal # 营业总成本/营业总收入
    op_of_gr: Decimal # 营业利润/营业总收入
    ebit_of_gr: Decimal # 息税前利润/营业总收入
    roe: Decimal # 净资产收益率
    roe_waa: Decimal # 加权平均净资产收益率
    roe_dt: Decimal # 净资产收益率(扣除非经常损益)
    roa: Decimal # 总资产报酬率
    npta: Decimal # 总资产净利润
    roic: Decimal # 投入资本回报率
    roe_yearly: Decimal # 年化净资产收益率
    roa2_yearly: Decimal # 年化总资产报酬率
    roe_avg: Decimal # 平均净资产收益率(增发条件)
    opincome_of_ebt: Decimal # 经营活动净收益/利润总额
    investincome_of_ebt: Decimal # 价值变动净收益/利润总额
    n_op_profit_of_ebt: Decimal # 营业外收支净额/利润总额
    tax_to_ebt: Decimal # 所得税/利润总额
    dtprofit_to_profit: Decimal # 扣除非经常损益后的净利润/净利润
    salescash_to_or: Decimal # 销售商品提供劳务收到的现金/营业收入
    ocf_to_or: Decimal # 经营活动产生的现金流量净额/营业收入
    ocf_to_opincome: Decimal # 经营活动产生的现金流量净额/经营活动净收益
    capitalized_to_da: Decimal # 资本支出/折旧和摊销
    debt_to_assets: Decimal # 资产负债率
    assets_to_eqt: Decimal # 权益乘数
    dp_assets_to_eqt: Decimal # 权益乘数(杜邦分析)
    ca_to_assets: Decimal # 流动资产/总资产
    nca_to_assets: Decimal # 非流动资产/总资产
    tbassets_to_totalassets: Decimal # 有形资产/总资产
    int_to_talcap: Decimal # 带息债务/全部投入资本
    eqt_to_talcapital: Decimal # 归属于母公司的股东权益/全部投入资本
    currentdebt_to_debt: Decimal # 流动负债/负债合计
    longdeb_to_debt: Decimal # 非流动负债/负债合计
    ocf_to_shortdebt: Decimal # 经营活动产生的现金流量净额/流动负债
    debt_to_eqt: Decimal # 产权比率
    eqt_to_debt: Decimal # 归属于母公司的股东权益/负债合计
    eqt_to_interestdebt: Decimal # 归属于母公司的股东权益/带息债务
    tangibleasset_to_debt: Decimal # 有形资产/负债合计
    tangasset_to_intdebt: Decimal # 有形资产/带息债务
    tangibleasset_to_netdebt: Decimal # 有形资产/净债务
    ocf_to_debt: Decimal # 经营活动产生的现金流量净额/负债合计
    ocf_to_interestdebt: Decimal # 经营活动产生的现金流量净额/带息债务
    ocf_to_netdebt: Decimal # 经营活动产生的现金流量净额/净债务
    ebit_to_interest: Decimal # 已获利息倍数(EBIT/利息费用)
    longdebt_to_workingcapital: Decimal # 长期债务与营运资金比率
    ebitda_to_debt: Decimal # 息税折旧摊销前利润/负债合计
    turn_days: Decimal # 营业周期
    roa_yearly: Decimal # 年化总资产净利率
    roa_dp: Decimal # 总资产净利率(杜邦分析)
    fixed_assets: Decimal # 固定资产合计
    profit_prefin_exp: Decimal # 扣除财务费用前营业利润
    non_op_profit: Decimal # 非营业利润
    op_to_ebt: Decimal # 营业利润／利润总额
    nop_to_ebt: Decimal # 非营业利润／利润总额
    ocf_to_profit: Decimal # 经营活动产生的现金流量净额／营业利润
    cash_to_liqdebt: Decimal # 货币资金／流动负债
    cash_to_liqdebt_withinterest: Decimal # 货币资金／带息流动负债
    op_to_liqdebt: Decimal # 营业利润／流动负债
    op_to_debt: Decimal # 营业利润／负债合计
    roic_yearly: Decimal # 年化投入资本回报率
    total_fa_trun: Decimal # 固定资产合计周转率
    profit_to_op: Decimal # 利润总额／营业收入
    q_opincome: Decimal # 经营活动单季度净收益
    q_investincome: Decimal # 价值变动单季度净收益
    q_dtprofit: Decimal # 扣除非经常损益后的单季度净利润
    q_eps: Decimal # 每股收益(单季度)
    q_netprofit_margin: Decimal # 销售净利率(单季度)
    q_gsprofit_margin: Decimal # 销售毛利率(单季度)
    q_exp_to_sales: Decimal # 销售期间费用率(单季度)
    q_profit_to_gr: Decimal # 净利润／营业总收入(单季度)
    q_saleexp_to_gr: Decimal # 销售费用／营业总收入 (单季度)
    q_adminexp_to_gr: Decimal # 管理费用／营业总收入 (单季度)
    q_finaexp_to_gr: Decimal # 财务费用／营业总收入 (单季度)
    q_impair_to_gr_ttm: Decimal # 资产减值损失／营业总收入(单季度)
    q_gc_to_gr: Decimal # 营业总成本／营业总收入 (单季度)
    q_op_to_gr: Decimal # 营业利润／营业总收入(单季度)
    q_roe: Decimal # 净资产收益率(单季度)
    q_dt_roe: Decimal # 净资产单季度收益率(扣除非经常损益)
    q_npta: Decimal # 总资产净利润(单季度)
    q_opincome_to_ebt: Decimal # 经营活动净收益／利润总额(单季度)
    q_investincome_to_ebt: Decimal # 价值变动净收益／利润总额(单季度)
    q_dtprofit_to_profit: Decimal # 扣除非经常损益后的净利润／净利润(单季度)
    q_salescash_to_or: Decimal # 销售商品提供劳务收到的现金／营业收入(单季度)
    q_ocf_to_sales: Decimal # 经营活动产生的现金流量净额／营业收入(单季度)
    q_ocf_to_or: Decimal # 经营活动产生的现金流量净额／经营活动净收益(单季度)
    basic_eps_yoy: Decimal # 基本每股收益同比增长率(%)
    dt_eps_yoy: Decimal # 稀释每股收益同比增长率(%)
    cfps_yoy: Decimal # 每股经营活动产生的现金流量净额同比增长率(%)
    op_yoy: Decimal # 营业利润同比增长率(%)
    ebt_yoy: Decimal # 利润总额同比增长率(%)
    netprofit_yoy: Decimal # 归属母公司股东的净利润同比增长率(%)
    dt_netprofit_yoy: Decimal # 归属母公司股东的净利润-扣除非经常损益同比增长率(%)
    ocf_yoy: Decimal # 经营活动产生的现金流量净额同比增长率(%)
    roe_yoy: Decimal # 净资产收益率(摊薄)同比增长率(%)
    bps_yoy: Decimal # 每股净资产相对年初增长率(%)
    assets_yoy: Decimal # 资产总计相对年初增长率(%)
    eqt_yoy: Decimal # 归属母公司的股东权益相对年初增长率(%)
    tr_yoy: Decimal # 营业总收入同比增长率(%)
    or_yoy: Decimal # 营业收入同比增长率(%)
    q_gr_yoy: Decimal # 营业总收入同比增长率(%)(单季度)
    q_gr_qoq: Decimal # 营业总收入环比增长率(%)(单季度)
    q_sales_yoy: Decimal # 营业收入同比增长率(%)(单季度)
    q_sales_qoq: Decimal # 营业收入环比增长率(%)(单季度)
    q_op_yoy: Decimal # 营业利润同比增长率(%)(单季度)
    q_op_qoq: Decimal # 营业利润环比增长率(%)(单季度)
    q_profit_yoy: Decimal # 净利润同比增长率(%)(单季度)
    q_profit_qoq: Decimal # 净利润环比增长率(%)(单季度)
    q_netprofit_yoy: Decimal # 归属母公司股东的净利润同比增长率(%)(单季度)
    q_netprofit_qoq: Decimal # 归属母公司股东的净利润环比增长率(%)(单季度)
    equity_yoy: Decimal # 净资产同比增长率
    rd_exp: Decimal # 研发费用
    update_flag: str # 更新标识
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FinancialIndicators':
        """从JSON字符串创建财务指标对象"""
        data = json.loads(json_str)
        # 转换日期字段
        for date_field in ['ann_date', 'end_date']:
            if data.get(date_field):
                data[date_field] = datetime.strptime(data[date_field], '%Y-%m-%d').date()
        
        # 转换Decimal字段
        for key, value in data.items():
            if isinstance(value, (str, int, float)) and key not in ['ts_code', 'update_flag']:
                data[key] = Decimal(str(value))
        
        return cls(**data)

    def to_json(self) -> str:
        """将财务指标对象转换为JSON字符串"""
        data = asdict(self)
        # 转换日期字段
        for date_field in ['ann_date', 'end_date']:
            if data.get(date_field):
                data[date_field] = data[date_field].isoformat()
        
        # 转换Decimal字段
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = str(value)
        
        return json.dumps(data, ensure_ascii=False)

@dataclass
class FinancialReport:
    """财务年报"""
    ts_code: str                                    # TS代码
    report_date: date                              # 报告日期
    report_type: str                              # 报告类型
    end_type: str                                 # 报告期类型
    income_statement: IncomeStatement               # 利润表
    balance_sheet: BalanceSheet                    # 资产负债表
    cash_flow_statement: CashFlowStatement         # 现金流量表
    financial_indicators: FinancialIndicators      # 财务指标

    def to_json(self) -> str:
        """将财务报告对象转换为JSON字符串"""
        data = {
            'ts_code': self.ts_code,
            'report_date': self.report_date.isoformat(),
            'report_type': self.report_type,
            'end_type': self.end_type,
            'income_statement': self.income_statement.to_json() if self.income_statement else None,
            'balance_sheet': self.balance_sheet.to_json() if self.balance_sheet else None,
            'cash_flow_statement': self.cash_flow_statement.to_json() if self.cash_flow_statement else None,
            'financial_indicators': self.financial_indicators.to_json() if self.financial_indicators else None
        }
        return json.dumps(data, ensure_ascii=False)
