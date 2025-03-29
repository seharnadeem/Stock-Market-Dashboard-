import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern aesthetics
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        color: #444;
    }
    .css-1d391kg {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .css-1cpxqw2 {
        color: #444;
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .css-1r6slb0 {
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #3366FF;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #2952cc;
    }
</style>
""", unsafe_allow_html=True)

# Dashboard header
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://img.icons8.com/fluency/96/null/financial-growth-analysis.png", width=80)
with col2:
    st.title("Stock Market Dashboard")
    st.markdown("*Real-time market data and analysis*")

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("", ["Market Overview", "Stock Analysis", "Technical Indicators"])

# Function to fetch stock data
def fetch_stock_data(symbol, period='1y'):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        return hist, stock.info
    except:
        return None, None

# Market Overview Page
if page == "Market Overview":
    st.header("Market Overview")
    
    # Major indices
    indices = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones",
        "^IXIC": "NASDAQ",
        "^FTSE": "FTSE 100"
    }
    
    # Create columns for indices
    cols = st.columns(len(indices))
    
    for i, (symbol, name) in enumerate(indices.items()):
        with cols[i]:
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                current_price = info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose', 0)
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close > 0 else 0
                
                st.metric(
                    name,
                    f"${current_price:,.2f}",
                    f"{change:+.2f} ({change_pct:+.2f}%)",
                    delta_color="normal"
                )
            except:
                st.metric(name, "N/A")
    
    # Market movers
    st.subheader("Top Market Movers")
    
    # Popular stocks to track
    popular_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT"]
    
    # Create a DataFrame for movers
    movers_data = []
    for symbol in popular_stocks:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            current_price = info.get('regularMarketPrice', 0)
            prev_close = info.get('previousClose', 0)
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close > 0 else 0
            
            movers_data.append({
                'Symbol': symbol,
                'Price': current_price,
                'Change': change,
                'Change %': change_pct,
                'Volume': info.get('regularMarketVolume', 0)
            })
        except:
            continue
    
    movers_df = pd.DataFrame(movers_data)
    if not movers_df.empty:
        # Sort by absolute change percentage
        movers_df['Abs Change %'] = movers_df['Change %'].abs()
        movers_df = movers_df.sort_values('Abs Change %', ascending=False)
        
        # Display movers table
        st.dataframe(
            movers_df[['Symbol', 'Price', 'Change', 'Change %', 'Volume']].style.format({
                'Price': '${:.2f}',
                'Change': '${:+.2f}',
                'Change %': '{:+.2f}%',
                'Volume': '{:,.0f}'
            })
        )
    
    # Market sentiment
    st.subheader("Market Sentiment")
    
    # VIX (Volatility Index)
    try:
        vix = yf.Ticker("^VIX")
        vix_info = vix.info
        vix_price = vix_info.get('regularMarketPrice', 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "VIX (Volatility Index)",
                f"{vix_price:.2f}",
                "Fear & Greed Indicator"
            )
        
        # Interpret VIX
        with col2:
            if vix_price < 20:
                sentiment = "Extreme Greed"
                color = "green"
            elif vix_price < 30:
                sentiment = "Greed"
                color = "lightgreen"
            elif vix_price < 40:
                sentiment = "Neutral"
                color = "yellow"
            elif vix_price < 50:
                sentiment = "Fear"
                color = "orange"
            else:
                sentiment = "Extreme Fear"
                color = "red"
            
            st.markdown(f"""
            <div style="
                background-color: {color};
                color: white;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
            ">
                <h3 style="margin:0">{sentiment}</h3>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.warning("Unable to fetch market sentiment data")

# Stock Analysis Page
elif page == "Stock Analysis":
    st.header("Stock Analysis")
    
    # Stock search
    stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):", "AAPL").upper()
    
    if stock_symbol:
        with st.spinner(f"Fetching data for {stock_symbol}..."):
            hist, info = fetch_stock_data(stock_symbol)
            
            if hist is not None and info is not None:
                # Company info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Current Price",
                        f"${info.get('regularMarketPrice', 0):.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Market Cap",
                        f"${info.get('marketCap', 0) / 1e9:.2f}B"
                    )
                
                with col3:
                    st.metric(
                        "Volume",
                        f"{info.get('regularMarketVolume', 0):,.0f}"
                    )
                
                # Price chart
                st.subheader("Price History")
                
                # Time period selector
                time_period = st.radio(
                    "Select Time Period:",
                    ["1 Month", "3 Months", "6 Months", "1 Year", "5 Years"],
                    horizontal=True
                )
                
                period_mapping = {
                    "1 Month": "1mo",
                    "3 Months": "3mo",
                    "6 Months": "6mo",
                    "1 Year": "1y",
                    "5 Years": "5y"
                }
                
                # Fetch data for selected period
                hist = yf.Ticker(stock_symbol).history(period=period_mapping[time_period])
                
                # Create candlestick chart
                fig = go.Figure(data=[go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close']
                )])
                
                fig.update_layout(
                    title=f"{stock_symbol} Stock Price",
                    yaxis_title="Price ($)",
                    xaxis_title="Date",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Company info
                st.subheader("Company Information")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **Company Name:** {info.get('longName', 'N/A')}  
                    **Sector:** {info.get('sector', 'N/A')}  
                    **Industry:** {info.get('industry', 'N/A')}  
                    **Country:** {info.get('country', 'N/A')}  
                    **Exchange:** {info.get('exchange', 'N/A')}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **52 Week High:** ${info.get('fiftyTwoWeekHigh', 'N/A')}  
                    **52 Week Low:** ${info.get('fiftyTwoWeekLow', 'N/A')}  
                    **Average Volume:** {info.get('averageVolume', 'N/A'):,.0f}  
                    **P/E Ratio:** {info.get('trailingPE', 'N/A'):.2f}  
                    **Dividend Yield:** {info.get('dividendYield', 0) * 100:.2f}%
                    """)
                
                # Business summary
                st.markdown("### Business Summary")
                st.write(info.get('longBusinessSummary', 'No information available'))
            else:
                st.error(f"Unable to fetch data for {stock_symbol}")

# Technical Indicators Page
elif page == "Technical Indicators":
    st.header("Technical Indicators")
    
    # Stock selection
    stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):", "AAPL").upper()
    
    if stock_symbol:
        with st.spinner(f"Calculating technical indicators for {stock_symbol}..."):
            hist, info = fetch_stock_data(stock_symbol)
            
            if hist is not None:
                # Calculate technical indicators
                # RSI
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                # MACD
                exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
                exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                
                # Bollinger Bands
                sma = hist['Close'].rolling(window=20).mean()
                std = hist['Close'].rolling(window=20).std()
                upper_band = sma + (std * 2)
                lower_band = sma - (std * 2)
                
                # Create subplots
                fig = go.Figure()
                
                # Add candlestick chart
                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name='Price'
                ))
                
                # Add Bollinger Bands
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=upper_band,
                    name='Upper BB',
                    line=dict(color='gray', dash='dash')
                ))
                
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=lower_band,
                    name='Lower BB',
                    line=dict(color='gray', dash='dash')
                ))
                
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=sma,
                    name='SMA 20',
                    line=dict(color='blue')
                ))
                
                fig.update_layout(
                    title=f"{stock_symbol} Price with Bollinger Bands",
                    yaxis_title="Price ($)",
                    xaxis_title="Date",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # RSI Chart
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(
                    x=hist.index,
                    y=rsi,
                    name='RSI',
                    line=dict(color='purple')
                ))
                
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                
                fig_rsi.update_layout(
                    title="Relative Strength Index (RSI)",
                    yaxis_title="RSI",
                    xaxis_title="Date",
                    height=300
                )
                
                st.plotly_chart(fig_rsi, use_container_width=True)
                
                # MACD Chart
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(
                    x=hist.index,
                    y=macd,
                    name='MACD',
                    line=dict(color='blue')
                ))
                
                fig_macd.add_trace(go.Scatter(
                    x=hist.index,
                    y=signal,
                    name='Signal',
                    line=dict(color='orange')
                ))
                
                fig_macd.update_layout(
                    title="MACD",
                    yaxis_title="MACD",
                    xaxis_title="Date",
                    height=300
                )
                
                st.plotly_chart(fig_macd, use_container_width=True)
                
                # Current indicator values
                st.subheader("Current Indicator Values")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    current_rsi = rsi.iloc[-1]
                    st.metric(
                        "RSI",
                        f"{current_rsi:.2f}",
                        "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"
                    )
                
                with col2:
                    current_macd = macd.iloc[-1]
                    current_signal = signal.iloc[-1]
                    st.metric(
                        "MACD",
                        f"{current_macd:.2f}",
                        "Bullish" if current_macd > current_signal else "Bearish"
                    )
                
                with col3:
                    current_price = hist['Close'].iloc[-1]
                    current_bb_position = (current_price - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1]) * 100
                    st.metric(
                        "BB Position",
                        f"{current_bb_position:.1f}%",
                        "Upper" if current_bb_position > 80 else "Lower" if current_bb_position < 20 else "Middle"
                    )
            else:
                st.error(f"Unable to fetch data for {stock_symbol}")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #eee;">
    <p style="color: #666;">Stock Market Dashboard - Created with Streamlit</p>
    <p style="color: #999; font-size: 0.8em;">Data provided by Yahoo Finance</p>
</div>
""", unsafe_allow_html=True)