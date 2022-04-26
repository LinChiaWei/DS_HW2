


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
    data = pd.concat([train,test],axis=0)
    data.reset_index(inplace=True,drop=True)
    ###

    ### give data corresponding date
    df = pd.date_range(start='2018/03/28',periods=len(data))
    df.format(formatter=lambda x: x.strftime('%Y%m%d'))
    data['date'] = df
    test_start = data['date'][(len(train)-20)]
    data = data[['date','open']]
    data.columns = ['ds','y']
    ###



    ### splitting data to original
    train = data[:-20]
    test = data[-20:]
    ###

    ###training
    lstday = test.iloc[0]['y']
    lsttwoday = train.iloc[-1]['y']
    state = 0
    predict = []
    action = []
    with open(args.output, 'w') as output_file:
        for i in range(20):
            model = Prophet(daily_seasonality=True)
            model.fit(train)
            future = model.make_future_dataframe(periods=1)
            forecast = model.predict(future)
            result = forecast['yhat'][-1:]
            predict.append(result)
            result = result.item()
            if lsttwoday < lstday  and  lstday < result:
                if i == 0 or state == 0:
                    state = -1
                    action.append("-1")
                elif state == 1:
                    state -= 1
                    action.append("-1")
                else:
                    state = state
                    action.append("0")
            elif lsttwoday > lstday and lstday > result:
                if state == 0:
                    state += 1
                    action.append("1")
                elif state == -1:
                    state += 1
                    action.append("1")
                else:
                    state = state
                    action.append("0")
            elif lsttwoday > lstday and lstday < result:
                    state = state
                    action.append("0")
            elif lsttwoday < lstday and lstday > result:
                state = state
                action.append("0")
                lsttwoday = lstday
                lstday = result
            train = train.append(test.iloc[i],ignore_index=True)
    ###
    
    ouput = pd.DataFrame(action)
    ouput.to_csv(args.output,index=False,header=False)