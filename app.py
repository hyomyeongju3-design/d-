import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Global Asset Tracker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 통합 금융 자산 대시보드")
st.caption("AI & Big Data 전공 프로젝트 - 전 세계 주식, 지수, 암호화폐 실시간 트래킹")

st.sidebar.header("📂 종목 라이브러리")

presets = {
    "미국 기술주": "AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META",
    "국내 주요주": "005930.KS, 000660.KS, 035420.KS, 035720.KS, 068270.KS, 096770.KS",
    "시장 지수 & 코인": "^GSPC, ^IXIC, ^DJI, BTC-USD, ETH-USD, KRW=X",
}

selected_preset = st.sidebar.selectbox("프리셋 선택", list(presets.keys()))
custom_input = st.sidebar.text_area("티커 직접 수정", value=presets[selected_preset])
period = st.sidebar.select_slider("조회 기간", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="1y")

@st.cache_data(ttl=3600)
def fetch_multi_data(ticker_str):
    tickers = [t.strip() for t in ticker_str.split(",") if t.strip()]
    all_data = {}
    for t in tickers:
        try:
            df = yf.download(t, period=period, progress=False)
            if not df.empty:
                all_data[t] = df
        except:
            continue
    return all_data

data = fetch_multi_data(custom_input)

if data:
    st.subheader("🚀 주요 종목 요약")
    cols = st.columns(4)
    for i, (ticker, df) in enumerate(data.items()):
        current = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        change = ((current - prev) / prev) * 100
        with cols[i % 4]:
            st.metric(label=ticker, value=f"{current:,.2f}", delta=f"{change:.2f}%")

    st.divider()
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
        st.write("### 🔍 상세 선택")
        target = st.radio("종목 선택", list(data.keys()))
        target_df = data[target]
        st.write(f"**최고가:** {target_df['High'].max():,.2f}")
        st.write(f"**최저가:** {target_df['Low'].min():,.2f}")
        st.write(f"**평균 거래량:** {int(target_df['Volume'].mean()):,}")

    with col_right:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=target_df.index, y=target_df['Close'], mode='lines', name=target, line=dict(color='#00ff88', width=2)))
        fig.update_layout(
            title=f"{target} 주가 변동 추이",
            xaxis_title="날짜",
            yaxis_title="가격",
            template="plotly_dark",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 원본 데이터 프레임 확인"):
        st.dataframe(data[target].sort_index(ascending=False), use_container_width=True)
else:
    st.warning("데이터가 없습니다.")

st.sidebar.info(f"업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
