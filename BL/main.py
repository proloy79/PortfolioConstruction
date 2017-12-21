# -*- coding: utf-8 -*-
"""

"""
#*****all matrix are column by default***** 

import datetime as dt
import market_data as mkt
import enum_def as en
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import black_litterman as bl
import os

#set to True if you need to reload the data from yahoo
importData=False
#importData=True

dataDir = os.path.realpath("./../data")
dataSrc = "yahoo"

tickers = ['AAPL','ABT','AJG','AMZN','BA','BBY','CVX','FB', 'GE','JPM', 'PG','T', 'TEL','XOM']
#tickers = ['ABT','BA','BBY','CVX','GE','PG','TEL','XOM']
#tickers = ['AAPL']

#the current db has data for the below date range, if a fresh set is required
#execute import_data
startDt = dt.date(2013,1,1)
endDt = dt.date(2017,12,17)

stDtStr = startDt.strftime('%Y%m%d')
endDtStr = endDt.strftime('%Y%m%d')

if not os.path.exists(dataDir):
    os.makedirs(dataDir)
    
rawDataFile = os.path.join(dataDir, stDtStr + '_' + endDtStr 
                                  + '_' + dataSrc + '-data.xlsx') 

fittedVolFile = os.path.join(dataDir, 'fitted_' + stDtStr + '_' + endDtStr 
                             + '_vols.xlsx')        

#want to check the data imported is fine manually before proceeding
if importData:
    #sometimes throws error saying no data fetched but can see data in the file
    #could be missing data for some days, better to check the output file before proceeding
    mkt.import_data(tickers, dataSrc, startDt, endDt, rawDataFile)
else:      
    mde = mkt.mde(tickers, en.ReturnFreq.WEEKLY, rawDataFile)
    
    #for ticker in volObj.tickers:
    #    volResult = volObj.volResult[ticker]
    #    plt.plot(pd.DataFrame(volResult.conditional_volatility))
    #    plt.ylabel('cond.vol')    
    #    print("\n##########", ticker, "##########\n", volResult.params)
    #

    mde.prepare_env()
    
    optimalWts = bl.calc_optimal_wt(1.24, mde.covariance, mde.equilibriumWts)
       




