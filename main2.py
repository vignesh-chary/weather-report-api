import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import gradio as gr

# Function to get historical cryptocurrency data for the past 2 months
def get_historical_data(crypto_id='bitcoin', currency='usd', days=60):
    # Calculate the date 2 months ago
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    
    # Convert dates to Unix timestamps
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart/range'
    params = {
        'vs_currency': currency,
        'from': start_timestamp,
        'to': end_timestamp
    }

    try:
        # Send GET request to CoinGecko API
        response = requests.get(url, params=params)
        data = response.json()
        
        # Check if the request was successful
        if response.status_code == 200 and 'prices' in data:
            return data['prices']  # Return the list of price data
        else:
            print(f"Error: Unable to fetch historical data for {crypto_id}.")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Function to plot the historical price data
def plot_historical_data(prices, crypto_id='bitcoin', currency='usd'):
    # Extract timestamps and prices
    timestamps = [entry[0] for entry in prices]
    price_values = [entry[1] for entry in prices]

    # Convert timestamps to datetime objects for plotting
    times = [datetime.utcfromtimestamp(ts / 1000) for ts in timestamps]
    
    # Set up the plot
    plt.figure(figsize=(10, 6))
    plt.plot(times, price_values, color='blue', label=f'{crypto_id.capitalize()} Price')
    plt.xlabel('Date')
    plt.ylabel(f'{crypto_id.capitalize()} Price ({currency.upper()})')
    plt.title(f'{crypto_id.capitalize()} Price Over the Last 2 Months')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot to a file and return the file path
    file_path = "/mnt/data/crypto_price_plot.png"
    plt.savefig(file_path)
    plt.close()
    return file_path

# Gradio interface function
def crypto_price_plot(crypto_id, currency, days):
    prices = get_historical_data(crypto_id, currency, days)
    if prices:
        # Plot the data and return the image file path
        return plot_historical_data(prices, crypto_id, currency)
    else:
        return "Error fetching data"

# Gradio UI setup
def create_gradio_interface():
    # Create a dropdown for cryptocurrency selection
    crypto_choices = ['bitcoin', 'ethereum', 'litecoin', 'dogecoin']

    # Create a Gradio interface
    interface = gr.Interface(
        fn=crypto_price_plot,  # Function to call
        inputs=[
            gr.Dropdown(choices=crypto_choices, label="Cryptocurrency", value="bitcoin"),  # Use 'value' instead of 'default'
            gr.Dropdown(choices=["usd", "eur", "gbp"], label="Currency", value="usd"),  # Use 'value' instead of 'default'
            gr.Slider(minimum=30, maximum=180, step=1, value=60, label="Days", interactive=True)
        ],
        outputs=gr.Image(label="Cryptocurrency Price Chart"),  # Output the image of the plot
        live=True,  # Update the plot live when parameters change
        title="Cryptocurrency Price Tracker",
        description="Select a cryptocurrency, a currency, and the number of days to view its historical price data over the past selected period."
    )
    
    return interface

# Launch the Gradio interface
if __name__ == "__main__":
    interface = create_gradio_interface()
    interface.launch()
