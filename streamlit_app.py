import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Fetch metal prices
def get_metal_price(ticker):
    metal = yf.Ticker(ticker)
    return metal.history(period='1d')['Close'].iloc[-1] / 28

silver_price = get_metal_price('SI=F')
gold_price = get_metal_price('GC=F')

# Fetch historical data
def get_metal_data(ticker):
    data = yf.Ticker(ticker).history(period='1y')
    data.index = pd.to_datetime(data.index)
    return data

silver_data = get_metal_data('SI=F')
gold_data = get_metal_data('GC=F')

# Streamlit UI
st.title("Gold & Silver Price Dashboard")
st.write("Current prices per gram:")
st.metric(label="Silver Price", value=f"${silver_price:.2f}")
st.metric(label="Gold Price", value=f"${gold_price:.2f}")

# User Input
metal_choice = st.selectbox("Select Metal", ["Silver", "Gold"])
weight = st.number_input("Enter weight in grams", min_value=0.0, value=0.0, step=0.1)

# Calculate value
if metal_choice.lower() == "silver":
    jewelry_value = silver_price * weight
else:
    jewelry_value = gold_price * weight

st.subheader(f"Jewelry Value: ${jewelry_value:.2f}")

# Plot price charts
def plot_line_chart(data, title):
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.legend()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)  # Reset buffer pointer
    st.image(buf)

st.subheader("Price Charts")
plot_line_chart(silver_data, "Silver Price Chart")
plot_line_chart(gold_data, "Gold Price Chart")
