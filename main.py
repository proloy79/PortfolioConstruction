# -*- coding: utf-8 -*-
"""

"""

import datetime as dt
#from dateutil.relativedelta import relativedelta
import market_data as mkt
import matplotlib.pyplot as plt
import pandas as pd
import EDef as en

dataSrc = 'yahoo'
tickers = ['AAPL', 'MSFT', '^GSPC']
#tickers = ['AAPL']

#uncomment to work with a fresh set if required
#comment the hardcoded dates below
#endDt = dt.date.today()
#startDt =dt.date.today() - relativedelta(years=4)

startDt = dt.date(2013,12,18)
endDt = dt.date(2017,12,17)

mktData = mkt.MktData(tickers, en.ReturnFreq.WEEKLY, startDt, endDt)

#uncomment if you need to reload the data from yahoo
#mktData.import_data()

mktData.populate()

#for ticker in volObj.tickers:
#    volResult = volObj.volResult[ticker]
#    plt.plot(pd.DataFrame(volResult.conditional_volatility))
#    plt.ylabel('cond.vol')    
#    print("\n##########", ticker, "##########\n", volResult.params)
#


