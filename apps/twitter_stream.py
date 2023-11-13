import os
import time
from dotenv import load_dotenv
from pathlib import Path
import tweepy
from textblob import TextBlob
import snowflake.connector
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
import time
import nltk
nltk.download('punkt')

try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')
nltk.download('wordnet')
nltk_resources = ['stopwords', 'wordnet']

for resource in nltk_resources:
    try:
        nltk.data.find(f'corpora/{resource}')
    except LookupError:
        nltk.download(resource)

# Construct the path to the .env file in the parent directory
env_path = os.path.join(os.getcwd(), "twitter-sentiment-analysis", ".env")

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

# Initialize the Tweepy Client
client = tweepy.Client(bearer_token=os.getenv('BEARER_TOKEN'))


def determine_category(tweet_text):
    tweet_text_lower = tweet_text.lower()

    # Define keywords for each category
    healthcare_keywords = ['healthcare', 'medical', 'health']
    finance_keywords = ['finance', 'fintech', 'financial']
    education_keywords = ['education', 'edtech', 'learning']

    # Check for keywords in tweet text
    if any(keyword in tweet_text_lower for keyword in healthcare_keywords):
        return 'Healthcare'
    elif any(keyword in tweet_text_lower for keyword in finance_keywords):
        return 'Finance'
    elif any(keyword in tweet_text_lower for keyword in education_keywords):
        return 'Education'

    return 'General'



def get_snowflake_conn():
    return snowflake.connector.connect(
        user='melissamullen',
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account='lhb14091.us-east-1',  # Adjusted account name
        warehouse='melissa_warehouse_xs',
        database='melissa_db',
        schema='melissa_schema'
    )

def init_db():
    conn = get_snowflake_conn()
    cursor = conn.cursor()
    # Adjusted table creation query
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER AUTOINCREMENT PRIMARY KEY,
            tweet TEXT,
            sentiment_polarity FLOAT,
            sentiment_subjectivity FLOAT,
            created_at TIMESTAMP,
            category VARCHAR
        )
    ''')
    conn.commit()
    conn.close()


def save_to_db(tweet, sentiment, created_at, category):
    try:
        conn = get_snowflake_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tweets (tweet, sentiment_polarity, sentiment_subjectivity, created_at, category) 
            VALUES (%s, %s, %s, %s, %s)
        ''', (tweet, sentiment.polarity, sentiment.subjectivity, created_at, category))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while saving to database: {e}")
    finally:
        conn.close()


def preprocess_tweet_text(tweet_text):
    # Remove URLs
    tweet_text = re.sub(r'http\S+|www\S+|https\S+', '', tweet_text, flags=re.MULTILINE)
    
    # Remove user @ references and '#' from tweet
    tweet_text = re.sub(r'\@\w+|\#','', tweet_text)

    # Tokenization
    tweet_tokens = word_tokenize(tweet_text)

    # Filter stopwords
    filtered_words = [word for word in tweet_tokens if word not in stopwords.words('english')]
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]

    return " ".join(lemmatized_words)


def fetch_and_analyze_tweets(query, max_results=100):
    try:
        tweets = client.search_recent_tweets(query=query, max_results=max_results, tweet_fields=["created_at"])
        for tweet in tweets.data:
            if tweet.text.startswith("RT"):
                continue

            cleaned_text = preprocess_tweet_text(tweet.text)
            analysis = TextBlob(cleaned_text)
            sentiment = analysis.sentiment
            created_at = tweet.created_at
            category = determine_category(cleaned_text)  # Determine the category

            print(f"Tweet: {cleaned_text}\nSentiment: {sentiment}\nCreated at: {created_at}\nCategory: {category}")
            save_to_db(cleaned_text, sentiment, created_at, category)
    except Exception as e:
        print(f"An error occurred: {e}")


# Intialize the database
init_db()

# # Define the batch interval (in seconds)
# batch_interval = 900  # Adjust as needed

# while True:
#     try:
#         # Fetch and process tweets
#         query = "#AI OR #ArtificialIntelligence -is:retweet"
#         fetch_and_analyze_tweets(query, max_results=100)

#         # Wait for the next batch
#         time.sleep(batch_interval)

#     except tweepy.TweepyException as e:
#         if e.api_code == 429:  # Rate limit exceeded
#             print("Rate limit exceeded. Waiting to retry...")
#             time.sleep(15 * 60)  # Wait 15 minutes before retrying
#         else:
#             print(f"An error occurred: {e}")
#             time.sleep(batch_interval)


def main():
    try:
        # Fetch and process tweets
        query = "#AI OR #ArtificialIntelligence -is:retweet"
        fetch_and_analyze_tweets(query, max_results=100)

    except tweepy.TweepyException as e:
        if e.api_code == 429:
            print("Rate limit exceeded. Exiting.")
        else:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()