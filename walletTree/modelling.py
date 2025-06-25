from sklearn.model_selection import train_test_split
import numpy as np
import pickle
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import os
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
import pickle



def main(ticker,data):
    t = ticker
    def calc_true_range(high,low):
        tr_lst = []
        if len(high) == len(low):
            for i in range(len(high)):
                tr = high[i] - low[i]
                tr_lst.append(tr)
        return tr_lst

    def find_atr(trlst,df,mda=14):
        # mda = moving day average
        i = 0
        thresh = mda
        atr_lst = []
        tot = 0
        while i < len(trlst):
            if i == thresh:
                thresh += mda
                atr = tot/mda
                atr_lst.append(atr)
                tot = 0
            tot += df["gaps"][i]
            i+=1
        return atr_lst

    def create_atrs(data):
        atr_lst = []
        for date in data['date']:
            path = 'data/'+t+"/"+t+"_"+str(date)+".csv"
            if not os.path.exists(path):
                print("data not found for date",date)
            else:
                df = pd.read_csv(path)
                df['gaps'] = calc_true_range(df['high'],df['low'])
                atrs = find_atr(df['gaps'],df)
                atr_lst.append(np.mean(atrs))
        return atr_lst
            
    data['atrs']= create_atrs(data)
    df = data

    def day_column(x):
        indices = np.where(df == x)
        return int(indices[0][0])

    df['day']=df['date'].apply(day_column)

    def target_column(x):
        indices = np.where(df == x)
        index = indices[0][0]
        if x != (df.shape[0]-1):
            return df["Open"][index+1]
        
    df["target"] =df["day"].apply(target_column)
    df.dropna(inplace=True)


    def min_max(x,mini,maxi):
        try:
            return (x-mini)/(maxi-mini)
        except ZeroDivisionError:
            print(maxi,mini)
            return 0

    def prep_data(data):
        data = data[['Open', 'High', 'Low', 'Close','date', 'atrs', 'target']]
        min_max_dict = {}
        for column in data.columns:
            if column.lower() not in ['date']:
                print(column)
                mini = min(data[column])
                maxi = max(data[column])
                data[column]=data[column].apply(min_max,args=[mini,maxi])
                min_max_dict.update({column:[mini,maxi]})
            
        
        print(min_max_dict)
        pickle.dump(min_max_dict,open("min_max_dict.pkl","wb"))
        return data

    def convert_real(x,column):
        d = pickle.load(open("min_max_dict.pkl","rb"))
        if column in d.keys():
            den = d[column][1] - d[column][0]
            return (x*den) + (d[column][0])
        else:
            raise Exception("invalid value to be converted")
        
    df = prep_data(df)

    x_xg_train, x_xg_test, y_xg_train, y_xg_test = train_test_split(df[['Open', 'High', 'Low', 'Close', 'atrs']], df['target'], test_size=0.2, shuffle=False)
    x_xg_train, x_xg_test, y_xg_train, y_xg_test = np.array(x_xg_train), np.array(x_xg_test), np.array(y_xg_train), np.array(y_xg_test)

    model_xg = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6)
    model_xg.fit(x_xg_train, y_xg_train)

    

    pickle.dump(model_xg, open("models/"+t+"_model.pkl","rb"))




