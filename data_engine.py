import akshare as ak
import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta

class DataEngine:
    """
    数据引擎：负责从 AkShare 获取 A 股数据并计算基础因子
    """
    def __init__(self):
        pass

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str):
        """
        获取个股日线复权数据
        symbol: 6位股票代码，如 '000001'
        """
        try:
            # 默认获取前复权数据
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
            if df.empty:
                return None
            
            # 修复列名映射，AkShare 返回 12 列
            # ['日期', '股票代码', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            df.columns = ['date', 'code', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'pct_chg', 'change', 'turnover']
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 确保数值列为 float
            numeric_cols = ['open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'pct_chg', 'change', 'turnover']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
            
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def add_technical_factors(self, df):
        """
        添加常用技术指标因子
        """
        if df is None or df.empty:
            return df
        
        # 均线系统
        df['MA5'] = talib.SMA(df['close'], timeperiod=5)
        df['MA20'] = talib.SMA(df['close'], timeperiod=20)
        df['MA60'] = talib.SMA(df['close'], timeperiod=60)
        
        # 动量指标
        df['RSI'] = talib.RSI(df['close'], timeperiod=14)
        
        # 趋势指标
        macd, macdsignal, macdhist = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        df['MACD'] = macd
        df['MACD_signal'] = macdsignal
        df['MACD_hist'] = macdhist
        
        # 波动率
        df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        
        # 布林带
        upper, middle, lower = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        df['BB_upper'] = upper
        df['BB_middle'] = middle
        df['BB_lower'] = lower
        
        return df

    def get_market_snapshot(self):
        """
        获取全市场实时快照（用于选股）
        """
        try:
            df = ak.stock_zh_a_spot_em()
            return df
        except Exception as e:
            print(f"Error fetching market snapshot: {e}")
            return None

if __name__ == "__main__":
    # 测试代码
    engine = DataEngine()
    test_df = engine.get_stock_daily("000001", "20240101", "20250101")
    if test_df is not None:
        test_df = engine.add_technical_factors(test_df)
        print("数据获取及因子计算成功！")
        print(test_df.tail())
    else:
        print("数据获取失败，请检查网络或代码。")
