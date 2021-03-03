import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.regression.mixed_linear_model import MixedLMResultsWrapper
from statsmodels.tools.validation import  bool_like, float_like


class Assumptions:
    def __init__(self, model, data, title='Model Report'):
        self.title = title
        self.model = model
        self.data = data
        self.target = model.model.endog_names
        self.features = list(model.model.exog_names)
        self.features.remove('Intercept')
        self.formula = model.model.formula
        
        if len(self.features) > 1:
            self.multi = True
        else:
            self.multi = False
        
    def check(self):
        rainbow_statistic, rainbow_p_value = self.linearity()
        lagrange_multiplier_pvalue, f_stat_p_value = self.homoscedasticity()
        ss  = self.sum_squared_residuals(self.model.model.endog, self.model.predict())
        self.results  = pd.DataFrame([[rainbow_statistic, rainbow_p_value, lagrange_multiplier_pvalue,
                                    f_stat_p_value, ss]], columns = ['rainbow_stat', 'rainbow_p', 
                                                                 'lagrange_multiplier', 'f_stat_p', 'ss'])
        if self.multi:
            multicollinearity = self.multicollinearity()
            self.results['av_var_inflation'] = multicollinearity.VIF.max()
            
        display(Markdown(self.results.to_markdown()))
        self.model_report()
        
    # Linearity
    def linearity(self):
        rainbow_statistic, rainbow_p_value = self.linear_rainbow(self.model)
        return  rainbow_statistic, rainbow_p_value

    # Homoscedasticity
    def homoscedasticity(self):
        y = self.data[self.target]
        y_hat = self.model.predict()
        
        fig, ax = plt.subplots()
        ax.set(xlabel="Predicted",
                ylabel="Residuals (Predicted - Actual)")
        ax.scatter(x=y_hat, y=y_hat-y, color="blue", alpha=0.2)
        ax.set_title('Residuals');

        lm, lm_p_value, fvalue, f_p_value = het_breuschpagan(y-y_hat, self.data[self.features])
        return lm_p_value, f_p_value
        print("Lagrange Multiplier p-value:", lm_p_value)
        print("F-statistic p-value:", f_p_value)

    def multicollinearity(self):
        rows = self.data[self.features].values

        vif_df = pd.DataFrame()
        vif_df["VIF"] = [variance_inflation_factor(rows, i) for i in range(2)]
        vif_df["feature"] = self.features

        return  vif_df
    
    
    def linear_rainbow(self, res, frac=0.5, order_by=None, use_distance=False,
                       center=None):


        frac = float_like(frac, "frac")

        use_distance = bool_like(use_distance, "use_distance")
        nobs = res.nobs

        endog = res.model.endog
        exog = res.model.exog
        exog_names = res.model.exog_names
        endog_name = res.model.endog_names
        if isinstance(res, MixedLMResultsWrapper):
            groups = self.data[res.model.data.exog_re_names]
            exog = np.hstack((exog, groups))
            exog_names = exog_names + ['groups']

            exog = pd.DataFrame(exog, columns = exog_names)
            exog[endog_name] = endog
  
        
        

        
        if isinstance(res, MixedLMResultsWrapper):
            data = pd.DataFrame()
   
            for group in exog.groups.unique():
        
                frame = exog[exog.groups == group].reset_index(drop=True)
                nobs = len(frame)
                lowidx = np.ceil(0.5 * (1 - frac) * nobs).astype(int)
                uppidx = np.floor(lowidx + frac * nobs).astype(int)
                mi_sl = slice(lowidx, uppidx)
                frame = frame.iloc[mi_sl]

                data = data.append(frame)

            exog_names.remove('Intercept')
            data[data.columns[:-2]] = data[data.columns[:-2]].astype(float)
            formula = endog_name + '~' + '+'.join(exog_names[:-1]) + '+ 1'
            res_mi = sm.MixedLM.from_formula(formula, 
                                             groups='groups',
                                             data=data).fit()
        
            
        else:
            lowidx = np.ceil(0.5 * (1 - frac) * nobs).astype(int)
            uppidx = np.floor(lowidx + frac * nobs).astype(int)
            if uppidx - lowidx < exog.shape[1]:
                raise ValueError("frac is too small to perform test. frac * nobs"
                                 "must be greater than the number of exogenous"
                                 "variables in the model.")
            mi_sl = slice(lowidx, uppidx)
            endog = endog[mi_sl]
            exog = exog[mi_sl]
            res_mi = sm.OLS(endog, exog).fit()
  

        nobs = res.model.exog.shape[0]
        nobs_mi = res_mi.model.endog.shape[0]

        if isinstance(res, MixedLMResultsWrapper):
            ss_mi = self.sum_squared_residuals(res_mi.model.endog, res_mi.predict())
            ss  = self.sum_squared_residuals(res.model.endog, res.predict())

        else:
            ss_mi = res_mi.ssr
            ss = res.ssr
        
        fstat = (ss - ss_mi) / (nobs - nobs_mi) / ss_mi * res_mi.df_resid
        pval = stats.f.sf(fstat, nobs - nobs_mi, res_mi.df_resid)
        return fstat, pval
    
    def sum_squared_residuals(self, true, preds):
        return ((true-preds)**2).sum()
    
    def model_report(self):
        threshold = .05
        linear = round(self.results.rainbow_p.iloc[0], 2)
        homo = round(self.results.lagrange_multiplier.iloc[0], 2)
        
        if linear > 0.05:
            linear = '**met** (p > 0.05)'
        else:
            linear = '**violated** (p < 0.05)'
        if homo > 0.05:
            homo = '**met** (p > 0.05)'
        else:
            homo = '**violated** (p < 0.05)'
        mark = f'''\n# {self.title}\n\n**formula:** `{self.formula}`\n\n### Assumptions\n- Linearity Assumption was {linear}\n- Homoscedasticity was {homo}'''

        display(Markdown(mark))
