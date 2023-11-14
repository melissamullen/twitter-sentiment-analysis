# Real-Time Sentiment Analysis of Twitter Data


- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)


## Project Overview
This project involves creating a Python application that performs real-time sentiment analysis on Twitter data. It analyzes tweets on various AI-related topics, assesses their sentiment, and visualizes the results in an interactive dashboard using Streamlit. The data is fetched in real-time using Tweepy and stored in a Snowflake database.

## Features
- 'Real-time' Twitter data fetching and analysis (updates every one minute).
- Sentiment analysis of tweets related to AI.
- Interactive dashboard built with Streamlit for data visualization.
- Data storage and retrieval using Snowflake.
- Automated tweet fetching using a scheduled cron job.

## Technologies Used
- Python
- NLTK (for lemmatization)
- TextBlob (for sentiment model)
- SQL
- Snowflake
- AWS (EC2 instance)
- Streamlit (for the [dashboard](https://melissa-mullen-twitter-sentiment-analysis.streamlit.app/))
- Twitter API

## Prerequisites
- Python 3.9
- Twitter Developer Account and API credentials
- Snowflake account
- Streamlit
- Additional Python libraries: `tweepy`, `textblob`, `pandas`, `numpy`, `matplotlib`

## Installation
1. Clone the repository:

`git clone https://github.com/melissamullen/twitter-sentiment-analysis.git`

2. Navigate to the project directory:

`cd twitter-sentiment-analysis`

3. Install required Python packages:

`pip install -r requirements.txt`


## Configuration
1. Set up your Twitter API credentials and Snowflake connection details in an `.env` file or use environment variables.

## Running the Dashboard
To run the Streamlit dashboard locally, execute the following command:

`streamlit run apps/sentiment_dashboard.py`

## Deployment
- The dashboard is deployed on Streamlit Sharing.
- The tweet fetching script is set up as a cron job on an AWS EC2 instance.
