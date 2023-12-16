import streamlit as st
import pandas as pd
import os, sys
from sqlalchemy import create_engine
from urllib.parse import quote
import matplotlib.pyplot as plt
import seaborn as sns

rpath = os.path.abspath('..')
if rpath not in sys.path:
    sys.path.insert(0, rpath)

username = 'postgres'
password = 'nati@postgres'
hostname = 'localhost'
port = '5432'
database_name = 'TellCo'

# Escape the special characters in the password
escaped_password = quote(password, safe='')

# Create the database engine
engine = create_engine(f'postgresql://{username}:{escaped_password}@{hostname}:{port}/{database_name}')

def show():
    st.header("User Experiance Analysis Page")

    # Add a selectbox to choose between options
    main_option = st.selectbox(
        'Select an analysis:',
        ['Top 10 Users by Experiance Score', 'Experiance Score Changes for the Last 20,000 xDR Sessions']
    )

    if main_option == 'Top 10 Users by Experiance Score':
        top_10_users_by_experiance_score()

    elif main_option == 'Experiance Score Changes for the Last 20,000 xDR Sessions':
        show_time_series_experience_scores()



def top_10_users_by_experiance_score():
    """
    This function displays the top 10 users based on their engagement scores.
    """
    # Query to join data from both tables
    query = """
    SELECT *
    FROM satisfaction_result_df;
    """

    # Execute the query and fetch the top 10 users
    data = pd.read_sql(query, engine)

    # Sort data by engagement score in descending order
    data_sorted = data.sort_values(by='Experience Score', ascending=False)

    # Pick the top 10 users
    top_10_users = data_sorted.head(10)
    # Display the results
    st.subheader("Top 10 Users by Experiance Score")
    st.table(top_10_users[['MSISDN/Number', 'Experience Score']])

def show_time_series_experience_scores():
    # Display time series analysis of experience scores
    # Add your code here

    # Query the data from satisfaction_result_df and xdr_data
    query = """
        SELECT srdf."MSISDN/Number", srdf."Experience Score", xd."Start"
        FROM satisfaction_result_df srdf
        LEFT JOIN xdr_data xd ON srdf."MSISDN/Number" = xd."MSISDN/Number"
    """
    df_combined = pd.read_sql(query, engine)

    # Filter rows with non-null 'Experience Score' and 'Start'
    df_filtered = df_combined.dropna(subset=['Experience Score', 'Start'])

    # Sort the DataFrame by 'Start' column
    df_sorted = df_filtered.sort_values(by='Start', ascending=True)

    # Select the most recent 20,000 XDR sessions
    df_recent = df_sorted.tail(20000)

    # Convert the 'Start' column to datetime format
    df_recent['Start'] = pd.to_datetime(df_recent['Start'])

    # Sort the DataFrame by the 'Start' column
    df_recent_sorted = df_recent.sort_values(by='Start')

    # Calculate the moving average for 'Experience Score'
    window_size = 1000  # You can adjust the window size as needed
    df_recent_sorted['Experience Score MA'] = df_recent_sorted['Experience Score'].rolling(window=window_size).mean()

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot time series line plot and moving average for the most recent data
    sns.lineplot(data=df_recent_sorted, x=df_recent_sorted.index, y='Experience Score', ax=ax, label='Experience Score')
    sns.lineplot(data=df_recent_sorted, x=df_recent_sorted.index, y='Experience Score MA', ax=ax, label='Experience Score MA', color='red')

    # Set the plot details
    ax.set_title('Time Series Analysis of Experience Scores (Most Recent 20,000 Sessions) with Moving Average')
    ax.set_xlabel('Start')
    ax.set_ylabel('Experience Score')
    ax.tick_params(rotation=45)
    ax.legend()

    # Display the plot in Streamlit
    st.pyplot(fig)

