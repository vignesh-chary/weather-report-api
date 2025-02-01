import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import requests
import schedule
import time
from datetime import datetime

# Your OpenWeatherMap API key
API_KEY = ""
city = "Hyderabad,IN"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

# Initialize lists to hold real-time data
timestamps = []
temperatures = []

# Function to fetch and store weather data
def fetch_weather_data():
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            # Extract data
            temperature = data['main']['temp']
            timestamp = datetime.now().strftime('%H:%M:%S')  # Get the current time
            # Append new data to the lists
            temperatures.append(temperature)
            timestamps.append(timestamp)
            print(f"New data fetched: {timestamp} - {temperature}°C")
        else:
            print("Failed to fetch data:", response.status_code)
    except Exception as e:
        print(f"Error fetching weather data: {e}")

# Plotting the real-time data
def update_plot(frame):
    fetch_weather_data()  # Fetch the latest data
    ax.clear()  # Clear the previous plot
    ax.plot(timestamps, temperatures, label="Temperature (°C)", color="blue")  # Plot the new data
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title(f"Real-time Weather Data for {city}")
    ax.legend()
    plt.xticks(rotation=45, ha='right')

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Set up the animation to update every 10 seconds
ani = FuncAnimation(fig, update_plot, interval=10000)  # 10000 ms = 10 seconds

# Display the plot
plt.tight_layout()
plt.show()

# Automate the pipeline: run every 10 seconds to fetch new data
schedule.every(10).seconds.do(fetch_weather_data)

print("Starting automated pipeline...")
while True:
    schedule.run_pending()
    time.sleep(1)