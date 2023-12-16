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
    st.header("User Engagement Analysis Page")

    # Add options for user engagement analysis
    engagement_option = st.selectbox(
        'Select an analysis:',
        [
         'Top 3 Most Used Applications',
         'Top 10 Users by Engagment Score',
         'Engagement Score Changes for the Last 20,000 xDR Sessions']
    )


    if engagement_option == 'Top 3 Most Used Applications':
        show_top_3_applications()

    elif engagement_option == 'Top 10 Users by Engagment Score':
        show_top_10_users_by_engagement_score()

    elif engagement_option == 'Engagement Score Changes for the Last 20,000 xDR Sessions':
        show_engagement_score_changes()


# Function to show top 3 most used applications
def show_top_3_applications():
    # Fetch data from the xdr_data table
    query_xdr = """
        SELECT *
        FROM xdr_data
    """
    df = pd.read_sql(query_xdr, engine)

    # List of application columns
    application_columns = ['Social Media', 'Google', 'Email', 'Youtube', 'Netflix', 'Gaming', 'Other']

    # Calculate total upload and download data volumes for each application
    total_data = {}
    for app in application_columns:
        total_data[app] = df[app + ' DL (Bytes)'].sum() + df[app + ' UL (Bytes)'].sum()

    # Create a new DataFrame with the total data volumes
    total_data_df = pd.DataFrame.from_dict(total_data, orient='index', columns=['Total Data Volume'])
    total_data_df.index.name = 'Applications'

    # Select the top 3 most used applications based on total data volume
    top_3_apps = total_data_df.nlargest(3, 'Total Data Volume')

    # Plot the bar chart
    fig, ax = plt.subplots()
    sns.barplot(x=top_3_apps.index, y='Total Data Volume', data=top_3_apps, ax=ax)
    ax.set_title('Total Upload + Download Data Volume vs. Application')
    ax.set_xlabel('Applications')
    ax.set_ylabel('Total Data Volume')
    st.pyplot(fig)

def show_top_10_users_by_engagement_score():
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
    data_sorted = data.sort_values(by='Engagement Score', ascending=False)

    # Pick the top 10 users
    top_10_users = data_sorted.head(10)
    # Display the results
    st.subheader("Top 10 Users by Engagement Score")
    st.table(top_10_users[['MSISDN/Number', 'Engagement Score']])


# Function to show engagement score changes for the last 20,000 xDR sessions
def show_engagement_score_changes():
    # Display time series analysis of engagement scores
    # Add your code here

    # Query the data from satisfaction_result_df and xdr_data
    query = """
        SELECT srdf."MSISDN/Number", srdf."Engagement Score", xd."Start"
        FROM satisfaction_result_df srdf
        LEFT JOIN xdr_data xd ON srdf."MSISDN/Number" = xd."MSISDN/Number"
    """
    df_combined = pd.read_sql(query, engine)

    # Filter rows with non-null 'Engagement Score' and 'Start'
    df_filtered = df_combined.dropna(subset=['Engagement Score', 'Start'])

    # Sort the DataFrame by 'Start' column
    df_sorted = df_filtered.sort_values(by='Start', ascending=True)

    # Select the most recent 20,000 XDR sessions
    df_recent = df_sorted.tail(20000)

    # Convert the 'Start' column to datetime format
    df_recent['Start'] = pd.to_datetime(df_recent['Start'])

    # Sort the DataFrame by the 'Start' column
    df_recent_sorted = df_recent.sort_values(by='Start')

    # Calculate the moving average for 'Engagement Score'
    window_size = 1000  # You can adjust the window size as needed
    df_recent_sorted['Engagement Score MA'] = df_recent_sorted['Engagement Score'].rolling(window=window_size).mean()

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot time series line plot and moving average for the most recent data
    sns.lineplot(data=df_recent_sorted, x=df_recent_sorted.index, y='Engagement Score', ax=ax, label='Engagement Score')
    sns.lineplot(data=df_recent_sorted, x=df_recent_sorted.index, y='Engagement Score MA', ax=ax, label='Engagement Score MA', color='red')

    # Set the plot details
    ax.set_title('Time Series Analysis of Engagement Scores (Most Recent 20,000 Sessions) with Moving Average')
    ax.set_xlabel('Start')
    ax.set_ylabel('Engagement Score')
    ax.tick_params(rotation=45)
    ax.legend()

    # Display the plot in Streamlit
    st.pyplot(fig)
