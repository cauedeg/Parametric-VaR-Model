from functions import *
from settings import *

var = VaR()

def main():

    net_exp = pd.read_excel("inputs/exposure.xlsx")
    prices = pd.read_excel("inputs/prices.xlsx")

    prices = pd.pivot_table(
        prices, 
        values="value", 
        index="date", 
        columns="asset"
        )

    prices.index = pd.to_datetime(prices.index)
    prices = prices.ffill()

    net_exp_mtm = pd.pivot_table(
        net_exp,
        values="exposure",
        index="period",
        columns="risk_factor",
        aggfunc="sum",
        )

    mtm = var.f_mtm(net_exp_mtm, prices, DT_INI)
    mtm_g = mtm.sum().to_frame().T
    mtm_g.index = ["Total"]

    vol = {}
    for i in mtm.columns:
        vol[i] = var.f_vol(1, prices[i], 1)

    returns = var.f_returns(prices, mtm_g.columns)
    returns = returns.dropna()
    corr = var.f_corr_ewma(returns, 0.94)
    cov = var.f_cov(corr, vol)
    par_var = var.f_par_VaR(mtm_g, cov)

    print(float(par_var))

main()