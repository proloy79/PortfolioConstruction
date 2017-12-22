# -*- coding: utf-8 -*-
"""
"""

import numpy as np
import pandas as pd

class BL:
    
    def __init__(self, riskAvFactor, covariance, eqlibriumWts):
        self.riskAvFactor = riskAvFactor        
        self.covariance = covariance
        self.eqlibriumWts = np.row_stack(eqlibriumWts)        
     
    def optimize(self):
        self.calc_optimal_premium()
        self.calc_optimal_wt()
        
        self.sigma = np.dot(np.column_stack(self.optimalWts), np.dot(self.covariance, self.optimalWts))
        print("\nsigma market (historical): ")    
        print(self.sigma)
        
        
    def calc_optimal_premium(self):                
        self.optimalPrems = 2 * self.riskAvFactor *  np.dot(self.covariance, self.eqlibriumWts)
        
        print("\noptimal premium: ")    
        print(self.optimalPrems)
        
           
    def calc_optimal_wt(self):            
        self.optimalWts = (0.5 / self.riskAvFactor *  np.linalg.inv(np.matrix(self.covariance)) * np.matrix(self.optimalPrems))
        
        print("\noptimal wts: ")    
        print(self.optimalWts)
        
         
    def serialize_to_file(self, writer, tickers):        
        pd.DataFrame(self.optimalWts,index=tickers, columns=['OptimalWt']).to_excel(writer, 'OptWts')        
        pd.DataFrame(self.optimalPrems,index=tickers, columns=['OptimalRtn']).to_excel(writer, 'OptPrems')        
        
        writer.save()