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
    st.header("TellCo Data Analysis")

    # Add a selectbox to choose between options
    main_option = st.selectbox(
        'Select an analysis:',
        ['Distribution of user analysis scores', 'Distribution of user analysis scores with Handset groups', 'Time series analysis of user analysis scores']
    )

    if main_option == 'Distribution of user analysis scores':
        show_distribution_of_scores()

    elif main_option == 'Distribution of user analysis scores with Handset groups':
        show_distribution_with_handset_groups()

    elif main_option == 'Time series analysis of user analysis scores':
        show_time_series_analysis()
    

def show_distribution_of_scores():
    st.subheader("Distribution of User Analysis Scores")

    # Fetch data from the satisfaction_result_df table
    query = """
        SELECT "Experience Score", "Engagement Score", "Satisfaction Score"
        FROM satisfaction_result_df
    """
    df_scores = pd.read_sql(query, engine)

    # Calculate average scores for top 25%, 50%, 75%, and all users
    top_25_exp = df_scores["Experience Score"].quantile(0.75)
    top_50_exp = df_scores["Experience Score"].quantile(0.5)
    top_75_exp = df_scores["Experience Score"].quantile(0.25)
    all_users_exp = df_scores["Experience Score"].mean()

    top_25_eng = df_scores["Engagement Score"].quantile(0.75)
    top_50_eng = df_scores["Engagement Score"].quantile(0.5)
    top_75_eng = df_scores["Engagement Score"].quantile(0.25)
    all_users_eng = df_scores["Engagement Score"].mean()

    top_25_sat = df_scores["Satisfaction Score"].quantile(0.75)
    top_50_sat = df_scores["Satisfaction Score"].quantile(0.5)
    top_75_sat = df_scores["Satisfaction Score"].quantile(0.25)
    all_users_sat = df_scores["Satisfaction Score"].mean()

    # Create a DataFrame to display the results
    result_df = pd.DataFrame({
        'Experience Score': [top_25_exp, top_50_exp, top_75_exp, all_users_exp],
        'Engagement Score': [top_25_eng, top_50_eng, top_75_eng, all_users_eng],
        'Satisfaction Score': [top_25_sat, top_50_sat, top_75_sat, all_users_sat],
    }, index=['Top 25%', 'Top 50%', 'Top 75%', 'All Users'])

    # Define a custom color scale based on min and max values in the table
    color_scale = sns.light_palette("seagreen", as_cmap=True)

    # Display the results as a table with colored cells
    st.table(result_df.style.background_gradient(cmap=color_scale, axis=None))


    
def show_distribution_with_handset_groups():
    # Display the distribution of user analysis scores with Handset groups
    # Add your code here
    
    # Query the data from satisfaction_result_df and xdr_data
    query = """
        SELECT srdf."MSISDN/Number", srdf."Experience Score", srdf."Engagement Score", srdf."Satisfaction Score", xd."Handset Manufacturer"
        FROM satisfaction_result_df srdf
        LEFT JOIN xdr_data xd ON srdf."MSISDN/Number" = xd."MSISDN/Number"
    """
    df_combined = pd.read_sql(query, engine)

    # Filter rows with valid 'Handset Manufacturer' values
    valid_handset_values = ['Apple', 'Samsung', 'Huawei']
    df_filtered = df_combined[df_combined['Handset Manufacturer'].isin(valid_handset_values)]

    # Calculate average scores for each metric
    avg_scores = df_filtered.groupby('Handset Manufacturer').agg({
        'Experience Score': 'mean',
        'Engagement Score': 'mean',
        'Satisfaction Score': 'mean'
    }).transpose()

    # Define a custom color scale based on min and max values in the table
    color_scale = sns.light_palette("seagreen", as_cmap=True)

    # Display the result in a table with colored cells
    st.subheader("Distribution of User Analysis Scores with Handset Groups")
    st.table(avg_scores.style.background_gradient(cmap=color_scale, axis=None))



def show_time_series_analysis():
    # Add a sub-selectbox for Time series analysis options
    sub_option = st.selectbox(
        'Select a sub-analysis:',
        ['Time series analysis of experiance scores', 'Time series analysis of engagment scores', 'Time series analysis of satisfaction scores']
    )

    if sub_option == 'Time series analysis of experiance scores':
        show_time_series_experience_scores()

    elif sub_option == 'Time series analysis of engagment scores':
        show_time_series_engagement_scores()

    elif sub_option == 'Time series analysis of satisfaction scores':
        show_time_series_satisfaction_scores()

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
    
def show_time_series_engagement_scores():
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

def show_time_series_satisfaction_scores():
    # Display time series analysis of satisfaction scores
    # Add your code here

    # Query the data from satisfaction_result_df and xdr_data
    query = """
        SELECT srdf."MSISDN/Number", srdf."Satisfaction Score", xd."Start"
        FROM satisfaction_result_df srdf
        LEFT JOIN xdr_data xd ON srdf."MSISDN/Number" = xd."MSISDN/Number"
    """
    df_combined = pd.read_sql(query, engine)

    # Filter rows with non-null 'Satisfaction Score' and 'Start'
    df_filtered = df_combined.dropna(subset=['Satisfaction Score', 'Start'])

    # Sort the DataFrame by 'Start' column
    df_sorted = df_filtered.sort_values(by='Start', ascending=True)

    # Select the most recent 20,000 XDR sessions
    df_recent = df_sorted.tail(20000)

    # Convert the 'Start' column to datetime format
    df_recent['Start'] = pd.to_datetime(df_recent['Start'])

    # Sort the DataFrame by the 'Start' column
    df_recent_sorted = df_recent.sort_values(by='Start')

    # Calculate the moving average for 'Satisfaction Score'
    window_size = 1000  # You can adjust the window size as needed
    df_recent_sorted['Satisfaction Score MA'] = df_recent_sorted['Satisfaction Score'].rolling(window=window_size).mean()

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot time series line plot and moving average for the most recent data
    sns.lineplot(data=df_recent_sorted, x=df_recent_sorted.index, y='Satisfaction Score', ax=ax, label='Satisfaction Score')
    sns.lineplot(data=df_recent_sorted, x=df_recent_sorted.index, y='Satisfaction Score MA', ax=ax, label='Satisfaction Score MA', color='red')

    # Set the plot details
    ax.set_title('Time Series Analysis of Satisfaction Scores (Most Recent 20,000 Sessions) with Moving Average')
    ax.set_xlabel('Start')
    ax.set_ylabel('Satisfaction Score')
    ax.tick_params(rotation=45)
    ax.legend()

    # Display the plot in Streamlit
    st.pyplot(fig)

if __name__ == '__main__':
    show()
