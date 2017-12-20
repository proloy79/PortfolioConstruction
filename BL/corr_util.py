# -*- coding: utf-8 -*-
"""

"""
import pandas as pd

#generates the correlation given any input
def generate_corr(inputData, methodName):                
        df = pd.DataFrame(inputData)          
        return df.corr(method=methodName)        
        
#generate the rank correlations for the given conditional vols    
def generate_rank_corr(inputData):                
    return generate_corr(inputData, 'spearman')
    
#generate the pearson correlations for the given conditional vols    
def generate_std_corr(inputData):                
     return generate_corr(inputData, 'pearson')          
    
    
#generate the kendall correlations for the given conditional vols    
def generate_kendall_corr(inputData):        
    return generate_corr(inputData, 'kendall')    
    
    
               
    
        
            
   