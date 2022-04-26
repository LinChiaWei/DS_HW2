


if __name__ == '__main__':
    import argparse


    parser = argparse.ArgumentParser()
    parser.add_argument('--training',
                       default='training_data.csv',
                       help='input training data file name')
    parser.add_argument('--testing',
                        default='testing_data.csv',
                        help='input testing data file name')
    parser.add_argument('--output',
                        default='output.csv',
                        help='output file name')
    args = parser.parse_args()
    
# The following part is an example.
# You can modify it at will.

    import numpy as np
    import pandas as pd
    import pandas_datareader as pdr
    import matplotlib.pyplot as plt
    import datetime as datetime
    from fbprophet import Prophet
    from sklearn import metrics
    from pandas import to_datetime
    from math import sqrt
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    import plotly.graph_objects as go

    ### read data
    train = pd.read_csv(args.training,header=None)
    test = pd.read_csv(args.testing,header=None)
    train = train.set_axis(['open','high','low','close'],axis=1,inplace=False)
    test = test.set_axis(['open','high','low','close'],axis=1,inplace=False)
    ###

    ### give data corresponding date
    df = pd.date_range('2018/03/28','2022/04/23')
    df2 = pd.date_range('2022/04/24','2022/05/13')
    df.format(formatter=lambda x: x.strftime('%Y%m%d'))
    df2.format(formatter=lambda x: x.strftime('%Y%m%d'))
    train['date']=df
    test['date']=df2
    train_len = len(df)
    ###
 
    data = pd.concat([train,test],axis=0)
    data.reset_index(inplace=True,drop=True)
    df = data
    df.index = df.date

    ### calculate features
    def relative_strength_idx(df,n=14):
        open = df['open']
        delta = open.diff()
        delta = delta[1:]
        pricesUp = delta.copy()
        pricesDown = delta.copy()
        pricesUp[pricesUp < 0] = 0
        pricesDown[pricesDown > 0] = 0
        rollUp = pricesUp.rolling(n).mean()
        rollDown = pricesDown.abs().rolling(n).mean()
        rs = rollUp / rollDown
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi

    df['EMA_3'] = df['open'].ewm(3).mean().shift()
    df['EMA_7'] = df['open'].ewm(7).mean().shift()
    df['EMA_30'] = df['open'].ewm(30).mean().shift()

    df['SMA_3'] = df['open'].rolling(3).mean().shift()
    df['SMA_7'] = df['open'].rolling(7).mean().shift()
    df['SMA_30'] = df['open'].rolling(30).mean().shift()

    df['RSI'] = relative_strength_idx(df).fillna(0)

    EMA_12 = pd.Series(df['open'].ewm(span=12, min_periods=12).mean())
    EMA_26 = pd.Series(df['open'].ewm(span=26, min_periods=26).mean())
    df['MACD'] = pd.Series(EMA_12 - EMA_26)
    df['MACD_signal'] = pd.Series(df.MACD.ewm(span=9, min_periods=9).mean())
    ###

    ### splitting data to original
    df['y'] = df['open'].shift(-1)
    df = df.dropna(axis=0).reset_index(drop=True)

    df_train = df[df.date<="2022-04-23"]
    df_valid = df[df.date>"2022-04-23"]
    ###

    features = ['SMA_3','SMA_7','SMA_30','EMA_3','EMA_7','EMA_30','RSI','MACD','MACD_signal']

    ### training
    model = Prophet()
    for feature in features:
        model.add_regressor(feature)

    model.fit(df_train[["date", "y"] + features].rename(columns={"date": "ds", "y": "y"}))
    forecast = model.predict(df_valid[["date", "y"] + features].rename(columns={"date": "ds"}))
    df_valid["Forecast_Prophet"] = forecast.yhat.values
    results = []
    results.append(forecast.yhat.values)
    result = np.reshape(results,19)
    ###

    ### stock action predict algorithm
    state = 0
    action = []
    with open(args.output, 'w') as output_file:
        for i in range(1,17):
            print(state)
            todayprice = result[i]
            if result[i+1] > todayprice and result[i+2] > todayprice:
                if i == 1 or state == 0:
                    state += 1
                    action.append("1")
                elif state == -1:
                    state += 1
                    action.append("1")
                else:
                    state = state
                    action.append("0")
            elif result[i+1] < todayprice and result[i+2] < todayprice:
                if state == 1:
                    state -= 1
                    action.append("-1")
                elif state == 0:
                    state -= 1
                    action.append("-1")
                else:
                    state = state
                    action.append("0")
            elif result[i+1] > todayprice and result[i+2] < todayprice:
                state = state
                action.append("0")
            elif result[i+1] < todayprice and result[i+2] > todayprice:
                state = state
                action.append("0")

    if result[18] < result [17]:
        if state == 1:
            state -= 1
            action.append("-1")
            action.append("0")
            action.append("0")
        elif state == 0:
            state -= 1
            action.append("-1")
            action.append("0")
            action.append("0")
        else:
            state += 1 
            action.append("1")
            action.append("0")
            action.append("0")
    else:
        if state == -1:
            state += 1
            action.append("1")
            action.append("0")
            action.append("0")
        else:
            state = state
            action.append("0")
            action.append("0")
            action.append("0")
    ###
    
    ouput = pd.DataFrame(action)
    ouput.to_csv(args.output,index=False,header=False)