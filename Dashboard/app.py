import streamlit as st
import os, sys, pandas

rpath = os.path.abspath('..')
if rpath not in sys.path:
    sys.path.insert(0, rpath)

from Dashboard import general_analysis
from Dashboard import overview_analysis
from Dashboard import engagment_analysis
from Dashboard import experience_analysis
from Dashboard import satisfaction_analysis

# Set page title
st.set_page_config(page_title="TellCo Data Analysis")

# Title
st.title("TellCo Data Analysis")

# Sidebar menu options
menu_options = [
    "General Analysis",
    "User Overview Analysis",
    "User Engagement Analysis",
    "User Experience Analysis",
    "User Satisfaction Analysis",
]

# Sidebar navigation bar
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)

# Page content based on the selected option
selected_page = st.sidebar.radio("", menu_options, index=0)

if selected_page == "General Analysis":
    general_analysis.show()

elif selected_page == "User Overview Analysis":
    overview_analysis.show()

elif selected_page == "User Engagement Analysis":
    engagment_analysis.show()

elif selected_page == "User Experience Analysis":
    experience_analysis.show()

elif selected_page == "User Satisfaction Analysis":
    satisfaction_analysis.show()