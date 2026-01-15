import vectorbt as vbt
import pandas as pd
import numpy as np

class BacktestEngine:
    """
    回测引擎：基于 VectorBT 实现高性能策略回测
    """
    def __init__(self):
        pass

    def run_ma_crossover_strategy(self, df, fast_ma=5, slow_ma=20):
        """
        双均线交叉策略回测
        """
        if df is None or df.empty:
            return None
        
        # 计算均线
        fast_ma_series = df['close'].rolling(window=fast_ma).mean()
        slow_ma_series = df['close'].rolling(window=slow_ma).mean()
        
        # 生成信号：金叉买入，死叉卖出
        entries = (fast_ma_series > slow_ma_series) & (fast_ma_series.shift(1) <= slow_ma_series.shift(1))
        exits = (fast_ma_series < slow_ma_series) & (fast_ma_series.shift(1) >= slow_ma_series.shift(1))
        
        # 执行回测
        # 修复参数：VectorBT 0.28.2 中 init_cash 代替 cash
        portfolio = vbt.Portfolio.from_signals(
            df['close'], 
            entries, 
            exits, 
            fees=0.001,      # 假设千分之一手续费
            init_cash=100000, # 初始资金 10万
            freq='D'
        )
        
        return portfolio

    def get_stats(self, portfolio):
        """
        获取回测统计指标
        """
        if portfolio is None:
            return {}
        
        return portfolio.stats()

if __name__ == "__main__":
    # 测试回测引擎
    from data_engine import DataEngine
    engine = DataEngine()
    df = engine.get_stock_daily("000001", "20230101", "20250101")
    
    bt_engine = BacktestEngine()
    pf = bt_engine.run_ma_crossover_strategy(df)
    
    if pf is not None:
        print("回测成功！")
        print(pf.stats())
    else:
        print("回测失败。")
