# -*- coding: utf-8 -*-
"""

"""
from pandas_datareader import data as web
import os
import pandas as pd
import enum_def as en
import vol_fitter as vf
import corr_util as cu
import numpy as np
import quote_ts as qt

#market data env class, which will setup the env for the application
class mde:
    
    def __init__(self, tickers, returnFreq, startDt, endDt, dataSrc = 'yahoo', storageDir = "."):
        self.returnFreq = returnFreq
        self.startDt = startDt
        self.endDt = endDt
        self.dataSrc = dataSrc
        self.tickers = tickers
        self.storageDir = storageDir        
        self.vols = {}
        self.returns = {}
        self.equilibriumWts = {}
        stDtS = startDt.strftime('%Y%m%d')
        endDtS = endDt.strftime('%Y%m%d')
        self.rawDataFile = os.path.join(os.path.realpath(self.storageDir), stDtS + '_' + endDtS 
                                  + '_' + dataSrc + '-data.xlsx')  
        outputDir = os.path.join(os.path.realpath(self.storageDir),'output')
        self.fittedVolFile = os.path.join(outputDir, stDtS + '_' + endDtS 
                                  + '_' + 'vols.xlsx')        
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
            
    #reads the tic(s) data from the data source and saves in to a xl file(from_to_dataSrc-data.xlsx)
    def import_data(self):          
        writer = pd.ExcelWriter(self.rawDataFile)        
        for ticker in self.tickers:
            print(ticker)
            yahooData = web.DataReader(self.tickers, self.dataSrc, self.startDt, self.endDt)
            df = yahooData.ix['Adj Close']
            df["Date"] = df.index 
            df.drop('Date', axis=1, inplace=True)           
            quotes = df
            
            if self.returnFreq == en.ReturnFreq.WEEKLY:
                quotes = df.resample('W', how=lambda x: x[-1])                
            elif self.returnFreq == en.ReturnFreq.MONTHLY:   
                quotes = df.resample('M', how=lambda x: x[-1])                
            elif self.returnFreq == en.ReturnFreq.ANNUALY:   
                quotes = df.resample('Y', how=lambda x: x[-1])     
                
            quotes.to_excel(writer, 'Adj Close')
            writer.save()

    def prepare_env(self):
        self.load_weights()
        #self.load_vols()        
        #self.create_covariance_matrix()
    
    def load_returns(self):                                    
        data = pd.read_excel(self.rawDataFile,sheetname='Adj Close')
            
        for ticker in self.tickers:                        
            rtn = qt.quotes(ticker, data[ticker],  data['Date'])
            self.returns[ticker] = rtn
    
    def load_weights(self):  
        xlData = pd.read_excel("../IdxWeight.xlsx",sheetname='IdxWt')                                          
        df = pd.DataFrame(xlData)
        df = df.drop(axis=1,labels=['Name','Sector'])
        df = df.set_index('Symbol')
        
        for ticker in self.tickers:                                                
            self.equilibriumWts[ticker] = df.get_value(ticker, 'Weight')
        
        print('\nweights :')
        print(self.wts)    
        
    #reads the data in xl and fits the volatility using GJR-GARCH
    #this fillted vol(s) is saved in dictionary vol and also saved to output/from_to_vol.xlsx
    def load_vols(self):                    
        writer = pd.ExcelWriter(self.fittedVolFile)         
        data = pd.read_excel(self.rawDataFile,sheetname='Adj Close')
        
        volData = {}    
        volData['Date'] = data['Date'][1:]
        
        for ticker in self.tickers:            
            vol = vf.vol(ticker, data[ticker])
            vol.fit_vol()
            self.vols[ticker] = vol            
            volData[ticker] = vol.stdDev           
        
        cols = ['Date']
        cols.extend(self.tickers)
        #print(volData)
        allData = pd.DataFrame(volData, columns = cols)
        allData.to_excel(writer, "vols", index=False)
        writer.save()                     
            
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
            