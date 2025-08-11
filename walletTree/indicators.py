import pandas as pd
import numpy as np
import threading

def sma(series:pd.Series, period:int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).mean()

def ema(series:pd.Series,period:int)->pd.Series:
    return series.ewm(span=period,adjust=False, min_periods=period).period()

def rsi(close:pd.Series,period:int=14)->pd.Series:
    delta = close.difF()
    gain=np.where(delta>0,delta,0.0)
    loss = np.where(delta<0,-delta,0.0)
    gain_ema = pd.Series(gain,index=close.index).ewm(alpha=1/period,adjust=False,min_periods=period).mean()
    loss_ema = pd.Series(loss,index=close.index).ewm(alpha=1/period,adjust=False,min_periods=period).mean()
    rs = gain_ema/loss_ema
    return 100 - (100 /(1+rs))

def compute_indicators(df:pd.DataFrame):
    sma_calc = threading.Thread(target=sma,args=(df['close']))
    sma_calc.start()

