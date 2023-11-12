# command to run: streamlit run apps/sentiment_dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import os
from wordcloud import WordCloud
import pytz
from datetime import datetime
import matplotlib.dates as mdates
from datetime import timedelta
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

# Construct the path to the .env file in the parent directory
path = Path("/Users/melissamullen/twitter-sentiment-analysis")
env_path = os.path.join(path, ".env")

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)


# Function to create a connection engine to Snowflake
def get_snowflake_engine():
    return create_engine(URL(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    ))


def fetch_date_range():
    engine = get_snowflake_engine()
    query = "SELECT MIN(created_at) as min_date, MAX(created_at) as max_date FROM tweets"
    df = pd.read_sql(query, engine)
    engine.dispose()

    # Convert dates to EST
    eastern = pytz.timezone('US/Eastern')
    min_date_est = pd.to_datetime(df.iloc[0]['min_date'], utc=True).astimezone(eastern)
    max_date_est = pd.to_datetime(df.iloc[0]['max_date'], utc=True).astimezone(eastern)

    return min_date_est, max_date_est


def fetch_data(date_range=None, category='All'):
    engine = get_snowflake_engine()
    query = "SELECT * FROM tweets WHERE 1=1"

    if date_range and len(date_range) == 2:
        # Convert to datetime and adjust for inclusivity of the end date
        start_date = pd.to_datetime(date_range[0], utc=True)
        end_date = pd.to_datetime(date_range[1], utc=True) + timedelta(days=1)  # Include the entire end date

        query += f" AND created_at >= '{start_date}' AND created_at < '{end_date}'"

    if category and category != 'All':
        query += f" AND category = '{category}'"

    df = pd.read_sql(query, engine)
    engine.dispose()

    # Convert 'created_at' to EST
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    df['created_at_est'] = df['created_at'].dt.tz_convert('US/Eastern')
    df = df.drop(columns=["created_at"])
    print(df)

    return df


def custom_date_formatter(x, pos=None):
    if pos == 0:  # First label is always full date and time
        return data['created_at_est_str'][x]
    else:
        # Check if this label's date is different from the previous label's date
        current_label = data['created_at_est_str'][x]
        previous_label = data['created_at_est_str'][x-1]
        
        current_date = current_label.split()[0]
        previous_date = previous_label.split()[0]

        if current_date != previous_date:
            return current_label  # Show full date and time for new dates
        else:
            return current_label.split()[1]  # Show only time otherwise


####### Streamlit App Layout ######
st.title('AI Twitter Sentiment Analysis Dashboard')
st.markdown('This dashboard displays sentiment analysis of AI-related tweets.')

# Fetch the range of dates with data in EST
min_date_est, max_date_est = fetch_date_range()

# Ensure the max date for the date picker does not exceed today's date in EST
today_est = datetime.now().astimezone(pytz.timezone('US/Eastern'))
max_date_est = min(max_date_est, today_est)

# Sidebar for Filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    [],
    min_value=min_date_est.date(),  # Use only the date part
    max_value=max_date_est.date()   # Use only the date part
)
selected_category = st.sidebar.selectbox("Select Category", options=['All', 'Healthcare', 'Finance', 'Education'])

# Fetch data based on filters
data = fetch_data(date_range=date_range, category=selected_category)

# TODO: Figure out why the utc data gets plotted if the est time is in datetime format
# Convert 'created_at_est' to string for plotting
data['created_at_est_str'] = data['created_at_est'].dt.strftime('%m-%d-%Y    %H:%M')

### Sentiment Over Time Plot ###
st.header('Sentiment Over Time')
fig, ax = plt.subplots()

# Ensure data is sorted by 'created_at_est'
data.sort_values('created_at_est', inplace=True)

ax.plot(data['created_at_est_str'], data['sentiment_polarity'], marker='o', linestyle='-', color="purple")

# Customize x-axis tick labels
tick_spacing = 5  # Adjust this based on your data's density
ax.xaxis.set_major_locator(plt.MaxNLocator(tick_spacing))

ax.set_xlabel('Time (EST)')
ax.set_ylabel('Sentiment Polarity')
ax.set_title('Sentiment Polarity Over Time (EST)')

# Adjust x-axis labels for readability
ax.tick_params(axis='x', rotation=20)

st.pyplot(fig)


### Sentiment Distribution Plot ###
st.header('Sentiment Distribution')
fig, ax = plt.subplots()

# Plotting a histogram
ax.hist(data['sentiment_polarity'], bins=20, color='purple', edgecolor='black')

ax.set_xlabel('Sentiment Polarity', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.set_title('Distribution of Sentiment Polarity', fontsize=14)

st.pyplot(fig)

print(data.columns)
### Word Cloud ###
# Assuming 'tweet' is the column containing the text
st.header('Word Cloud')
if 'tweet' in data.columns and not data.empty:
    words = ' '.join(data['tweet'])
    wordcloud = WordCloud(width=800, height=400).generate(words)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
else:
    st.write("No data available for the selected date range or category.")

