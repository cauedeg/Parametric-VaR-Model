from settings import *

class VaR:
    # def f_mtm(self, positions, prices, data):

    #     mtm = pd.DataFrame()
    #     if pd.to_datetime(data, dayfirst=True).strftime("%Y-%m-%d") not in prices.index:
    #         data = prices.index.max()
    #     for columns in positions:
    #         if "asset1_m" in columns:
    #             if "m0" in columns:
    #                 mtm[columns] = (
    #                     positions[columns]
    #                     * prices.loc[
    #                         pd.to_datetime(data, dayfirst=True).strftime("%Y-%m-%d"),
    #                         "asset1_spot",
    #                     ]
    #                 )
    #             else:
    #                 mtm[columns] = (
    #                     positions[columns]
    #                     * prices.loc[
    #                         pd.to_datetime(data, dayfirst=True).strftime("%Y-%m-%d"),
    #                         columns,
    #                     ]
    #                 )
    #         elif "gasolina" in columns:
    #             mtm[columns] = (
    #                 positions[columns]
    #                 * prices.loc[
    #                     pd.to_datetime(data, dayfirst=True).strftime("%Y-%m-%d"), columns
    #                 ]
    #                 * 1
    #                 / 100
    #             )

    #         else:
    #             mtm[columns] = (
    #                 positions[columns]
    #                 * prices.loc[
    #                     pd.to_datetime(data, dayfirst=True).strftime("%Y-%m-%d"), columns
    #                 ]
    #             )
    #     return mtm
    
    def f_mtm(self, positions, prices, data):

        mtm = pd.DataFrame()
        if pd.to_datetime(data, dayfirst=True).strftime("%Y-%m-%d") not in prices.index:
            data = prices.index.max()
        for columns in positions:
            mtm[columns] = (
                positions[columns]
                * prices.loc[
                    pd.to_datetime(data, dayfirst=True).strftime("%Y-%m-%d"), columns
                ]
            )
            
        return mtm

    def f_vol(self, modelo, precos, horizonte, L=None):

        """
        Calculate the price series volatility according to the selected model.

        Args:
            model - 1 for GARCH(1,1); 2 for EWMA (integer)
            prices - DataFrame containing the price series
            frequency - frequency for volatility calculation (B = business days; D = calendar days; M = monthly)
            L (optional) - if model == EWMA, define the lambda to be used
            horizon (optional) - if model == GARCH(1,1), define the time horizon for volatility calculation

        Returns:

            Dictionary containing the calculated volatilities for each time period

        """
        precos.dropna(inplace=True)
        retornos = np.log(precos.pct_change(1) + 1)
        garch_vol = {}
        vol = {}
        if modelo == 1:
            model = arch_model(
                retornos.dropna(),
                mean="Zero",
                vol="GARCH",
                p=1,
                q=1,
                dist="StudentsT",
                rescale=False,
            )
            model_fit = model.fit(disp='off') #remove terminal outputs
            yhat = model_fit.forecast(horizon=horizonte, reindex=False)
            garch_vol = yhat.variance.dropna().values[0] ** (1 / 2)
            vol = garch_vol.copy()

        ewma_calc = pd.DataFrame()
        ewma_vol = {}
        if modelo == 2:
            n = len(precos)
            ewma_calc["var"] = np.log(precos.pct_change(1) + 1) ** 2
            ewma_calc = ewma_calc.sort_index(ascending=False)
            ewma_calc["wts"] = [(L ** (i - 1) * (1 - L)) for i in range(1, n + 1)]
            ewma_calc["ewma"] = ewma_calc["wts"] * ewma_calc["var"]
            ewma_vol = np.sqrt(ewma_calc["ewma"].sum())
            vol = [ewma_vol.copy() for i in range(horizonte)]

        return vol

    def f_returns(self, precos, columns=None):

        if len(columns) != 0:
            returns = np.log(precos[columns].pct_change(1) + 1)

        else:
            returns = np.log(precos.pct_change(1) + 1)

        return returns

    def f_corr_ewma(self, returns, alpha):

        df = returns.copy()
        ativos = df.columns
        df["N"] = np.arange(len(df))[::-1]
        df["lambda"] = (1 - alpha) * alpha ** (df["N"]) / (1 - alpha ** len(df))
        matrix = pd.DataFrame(index=ativos, columns=ativos)

        for i in ativos:
            for j in ativos:
                df["pt1"] = df["lambda"] * (df[i] - df[i].mean()) * (df[j] - df[j].mean())
                pt1 = df["pt1"].sum()
                df["pt2"] = df["lambda"] * (df[i] - df[i].mean()) ** 2
                df["pt3"] = df["lambda"] * (df[j] - df[j].mean()) ** 2
                pt4 = np.sqrt(df["pt2"].sum() * df["pt3"].sum())
                correl = pt1 / pt4
                matrix.loc[i, j] = correl

        return matrix

    def f_cov(self, corr, vol):

        cov = pd.DataFrame(columns=corr.columns, index=corr.index)
        for i in cov.columns:
            for j in cov.index:
                cov.loc[j, i] = corr.loc[j, i] * vol[i] * vol[j]

        return cov

    def f_par_VaR(self, mtm, covariance):
        

        cov = covariance[mtm.columns].filter(
            items=mtm.columns, axis=0
        )

        var =math.sqrt(
                np.matmul(
                    np.matmul(cov, mtm.loc['Total']),
                    mtm.loc['Total'],
                )
            ) * (norm.ppf(0.05))

        return var
    
class CustomFormatter(logging.Formatter):

    grey = '\x1b[38;20m'
    yellow = '\x1b[33;20m'
    red = '\x1b[31;20m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    format = (
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s)'
    )

    FORMATS = {
        logging.DEBUG: Style.BRIGHT
        + format
        + Style.RESET_ALL,  # green color DEBUG
        logging.INFO: Style.BRIGHT
        + Fore.BLUE
        + format
        + Style.RESET_ALL,  # INFO in white and black
        logging.WARNING: Fore.YELLOW
        + format
        + Style.RESET_ALL,  # yellow WARNING
        logging.ERROR: Fore.RED
        + format
        + Style.RESET_ALL,  # red ERROR
        logging.CRITICAL: Style.BRIGHT
        + Fore.RED
        + format
        + Style.RESET_ALL,  # red and bold CRITICAL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class Logger:

    def __init__(self):
        self.logger = logging.getLogger('My_app')
        self.logger.setLevel(logging.DEBUG)

        # check handler logger
        if not self.logger.hasHandlers():
            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(CustomFormatter())
            self.logger.addHandler(ch)

    def insert(self, type, message):
        if type == 'd':
            self.logger.debug(message)
        elif type == 'i':
            self.logger.info(message)
        elif type == 'w':
            self.logger.warning(message)
        elif type == 'e':
            self.logger.error(message)
        elif type == 'c':
            self.logger.critical(message)
