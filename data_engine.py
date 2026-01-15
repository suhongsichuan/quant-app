import akshare as ak
import pandas as pd
import pandas_ta as ta
from datetime import datetime

class DataEngine:
    def __init__(self):
        pass

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str):
        try:
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
            if df.empty: return None
            df.columns = ['date', 'code', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'pct_chg', 'change', 'turnover']
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            numeric_cols = ['open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'pct_chg', 'change', 'turnover']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
            return df
        except Exception as e:
            print(f"Error: {e}")
            return None

    def add_technical_factors(self, df):
        if df is None or df.empty: return df
        
        # 基础指标
        df['MA5'] = ta.sma(df['close'], length=5)
        df['MA20'] = ta.sma(df['close'], length=20)
        df['MA60'] = ta.sma(df['close'], length=60)
        df['RSI'] = ta.rsi(df['close'], length=14)
        
        # MACD 处理
        macd = ta.macd(df['close'])
        if macd is not None:
            df['MACD'] = macd.iloc[:, 0]  # 取第一列
            df['MACD_signal'] = macd.iloc[:, 2]  # 取第三列
            df['MACD_hist'] = macd.iloc[:, 1]  # 取第二列
        
        # ATR 处理
        df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        # 布林带处理 (修复 KeyError 的核心逻辑)
        bbands = ta.bbands(df['close'], length=20, std=2)
        if bbands is not None:
            # 使用 iloc 索引而不是字符串列名，彻底避免 KeyError
            df['BB_lower'] = bbands.iloc[:, 0]   # Lower Band
            df['BB_middle'] = bbands.iloc[:, 1]  # Mid Band
            df['BB_upper'] = bbands.iloc[:, 2]   # Upper Band
            
        return df

    def get_market_snapshot(self):
        try:
            return ak.stock_zh_a_spot_em()
        except:
            return None
