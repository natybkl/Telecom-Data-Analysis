import streamlit as st
from Dashboard import general_analysis, overview_analysis, engagement_analysis, experience_analysis, satisfaction_analysis

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

# Sidebar
selected_page = st.sidebar.selectbox("Select Analysis", menu_options, index=0)

# Page content based on the selected option
if selected_page == "General Analysis":
    general_analysis.show()

elif selected_page == "User Overview Analysis":
    overview_analysis.show()

elif selected_page == "User Engagement Analysis":
    engagement_analysis.show()

elif selected_page == "User Experience Analysis":
    experience_analysis.show()

elif selected_page == "User Satisfaction Analysis":
    satisfaction_analysis.show()
