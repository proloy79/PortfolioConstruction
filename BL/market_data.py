# -*- coding: utf-8 -*-
"""

"""
from pandas_datareader import data as web
import os
import pandas as pd
import EDef as en
import vol_fitter as v
import corr_util as cu
import numpy as np

class MktData:
    
    def __init__(self, tickers, returnFreq, startDt, endDt, dataSrc = 'yahoo', storageDir = "."):
        self.returnFreq = returnFreq
        self.startDt = startDt
        self.endDt = endDt
        self.dataSrc = dataSrc
        self.tickers = tickers
        self.storageDir = storageDir        
        self.vols = {}
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
            returns = df
            
            if self.returnFreq == en.ReturnFreq.WEEKLY:
                 returns = df.resample('W', how=lambda x: x[-1])
            elif self.returnFreq == en.ReturnFreq.MONTHLY:   
                returns = df.resample('M', how=lambda x: x[-1])
            elif self.returnFreq == en.ReturnFreq.ANNUALY:   
                returns = df.resample('Y', how=lambda x: x[-1])
                
            returns.to_excel(writer, 'Adj Close')
            writer.save()

    def populate(self):
        self.load_vols()
        self.generate_corr()
        self.create_covariance_matrix()
        
    #reads the data in xl and fits the volatility using GJR-GARCH
    #this fillted vol(s) is saved in dictionary vol and also saved to output/from_to_vol.xlsx
    def load_vols(self):                    
        writer = pd.ExcelWriter(self.fittedVolFile)         
        data = pd.read_excel(self.rawDataFile,sheetname='Adj Close')
        
        volData = {}    
        volData['Date'] = data['Date'][1:]
        print(len(volData['Date']))
        for ticker in self.tickers:            
            vol = v.Vol(ticker, data[ticker])
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
        
        print('\ncorrelations are:')
        print(self.corr) 
        
    def create_covariance_matrix(self):                     
        arr = []
        
        for ticker in self.tickers:            
            arr.append(self.vols[ticker].stdDev[-1])
                               
        darr = np.diag(arr)        
        df = pd.DataFrame(darr, columns=self.tickers)          
        self.covariance = df.cov()
        
        print('\ncovariances are:')
        print(self.covariance) 
            