# -*- coding: utf-8 -*-
"""
"""

import numpy as np

def calc_optimal_rtn(riskAvFactor, covariance, eqlibriumWts):                
    optimalRtns = 2 * riskAvFactor *  np.dot(covariance, np.row_stack(eqlibriumWts))
    
    print("\noptimal rtns: ")    
    print(optimalRtns)
    
    return optimalRtns
       
def calc_optimal_wt(riskAvFactor, covariance, eqlibriumWts):
    optimal_excess_rtn =   calc_optimal_rtn(riskAvFactor, covariance, eqlibriumWts)                    
    optimalWts = (0.5 / riskAvFactor *  np.linalg.inv(np.matrix(covariance)) * np.matrix(optimal_excess_rtn))
    
    print("\noptimal wts: ")    
    print(optimalWts)
    
    return optimalWts
