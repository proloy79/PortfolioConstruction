# -*- coding: utf-8 -*-
"""

"""
from arch import arch_model
import numpy as np
import math
#import pandas as pd

#fits the vol using GJR
class vol:
    
    def __init__(self, ticker, quotes):        
        self.ticker = ticker
        self.quotes = quotes        
        self.params = {}
        
    #using the GJR-GARCH model to fit the vol                
    def fit_vol(self):                                    
        am = arch_model(self.quotes.pct_change().dropna(),p=1, o=1, q=1)
        result = am.fit()  
        
#        print(result.conditional_volatility)
#        
#        writer = pd.ExcelWriter("./../CondVolFromArch.xlsx")          
#        result.conditional_volatility.to_excel(writer, 'Vol')                          
#        writer.save()
                        
        self.params['mean'] = result.params['mu'] 
        self.params['omega'] = result.params['omega']
        self.params['alpha'] = result.params['alpha[1]']
        self.params['gamma'] = result.params['gamma[1]']
        self.params['beta'] = result.params['beta[1]']

        #print(self.params)
        
        #below terms are used in forecasting        
        self.persistence = self.params['alpha'] + 0.5*self.params['gamma'] + self.params['beta']
        self.averageVol = self.params['omega']/(1-self.persistence)
        
        #print(result.params)
                
        self.conditionalVol = np.zeros(len(self.quotes)-1)
        self.logRtn = np.zeros(len(self.quotes)-1)
        
        for i in range(1, len(self.quotes)):
            self.logRtn[i-1] = math.log(self.quotes[i]/self.quotes[i-1])                
        
        #let's assume the first std dev is same as that of the sample        
        self.conditionalVol[0] = np.std(self.logRtn)
        
        for i in range(1, len(self.logRtn)):            
            err = self.logRtn[i-1] - self.params['mean']
            S = 1 if err < 0 else 0
            self.conditionalVol[i] = math.sqrt(self.params['omega'] + 
                               (self.params['alpha'] + self.params['gamma']*S)*math.pow(err, 2) 
                               + self.params['beta']*self.conditionalVol[i-1]*self.conditionalVol[i-1])    
    
    #n 1,2,3 no of terms in the future
    def forecast_vol(self, n ):        
        return self.averageVol + math.pow(self.persistence, n)*(self.conditionalVol[-1] - self.averageVol)