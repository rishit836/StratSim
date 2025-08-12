import pandas as pd
import numpy as np
import threading

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

def compute_indicators(df:pd.DataFrame):
    thread_process = []
    result = {}

    def _sma_14():
        result['sma_20'] = sma(df['Close'],20)
    def _ema_14():
        result['sma_20'] = sma(df['Close'],20)
    def _rsi_14():
        result['rsi_14'] = rsi(df['Close'],14)

    thread_process.append(threading.Thread(target=_sma_14,name="sma_calculation"))
    thread_process.append(threading.Thread(target=_ema_14,name="ema_calculation"))
    thread_process.append(threading.Thread(target=_rsi_14,name="rsi_calculation"))



    for process in thread_process:
        process.start()
    for process in thread_process:
        process.join()


    return result


