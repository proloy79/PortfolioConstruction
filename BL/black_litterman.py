# -*- coding: utf-8 -*-
"""
"""

import numpy as np

def calc_optimal_rtn(riskAvFactor, covariance, eqlibriumWts):                
    return 2 * riskAvFactor *  np.matrix(covariance) * np.matrix(eqlibriumWts)
       
def calc_optimal_wt(riskAvFactor, covariance, eqlibriumWts):
    optimal_excess_rtn =   calc_optimal_rtn(riskAvFactor, covariance, eqlibriumWts)                      
    return (1 / 2 / riskAvFactor *  np.linalg.inv(np.matrix(covariance)) * np.matrix(optimal_excess_rtn))