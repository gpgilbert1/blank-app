import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import io
from PIL import Image
import sqlite3

# Fetch metal prices
def get_metal_price(ticker):
    metal = yf.Ticker(ticker)
    return metal.history(period='1y')['Close'].iloc[-1] / 28

silver_price = get_metal_price('SI=F')
gold_price = get_metal_price('GC=F')

# Fetch historical data
def get_metal_data(ticker):
    data = yf.Ticker(ticker).history(period='1y')
    data.index = pd.to_datetime(data.index)
    return data

# convert image to bianry
def convert_image_to_binary(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

silver_data = get_metal_data('SI=F')
gold_data = get_metal_data('GC=F')

# 🎨 Layout: Logo + Title
col1, col2 = st.columns([1, 4])  # Adjust width ratio

with col1:
    st.image("spectra_logo.jpg", width=200)  # Logo

with col2:
    st.title("Gold & Silver Prices")

sku = st.text_input("Enter SKU Number", "")

email = st.text_input("Enter Email Address", "")

st.write("Current prices per gram:")

# 📊 Layout: Price Metrics & Inputs
col1, col2 = st.columns([1, 2]) 

with col1:
    st.metric(label="Silver Price", value=f"${silver_price:.2f}")
    st.metric(label="Gold Price", value=f"${gold_price:.2f}")

    # User Input
    metal_choice = st.selectbox("Select Metal", ["Silver", "Gold"])
    weight = st.number_input("Enter weight in grams", min_value=0.0, value=0.0, step=0.1)

    # Calculate value
    jewelry_value = silver_price * weight if metal_choice.lower() == "silver" else gold_price * weight
    st.subheader(f"Jewelry Value: ${jewelry_value:.2f}")

    buy_col, sell_col = st.columns(2)

    with buy_col:
        buy_button = st.button("Buy")

    with sell_col:
        sell_button = st.button("Sell")

    if buy_button:
        st.write("You clicked Buy!")

    if sell_button:
        st.write("You clicked Sell!")

    uploaded_file = st.file_uploader("Upload a JPEG image", type=["jpg", "jpeg"])

#if uploaded_file is not None:
    # Open and display the image
    #image = Image.open(uploaded_file)
    #st.image(image, caption = "Uploaded Image", use_column_width = True)

conn = sqlite3.connect("products.db")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,  -- Added email column
        sku TEXT UNIQUE,
        product_name TEXT,
        jewelry_value REAL,  -- Added jewelry value column
        image BLOB
    )
""")
conn.commit()

if st.button("Submit"):
    if email and sku and jewelry_value and uploaded_file:
        # Open image
        image = Image.open(uploaded_file)
        image_binary = convert_image_to_binary(image)
        
        # Display captured data
        st.write(f"Email Address: {email}")
        st.write(f"SKU: {sku}")
        st.write(f"Jewelry Value: {jewelry_value}")
        st.image(image, caption="Uploaded Image", use_column_width=True)
    else:
        st.warning("Please fill in all fields and upload an image before submitting.")

    cursor.execute("INSERT INTO products (email, sku, jewelry_value, image) VALUES (?, ?, ?, ?)", 
                           (email, sku, jewelry_value, image_binary))
    conn.commit()
    st.success("Product saved successfully!")

# 📈 Charts Section
with col2:
    st.subheader("Price Charts")

    def plot_line_chart(data, title):
        plt.figure(figsize=(8, 4))
        plt.plot(data.index, data['Close'], label='Close Price', color="gold" if "Gold" in title else "silver")
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Price / Ounce (USD)')
        plt.grid(True)
        plt.legend()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)  # Reset buffer pointer
        st.image(buf)

    plot_line_chart(silver_data, "Silver Price Chart")
    plot_line_chart(gold_data, "Gold Price Chart")