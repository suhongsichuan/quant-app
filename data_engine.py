import akshare as ak
import pandas as pd
import pandas_ta as ta  # 切换到兼容性更好的 pandas_ta
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
        # 使用 pandas_ta 计算指标，这些指标与 TA-Lib 完全一致
        df['MA5'] = ta.sma(df['close'], length=5)
        df['MA20'] = ta.sma(df['close'], length=20)
        df['MA60'] = ta.sma(df['close'], length=60)
        df['RSI'] = ta.rsi(df['close'], length=14)
        
        macd = ta.macd(df['close'])
        df['MACD'] = macd['MACD_12_26_9']
        df['MACD_signal'] = macd['MACDs_12_26_9']
        df['MACD_hist'] = macd['MACDh_12_26_9']
        
        df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        bbands = ta.bbands(df['close'], length=20, std=2)
        df['BB_upper'] = bbands['BBU_20_2.0']
        df['BB_middle'] = bbands['BBM_20_2.0']
        df['BB_lower'] = bbands['BBL_20_2.0']
        return df

    def get_market_snapshot(self):
        try:
            return ak.stock_zh_a_spot_em()
        except:
            return None
