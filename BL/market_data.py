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
                
    def serialize_to_file(self, writer):        
        self.read_xl_db('Adj Close').to_excel(writer, 'Adj Close')                      
        self.read_xl_db('Volume').to_excel(writer, 'Volume')     
         
        params = {}
        logRtns = {}
        stdDevs = {}        
        
        for ticker in self.tickers:                        
            params[ticker] = self.vols[ticker].params             
            logRtns[ticker] = self.vols[ticker].logRtn
            stdDevs[ticker] = self.vols[ticker].conditionalVol                       
            
        pd.DataFrame(params).to_excel(writer, 'VolFitParams',index=params.keys())        
        pd.DataFrame(logRtns).to_excel(writer, 'LogRtns')     
        pd.DataFrame(stdDevs).to_excel(writer, 'ConditionalVol')             
        self.corr.to_excel(writer, 'Corr')        
        self.stdDevMatrix.to_excel(writer, 'StdDevMatrix')        
        pd.DataFrame(self.covariance).to_excel(writer, 'Covariance')
        pd.DataFrame(self.equilibriumWts,index=self.tickers, columns=['EquilibriumWt']).to_excel(writer, 'EqWts')        
        
        writer.save()
        
        
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
        marketCap =  np.column_stack(priceRow * volumeRow)
        total = marketCap.sum()
        self.equilibriumWts = np.column_stack(list(map(lambda x: x/total, marketCap)))
                
        print('\nequilibriumWts :')
        print(self.equilibriumWts)
        
    #reads the data in xl and fits the volatility using GJR-GARCH
    #this fillted vol(s) is saved in dictionary vol and also saved to output/from_to_vol.xlsx
    def load_vols(self):                            
        df = self.read_xl_db('Adj Close')
        debugParams = {}
        
        for ticker in self.tickers:            
            vol = vf.vol(ticker, df[ticker])
            vol.fit_vol()
            self.vols[ticker] = vol            
            debugParams[ticker]  = vol.params
                    
    def generate_corr(self):                     
        corrInput = {}
        
        for ticker in self.tickers:            
            corrInput[ticker] = self.vols[ticker].conditionalVol
                                         
        self.corr = cu.generate_rank_corr(corrInput)
        
        print('\ncorrelations :')
        print(self.corr) 
        
    def create_covariance_matrix(self):                     
        condVols = []
        
        for ticker in self.tickers:            
            condVols.append(self.vols[ticker].conditionalVol[-1])
                               
        diagCondVols = np.diag(condVols)        
        self.stdDevMatrix = pd.DataFrame(diagCondVols,index=self.tickers, columns=self.tickers)  
        
        print('\nconditional vols :')
        print(self.stdDevMatrix)
        
        self.generate_corr()        
        covData = np.dot(np.dot(self.stdDevMatrix,self.corr),self.stdDevMatrix)
        self.covariance = pd.DataFrame(covData,index=self.tickers, columns=self.tickers)
        
        print('\ncovariances :')
        print(self.covariance) 
            