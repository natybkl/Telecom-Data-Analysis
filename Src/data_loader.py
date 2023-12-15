import pandas as pd
import numpy as np
import matplotlib
from sqlalchemy import create_engine
from urllib.parse import quote

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans


username = 'postgres'
password = 'nati@postgres'
hostname = 'localhost'
port = '5432'
database_name = 'TellCo'

# Escape the special characters in the password
escaped_password = quote(password, safe='')

# Create the database engine
engine = create_engine(f'postgresql://{username}:{escaped_password}@{hostname}:{port}/{database_name}')

# Establish a connection
with engine.connect() as connection:
    # Query the data and load it into a pandas DataFrame
    query = """
        SELECT *
        FROM xdr_data
    """
    df = pd.read_sql(query, connection)

df.head()