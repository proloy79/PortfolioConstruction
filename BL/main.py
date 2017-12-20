# -*- coding: utf-8 -*-
"""

"""

import datetime as dt
import market_data as mkt
import enum_def as en
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt


dataSrc = 'yahoo'
tickers = ['AAPL', 'ABT', 'AJG', 'APA', 'TEL']
#tickers = ['AAPL']

#uncomment to work with a fresh set if required
#comment the hardcoded dates below
#endDt = dt.date.today()
#startDt =dt.date.today() - relativedelta(years=4)

startDt = dt.date(2012,1,1)
endDt = dt.date(2017,12,17)

mde = mkt.mde(tickers, en.ReturnFreq.WEEKLY, startDt, endDt)

#uncomment if you need to reload the data from yahoo
#mde.import_data()

mde.prepare_env()

#for ticker in volObj.tickers:
#    volResult = volObj.volResult[ticker]
#    plt.plot(pd.DataFrame(volResult.conditional_volatility))
#    plt.ylabel('cond.vol')    
#    print("\n##########", ticker, "##########\n", volResult.params)
#


