import matplotlib.pyplot as plt
import snowflake.connector
from dotenv import load_dotenv
import os
from pathlib import Path

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

# Function to fetch sentiment data from Snowflake
def fetch_sentiment_data():
    conn = get_snowflake_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT sentiment_polarity FROM tweets")
    data = cursor.fetchall()
    conn.close()
    return data

# Function to plot histogram of sentiment polarity
def plot_sentiment_histogram(data):
    polarities = [item[0] for item in data]  # Extract polarities
    plt.hist(polarities, bins=20, color='blue', edgecolor='black')
    plt.title('Histogram of Sentiment Polarity')
    plt.xlabel('Polarity')
    plt.ylabel('Frequency')
    plt.show()

# Main section to execute the functions
if __name__ == "__main__":
    sentiment_data = fetch_sentiment_data()
    plot_sentiment_histogram(sentiment_data)
