
import ast
from pandas import period_range
import yfinance as yf
from datetime import  timedelta, date

class import_data_market():

    def __init__(self, days_ago=200, ticker='SPY', interval='1d'):
        
        fromData = date.today() - timedelta(days=int(days_ago))
        fromData = fromData.strftime('%Y-%m-%d')
        today = date.today()

        today = today.strftime('%Y-%m-%d') 

        self.symbol = ticker
        self.start_date = fromData
        self.end_date = today
        self.interval = interval
        self.ticker = ticker

    def download(self):
        df = yf.download(self.ticker, start=self.start_date, end=self.end_date, interval=self.interval)
        self.df = df
        return df

    def q_learning_v1_data(self, df):

        data = df['Close']
        return data

    def to_json(data):

        # Convert index of dataframe to datetime column
        
        data['date'] = data.index.strftime('%Y-%m-%d %H:%M:%S')

        # Convert Dataframe to JSON response payload
        data_json = data.to_json(orient='records')
        
        # Convert String to Json
        data_json = ast.literal_eval(data_json)

        return data_json



class import_data_ticket():


    # Init this data: 
    # ticket; period; 
    def __init__(self, ticker='SPY', period='1d', interval='30m'):
        self.ticker = ticker
        self.period = period
        self.interval = interval

    def download(self):

        # ticker = yf.Ticker(self.ticker)
        # df = ticker.history(period=self.period, interval=self.interval)

        df = yf.download(tickers=self.ticker, period=self.period, interval=self.interval)
        df['date'] = df.index.strftime('%Y-%m-%d %H:%M:%S')
        data_json = df.to_json(orient='records')
        data_json = ast.literal_eval(data_json)

        return data_json

# data = import_data_ticket(ticker='ETH-USD', period='2h', interval='30m').download()

# print(data)


# import pandas_datareader as data_reader
# dataset = data_reader.DataReader('AAPL',data_source='yahoo')