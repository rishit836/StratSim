import pandas as pd
import numpy as np
import threading
import math

def sma(series:pd.Series, period:int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).mean()

def ema(series:pd.Series,period:int)->pd.Series:
    return series.ewm(span=period,adjust=False, min_periods=period).period()

def rsi(close:pd.Series,period:int=14)->pd.Series:
    delta = close.diff()
    gain=np.where(delta>0,delta,0.0)
    loss = np.where(delta<0,-delta,0.0)
    gain_ema = pd.Series(gain,index=close.index).ewm(alpha=1/period,adjust=False,min_periods=period).mean()
    loss_ema = pd.Series(loss,index=close.index).ewm(alpha=1/period,adjust=False,min_periods=period).mean()
    rs = gain_ema/loss_ema
    return 100 - (100 /(1+rs))

def MACD(close:pd.Series):
    ema_26 = ema(close,26)
    ema_12 = ema(close,12)
    ema_9  = ema(close,9)
    macd = []
    for val1, val2 in zip(ema_26,ema_12):
        macd.append(val1-val2)
    macd_signal_line = ema(pd.Series(macd),9)

    return macd_signal_line

def bullish_bearish_trend(close:pd.Series)->float:
    """
    returns a score out of 100, 100 being bullish and 0 being bearish
    the stock can be in between too
    """
    weights = {
        "rsi":40,
        "ema":30,
        "sma":30,
    }

    
    return 0

def compute_indicators(df:pd.DataFrame):
    thread_process = []
    result = {}

    def _sma_14():
        result['sma_20'] = sma(df['Close'],20)
    def _ema_14():
        result['sma_20'] = sma(df['Close'],20)
    def _rsi_14():
        result['rsi_14'] = rsi(df['Close'],14)
    def _macd():
        result['macd'] = MACD(df['Close'])

    thread_process.append(threading.Thread(target=_sma_14,name="sma_calculation"))
    thread_process.append(threading.Thread(target=_ema_14,name="ema_calculation"))
    thread_process.append(threading.Thread(target=_rsi_14,name="rsi_calculation"))



    for process in thread_process:
        process.start()
    for process in thread_process:
        process.join()


    return result


