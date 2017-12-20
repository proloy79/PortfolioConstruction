# -*- coding: utf-8 -*-
"""

"""
import math
import pandas as pd

#class holds the raw quotes and the log returns
class quotes:
    
    def __init__(self, ticker, quoteTs, dates):                
        self.rawQuotes = pd.Series(quoteTs, index=dates, name=ticker)        
                
    def gen_log_returns(self):                                    
        self.returns = []
        for i in range(1, len(self.quotes)):
            self.returns.append(math.log(self.quotes[i]/self.quotes[i-1]))
                