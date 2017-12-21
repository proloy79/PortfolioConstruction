# -*- coding: utf-8 -*-
"""

"""

import datetime as dt
import market_data as mkt
import enum_def as en
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import black_litterman as bl

#set to True if you need to reload the data from yahoo
importData=False
#importData=True

tickers = ['AAPL', 'ABT', 'AJG', 'APA', 'BA', 'BBY', 'FMC', 'TEL']
#tickers = ['AAPL']

#uncomment to work with a fresh set if required
#comment the hardcoded dates below
#endDt = dt.date.today()
#startDt =dt.date.today() - relativedelta(years=4)

startDt = dt.date(2013,1,1)
endDt = dt.date(2017,12,17)

mde = mkt.mde(tickers, en.ReturnFreq.WEEKLY, startDt, endDt)

#for ticker in volObj.tickers:
#    volResult = volObj.volResult[ticker]
#    plt.plot(pd.DataFrame(volResult.conditional_volatility))
#    plt.ylabel('cond.vol')    
#    print("\n##########", ticker, "##########\n", volResult.params)
#

if importData:
    mde.import_data1()

mde.prepare_env()

print('\noptimalWts :')
optimalWts = bl.calc_optimal_wt(1.24, mde.covariance, mde.equilibriumWts)

print(optimalWts)
print(optimalWts - list(mde.equilibriumWts.values()))



