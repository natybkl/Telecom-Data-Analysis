import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from urllib.parse import quote

# Your database connection details
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
    st.header("User Overview Analysis Page")

    # Add a selectbox to choose between analysis options
    analysis_option = st.selectbox(
        'Select an analysis:',
        ['Top 5 Handset Manufacturers', 'Distribution of Total DL', 'Distribution of Total UL', 'Total UL + DL vs. Application', 'Correlation Analysis']
    )

    # Call the respective function based on the user's choice
    if analysis_option == 'Top 5 Handset Manufacturers':
        show_top_manufacturers()
    elif analysis_option == 'Distribution of Total DL':
        show_distribution_total_dl()
    elif analysis_option == 'Distribution of Total UL':
        show_distribution_total_ul()
    elif analysis_option == 'Total UL + DL vs. Application':
        show_total_vs_application()
    elif analysis_option == 'Correlation Analysis':
        show_correlation_analysis()

def show_top_manufacturers():
    st.subheader("Top 5 Handset Manufacturers")
    query_top_manufacturers = """
        SELECT "Handset Manufacturer", COUNT(*) AS "Count"
        FROM xdr_data
        GROUP BY "Handset Manufacturer"
        ORDER BY "Count" DESC
        LIMIT 5
    """
    df_top_manufacturers = pd.read_sql(query_top_manufacturers, engine)
    st.table(df_top_manufacturers)

def show_distribution_total_dl():
    st.subheader("Distribution of Total DL (Bar Plot)")
    query_total_dl = """
        SELECT "MSISDN/Number", "Total DL (Bytes)"
        FROM xdr_data
    """
    df_total_dl = pd.read_sql(query_total_dl, engine)
    fig, ax = plt.subplots()
    sns.histplot(data=df_total_dl, x='Total DL (Bytes)', bins=30, kde=True)
    ax.set_xlabel("Total DL (Bytes)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Total DL")
    st.pyplot(fig)

def show_distribution_total_ul():
    st.subheader("Distribution of Total UL (Bar Plot)")
    query_total_ul = """
        SELECT "MSISDN/Number", "Total UL (Bytes)"
        FROM xdr_data
    """
    df_total_ul = pd.read_sql(query_total_ul, engine)
    fig, ax = plt.subplots()
    sns.histplot(data=df_total_ul, x='Total UL (Bytes)', bins=30, kde=True)
    ax.set_xlabel("Total UL (Bytes)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Total UL")
    st.pyplot(fig)

def show_total_vs_application():
    st.subheader("Total UL + DL vs. Application")
    query_total_vs_application = """
        SELECT "MSISDN/Number", "Social Media DL (Bytes)", "Google DL (Bytes)", "Email DL (Bytes)", "Youtube DL (Bytes)",
               "Netflix DL (Bytes)", "Gaming DL (Bytes)", "Other DL (Bytes)",
               "Social Media UL (Bytes)", "Google UL (Bytes)", "Email UL (Bytes)", "Youtube UL (Bytes)",
               "Netflix UL (Bytes)", "Gaming UL (Bytes)", "Other UL (Bytes)"
        FROM xdr_data
    """
    df = pd.read_sql(query_total_vs_application, engine)

    # List of application columns
    application_columns = ['Social Media', 'Google', 'Email', 'Youtube', 'Netflix', 'Gaming', 'Other']

    # Calculate total upload and download data volumes for each application
    total_data = {}
    for app in application_columns:
        total_data[app] = df[app + ' DL (Bytes)'].sum() + df[app + ' UL (Bytes)'].sum()

    # Create a new DataFrame with the total data volumes
    total_data_df = pd.DataFrame.from_dict(total_data, orient='index', columns=['Total Data Volume'])
    total_data_df.index.name = 'Applications'

    fig, ax = plt.subplots()
    sns.barplot(x=total_data_df.index, y='Total Data Volume', data=total_data_df)
    ax.set_xlabel("Applications")
    ax.set_ylabel("Total Data Volume")
    ax.set_title("Total Upload + Download Data Volume vs. Application")
    ax.tick_params(rotation=45)
    st.pyplot(fig)

def show_correlation_analysis():
    st.subheader("Correlation Analysis")

    # Query data from xdr_data table
    query_correlation = """
        SELECT "Social Media DL (Bytes)", "Social Media UL (Bytes)",
               "Youtube DL (Bytes)", "Youtube UL (Bytes)",
               "Netflix DL (Bytes)", "Netflix UL (Bytes)",
               "Google DL (Bytes)", "Google UL (Bytes)",
               "Email DL (Bytes)", "Email UL (Bytes)",
               "Gaming DL (Bytes)", "Gaming UL (Bytes)",
               "Other DL (Bytes)", "Other UL (Bytes)"
        FROM xdr_data
    """
    df = pd.read_sql(query_correlation, engine)

    # Step 1: Create a new DataFrame for total data volume
    total_data_volume = pd.DataFrame()

    # Calculate the total data volume for each application (UL + DL)
    total_data_volume['Social Media Total'] = df['Social Media DL (Bytes)'] + df['Social Media UL (Bytes)']
    total_data_volume['Youtube Total'] = df['Youtube DL (Bytes)'] + df['Youtube UL (Bytes)']
    total_data_volume['Netflix Total'] = df['Netflix DL (Bytes)'] + df['Netflix UL (Bytes)']
    total_data_volume['Google Total'] = df['Google DL (Bytes)'] + df['Google UL (Bytes)']
    total_data_volume['Email Total'] = df['Email DL (Bytes)'] + df['Email UL (Bytes)']
    total_data_volume['Gaming Total'] = df['Gaming DL (Bytes)'] + df['Gaming UL (Bytes)']
    total_data_volume['Other Total'] = df['Other DL (Bytes)'] + df['Other UL (Bytes)']

    # Step 2: Generate the correlation matrix
    correlation_matrix = total_data_volume.corr()

    # Define a custom color scale based on min and max values in the table
    color_scale = sns.light_palette("seagreen", as_cmap=True)

    # Display the results as a table with colored cells
    st.table(correlation_matrix.style.background_gradient(cmap=color_scale, axis=None))