import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os
import snowflake.connector

# Construct the path to the .env file in the parent directory
path = Path("/Users/melissamullen/twitter-sentiment-analysis")
env_path = os.path.join(path, ".env")

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

# Function to establish a connection to Snowflake
def get_snowflake_conn():
    return snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    )

def fetch_sentiment_time_series():
    conn = get_snowflake_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT sentiment_polarity, created_at FROM tweets")
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=['polarity', 'timestamp'])

    # Convert to datetime and handle NaT values
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])  # Drop rows where timestamp is NaT

    return df

def plot_time_series(data):
    data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
    data = data.dropna(subset=['timestamp'])  # Drop rows where timestamp is NaT

    # Ensure the timestamp is the index
    data.set_index('timestamp', inplace=True)

    # Option to filter data to a specific time frame
    filtered_data = data.between_time('22:28', '22:30')

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_data.index, filtered_data['polarity'], marker='o')  # Plot with markers

    plt.title('Sentiment Polarity Trend (5-minute intervals)')
    plt.xlabel('Time')
    plt.ylabel('Average Sentiment Polarity')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout for clarity
    plt.show()


if __name__ == "__main__":
    sentiment_data = fetch_sentiment_time_series()
    plot_time_series(sentiment_data)
