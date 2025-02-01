import streamlit as st
import pandas as pd
import requests
import sqlite3
from datetime import datetime
import plotly.express as px
import numpy as np
import time

# OpenWeatherMap API Key
API_KEY = "0b29aaa43b791d5ae4bc00380a545acf"

# SQLite database setup
conn = sqlite3.connect("weather_data.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather (
        city TEXT,
        timestamp TEXT,
        temperature REAL
    )
""")
conn.commit()

# List of cities
CITIES = ["Hyderabad,IN", "Mumbai,IN", "Delhi,IN", "Bengaluru,IN", "Chennai,IN"]

# Streamlit layout
st.set_page_config(page_title="Enhanced Weather Dashboard", layout="wide")
st.title("🌍 Enhanced Real-time Weather Dashboard with Insights")
st.write("Monitor and analyze weather data interactively for multiple cities.")

# City selection
selected_city = st.selectbox("Select a City:", CITIES)
st.write(f"Currently selected city: *{selected_city}*")

# Function to fetch weather data
def fetch_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temperature = data['main']['temp']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Save data to database
            cursor.execute("INSERT INTO weather (city, timestamp, temperature) VALUES (?, ?, ?)",
                           (city, timestamp, temperature))
            conn.commit()
            return timestamp, temperature
        else:
            st.error(f"Failed to fetch data: {response.status_code}")
            return None, None
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None, None

# Function to compute data insights
def compute_insights(df):
    if not df.empty:
        # Calculate basic statistics
        avg_temp = df["Temperature"].mean()
        std_temp = df["Temperature"].std()
        
        # Detect anomalies (outside ±2 standard deviations)
        df["Anomaly"] = np.where(
            (df["Temperature"] < avg_temp - 2 * std_temp) |
            (df["Temperature"] > avg_temp + 2 * std_temp),
            "Anomaly",
            "Normal"
        )
        
        # Calculate rolling averages (last 3 data points for simplicity)
        df["Rolling Avg"] = df["Temperature"].rolling(window=3, min_periods=1).mean()
        
        return avg_temp, std_temp, df
    return None, None, df

# Function to update the page continuously
def auto_fetch_and_update():
    # Placeholder for dynamic content
    placeholder_table = st.empty()
    placeholder_graph = st.empty()
    placeholder_insights = st.empty()

    while True:
        # Fetch weather data every 10 seconds
        timestamp, temperature = fetch_weather_data(selected_city)
        if timestamp and temperature:
            st.success(f"New data fetched for {selected_city}: {timestamp} - {temperature}°C")

        # Retrieve historical data for selected city
        cursor.execute("SELECT timestamp, temperature FROM weather WHERE city = ? ORDER BY timestamp ASC", (selected_city,))
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["Timestamp", "Temperature"])

        # Compute insights
        avg_temp, std_temp, df = compute_insights(df)

        # Update insights dynamically
        with placeholder_insights.container():
            st.subheader(f"📊 Insights for {selected_city}")
            if avg_temp is not None:
                st.write(f"*Average Temperature*: {avg_temp:.2f}°C")
                st.write(f"*Standard Deviation*: {std_temp:.2f}°C")
                st.write(f"*Number of Anomalies*: {len(df[df['Anomaly'] == 'Anomaly'])}")
            else:
                st.info("No data available yet.")

        # Update table dynamically
        with placeholder_table.container():
            st.subheader(f"📋 Historical Data for {selected_city}")
            st.dataframe(df)

        # Update graph dynamically
        with placeholder_graph.container():
            if not df.empty:
                st.subheader("📈 Temperature Trend (Interactive)")
                fig = px.line(df, x="Timestamp", y="Temperature", title=f"Temperature Trend for {selected_city}",
                              labels={"Timestamp": "Time", "Temperature": "Temperature (°C)"},
                              markers=True, color="Anomaly")
                fig.update_layout(xaxis=dict(tickangle=45))
                st.plotly_chart(fig)
            else:
                st.info("No data available. Fetch the latest weather data to populate the graph.")

        # Sleep to control the interval (10 seconds)
        time.sleep(10)

# Automatically start the data fetching and updating process
auto_fetch_and_update()
