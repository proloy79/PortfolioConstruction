# -*- coding: utf-8 -*-
"""

"""
from pandas_datareader import data as web
import pandas as pd
import enum_def as en
import vol_fitter as vf
import corr_util as cu
import numpy as np
import quote_ts as qt

def import_data(tickers, dataSrc, startDt, endDt, rawDataFile):        
    writer = pd.ExcelWriter(rawDataFile)        
    for ticker in tickers:
        print(ticker)
        df = web.DataReader(tickers, dataSrc, startDt, endDt)                                    
        df.to_excel(writer)
        writer.save()
        
#market data env class, which will setup the env for the application
class mde:
    
    def __init__(self, tickers, returnFreq, rawDataFile):
        self.returnFreq = returnFreq        
        self.tickers = tickers
        self.rawDataFile = rawDataFile        
        self.vols = {}
        self.returns = {}
        self.equilibriumWts = {}        
    
    #reads the raw data file and creates the right subset based on the required frequency
    def read_xl_db(self, sheetName):          
        data = pd.read_excel(self.rawDataFile,sheetname=sheetName)
        df = data.sort_values('Date')
        df = df.set_index('Date')
        
        #filter out extra tickers if any        
        df = df[self.tickers]        
        #print(df)        
        
        filteredDf = df
        
        if self.returnFreq == en.ReturnFreq.WEEKLY:                        
            filteredDf = df.resample('W').apply(lambda x: x[-1])                
        elif self.returnFreq == en.ReturnFreq.MONTHLY:   
            filteredDf = df.resample('M').apply(lambda x: x[-1])                
        elif self.returnFreq == en.ReturnFreq.ANNUALY:   
            filteredDf = df.resample('Y').apply(lambda x: x[-1])   
        
        #print(filteredDf)    
        
        return filteredDf   
                
#    #reads the tic(s) data from the data source and saves in to a xl file(from_to_dataSrc-data.xlsx)
#    def import_data1(self):          
#        writer = pd.ExcelWriter(self.rawDataFile)        
#        for ticker in self.tickers:
#            print(ticker)
#            yahooData = web.DataReader(self.tickers, self.dataSrc, self.startDt, self.endDt)
#            df = yahooData.ix['Adj Close']            
#            df["Date"] = df.index 
#            #df.drop('Date', axis=1, inplace=True)           
#            quotes = df
#            
#            if self.returnFreq == en.ReturnFreq.WEEKLY:
#                quotes = df.resample('W', how=lambda x: x[-1])                
#            elif self.returnFreq == en.ReturnFreq.MONTHLY:   
#                quotes = df.resample('M', how=lambda x: x[-1])                
#            elif self.returnFreq == en.ReturnFreq.ANNUALY:   
#                quotes = df.resample('Y', how=lambda x: x[-1])     
#                
#            quotes.to_excel(writer, 'Adj Close')
#            writer.save()
               
    def prepare_env(self):        
        self.load_vols()        
        self.load_equlibrium_wts()
        self.create_covariance_matrix()
    
    def load_returns(self):                                    
        df = self.read_xl_db('Adj Close')
        
        for ticker in self.tickers:                        
            rtn = qt.quotes(ticker, df[ticker],  df.index.values)            
            self.returns[ticker] = rtn
    
    def load_equlibrium_wts(self):           
        df = self.read_xl_db('Adj Close')                
        priceRow = df.iloc[1][0:].values                
        df = self.read_xl_db('Volume')        
        volumeRow = df.iloc[1][0:].values        
        marktCap =  np.column_stack(priceRow * volumeRow)
        total = marktCap.sum()
        self.equilibriumWts = np.column_stack(list(map(lambda x: x/total, marktCap)))
                
        print('\nequilibriumWts :')
        print(self.equilibriumWts)
        
    #reads the data in xl and fits the volatility using GJR-GARCH
    #this fillted vol(s) is saved in dictionary vol and also saved to output/from_to_vol.xlsx
    def load_vols(self):                            
        df = self.read_xl_db('Adj Close')
        
        for ticker in self.tickers:            
            vol = vf.vol(ticker, df[ticker])
            vol.fit_vol()
            self.vols[ticker] = vol            
            

# =============================================================================
#     #reads the data in xl and fits the volatility using GJR-GARCH
#     #this fillted vol(s) is saved in dictionary vol and also saved to output/from_to_vol.xlsx
#     def load_vols_old(self):                    
#         writer = pd.ExcelWriter(self.fittedVolFile)         
#         #df = pd.read_excel(self.rawDataFile,sheetname='Adj Close')
#         #data = df.sort_values('Date')
#         df = self.read_xl_db('Adj Close')
#         
#         volData = {}    
#         volData['Date'] = df.index.values[1:]
#         
#         for ticker in self.tickers:            
#             vol = vf.vol(ticker, df[ticker])
#             vol.fit_vol()
#             self.vols[ticker] = vol            
#             volData[ticker] = vol.stdDev           
#         
#         cols = ['Date']
#         cols.extend(self.tickers)
#         #print(volData)
#         allData = pd.DataFrame(volData, columns = cols)
#         allData.to_excel(writer, "vols", index=False)
#         writer.save()  
# =============================================================================
            
    def generate_corr(self):                     
        corrInput = {}
        
        for ticker in self.tickers:            
            corrInput[ticker] = self.vols[ticker].stdDev
                                         
        self.corr = cu.generate_rank_corr(corrInput)
        
        print('\ncorrelations :')
        print(self.corr) 
        
    def create_covariance_matrix(self):                     
        stdDevs = []
        
        for ticker in self.tickers:            
            stdDevs.append(self.vols[ticker].stdDev[-1])
                               
        dStdDevs = np.diag(stdDevs)        
        dfStdDevs = pd.DataFrame(dStdDevs, columns=self.tickers)  
        
        print('\nstd devs :')
        print(dfStdDevs)
        
        self.generate_corr()        
        self.covariance = np.dot(np.dot(dfStdDevs,self.corr),dfStdDevs)
        
        print('\ncovariances :')
        print(self.covariance) 
            