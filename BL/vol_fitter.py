# -*- coding: utf-8 -*-
"""

"""
from arch import arch_model
import numpy as np
import math

#fits the vol using GJR
class vol:
    
    def __init__(self, ticker, quotes):        
        self.ticker = ticker
        self.quotes = quotes        
        
    #using the GJR-GARCH model to fit the vol                
    def fit_vol(self):                                    
        am = arch_model(self.quotes.pct_change().dropna(),p=1, o=1, q=1)
        result = am.fit()  
        #print(result.summary())
        self.mean = result.params['mu'] 
        self.omega = result.params['omega']
        self.alpha = result.params['alpha[1]']
        self.gamma = result.params['gamma[1]']
        self.beta = result.params['beta[1]']

        #below terms are used in forecasting        
        self.persistence = self.alpha + 0.5*self.gamma + self.beta
        self.averageVol = self.omega/(1-self.persistence)
        
        #print(result.params)
                
        self.stdDev = np.zeros(len(self.quotes)-1)
        self.logRtn = np.zeros(len(self.quotes)-1)
        
        for i in range(1, len(self.quotes)):
            self.logRtn[i-1] = math.log(self.quotes[i]/self.quotes[i-1])                
        
        #let's assume the first std dev is same as that of the sample        
        self.stdDev[0] = np.std(self.logRtn)
        
        for i in range(1, len(self.logRtn)):            
            err = self.logRtn[i-1] - self.mean
            S = 1 if err < 0 else 0
            self.stdDev[i] = math.sqrt(self.omega + (self.alpha + self.gamma*S)*math.pow(err, 2) + self.beta*self.stdDev[i-1]*self.stdDev[i-1])    
    
    #n 1,2,3 no of terms in the future
    def forecast_vol(self, n ):        
        return self.averageVol + math.pow(self.persistence, n)*(self.stdDev[-1] - self.averageVol)