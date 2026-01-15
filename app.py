import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_engine import DataEngine
from backtest_engine import BacktestEngine
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(page_title="Manus 量化交易工具 (2026)", layout="wide")

st.title("📈 中国股市量化交易分析系统")
st.markdown("---")

# 初始化引擎
@st.cache_resource
def get_engines():
    return DataEngine(), BacktestEngine()

data_engine, bt_engine = get_engines()

# 侧边栏配置
st.sidebar.header("参数设置")
symbol = st.sidebar.text_input("股票代码 (如 000001)", value="000001")
start_date = st.sidebar.date_input("开始日期", value=datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("结束日期", value=datetime.now())

strategy_type = st.sidebar.selectbox("选择策略", ["双均线交叉", "RSI 超买超卖"])
fast_ma = st.sidebar.slider("短周期均线", 5, 60, 5)
slow_ma = st.sidebar.slider("长周期均线", 10, 120, 20)

# 主界面
tab1, tab2, tab3 = st.tabs(["行情分析", "策略回测", "选股器"])

with tab1:
    st.subheader(f"股票行情: {symbol}")
    with st.spinner("正在获取数据..."):
        df = data_engine.get_stock_daily(symbol, start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
        
    if df is not None:
        df = data_engine.add_technical_factors(df)
        
        # 绘制 K 线图
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name='K线')])
        
        # 添加均线
        fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], name='MA5', line=dict(color='orange', width=1)))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20', line=dict(color='blue', width=1)))
        
        fig.update_layout(title=f"{symbol} 历史行情", xaxis_rangeslider_visible=False, height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.error("无法获取数据，请检查股票代码或日期范围。")

with tab2:
    st.subheader("策略回测表现")
    if df is not None:
        with st.spinner("正在运行回测..."):
            pf = bt_engine.run_ma_crossover_strategy(df, fast_ma, slow_ma)
            
        if pf is not None:
            col1, col2, col3, col4 = st.columns(4)
            stats = pf.stats()
            col1.metric("总收益率", f"{stats['Total Return [%]']:.2f}%")
            col2.metric("年化收益率", f"{stats['Benchmark Return [%]']:.2f}%")
            col3.metric("最大回撤", f"{stats['Max Drawdown [%]']:.2f}%")
            col4.metric("夏普比率", f"{stats['Sharpe Ratio']:.2f}")
            
            # 绘制收益曲线
            st.subheader("累计收益曲线")
            fig_ret = go.Figure()
            fig_ret.add_trace(go.Scatter(x=pf.cumulative_returns().index, y=pf.cumulative_returns(), name='策略收益'))
            fig_ret.update_layout(height=400)
            st.plotly_chart(fig_ret, use_container_width=True)
        else:
            st.error("回测运行失败。")

with tab3:
    st.subheader("全市场实时快照 (Top 50)")
    if st.button("刷新市场数据"):
        with st.spinner("正在获取全市场数据..."):
            market_df = data_engine.get_market_snapshot()
            if market_df is not None:
                st.dataframe(market_df.head(50), use_container_width=True)
            else:
                st.error("获取市场快照失败。")

st.sidebar.markdown("---")
st.sidebar.info("本工具仅供学习研究使用，不构成投资建议。")
