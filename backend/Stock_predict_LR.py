# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import lightgbm as lgb
import xgboost as xgb
import warnings
import yfinance as yf 
import pandas as pd

warnings.filterwarnings('ignore')
sns.set(style="whitegrid")


def stock_predict(ticker):
    
    #나스닥 파일 불러오기
    data_path = 'data/nasdq_20241104.csv'
    data = pd.read_csv(data_path)

    
    start_date = '2010-01-04'
    end_date = '2024-10-25'
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    
    #AAPL 데이터 전처리
    stock_data.reset_index(inplace=True)
    stock_data['Date'] = stock_data['Date'].dt.strftime('%Y-%m-%d')
    stock_data.columns = ['Date', 'Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']
    stock_data.drop(columns=['Adj Close'], inplace=True)
    
    #Nasdaq 데이터 전처리
    #global_data = data.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume'])

    #AAPL, Nasdaq merge
    stock_merge_data = pd.merge(stock_data, data, on='Date', how='inner')

    #merge data 전처리
    stock_merge_data['Date'] = pd.to_datetime(stock_merge_data['Date'])
    stock_merge_data.set_index('Date', inplace=True)
    stock_merge_data.columns = stock_merge_data.columns.str.replace(' ', '')

    stock_merge_data['Close_InterestRate_Corr'] = stock_merge_data['Close'].rolling(252).corr(stock_merge_data['InterestRate'])
    stock_merge_data['Close_VIX_Corr'] = stock_merge_data['Close'].rolling(252).corr(stock_merge_data['VIX'])
    stock_merge_data['Rolling_Volatility'] = stock_merge_data['Close'].rolling(window=30).std()

    stock_merge_data['Daily_Return'] = stock_merge_data['Close'].pct_change()
    stock_merge_data['Volatility'] = stock_merge_data['Close'].rolling(window=30).std() # 이동 표준 편차를 계산하라
    stock_merge_data['Rolling_Mean_Close'] = stock_merge_data['Close'].rolling(window=30).mean()
    stock_merge_data.dropna(inplace=True)
    
    # Step 1: Replace infinite values with NaN
    stock_merge_data.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Step 2: Check for NaN values and handle them
    # Using forward fill to handle NaN values (you can adjust this as needed)
    stock_merge_data.fillna(method='ffill', inplace=True)

    return stock_merge_data

    # # 여기까지 하고 Azure Designer로 이동해서 처리
    # # //////////////////////////////////////////
    # X = stock_merge_data.drop(['Close', 'High', 'Low', 'Volume'], axis=1)  # Ensure 'Close' is dropped to create the feature set
    # y = stock_merge_data['Close']  # Target variable is 'Close' price
    
    # # Step 3: Standardize the data
    # scaler = StandardScaler()
    # scaler.fit_transform(X)


    # # Step 4: Split the data into training and testing sets
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # # Step 4: Standardize the data
    # #scaler = StandardScaler()
    # #scaler.fit(X_train)
    # #X_train_scaled = scaler.transform(X_train)
    # #X_test_scaled = scaler.transform(X_test)


    # # LR
    # lr = LinearRegression()
    # lr.fit(X_train, y_train)

    # # Make predictions
    # y_pred_lr = lr.predict(X_test)

   