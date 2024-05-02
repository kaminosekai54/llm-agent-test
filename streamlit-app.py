import os
import shutil
import streamlit as st
import pandas as pd
from datetime import datetime
from crews import SotaReviewCrew
import warnings

warnings.filterwarnings('ignore')

@ st.cache_data # Cache the processed dataframe
def preprocess_data(filepath):
    """
    Preprocesses the dataframe by converting date columns and ensuring correct types for other columns.
    """
    df = pd.read_csv(filepath, encoding="utf8").applymap(lambda x: x.decode('utf-8', 'replace') if isinstance(x, bytes) else x)
    df['Publication Date'] = pd.to_datetime(df['Publication Date'].replace("Not Available", pd.NaT), errors='coerce')
    df['Authors'] = df['Authors'].astype(str)
    return df

# Function to display the sidebar filters based on selected columns
def display_filters(df, selected_columns):
    st.sidebar.title('Filter Data')
    filtered_df = df.copy()

    # Filter by authors
    if 'Authors' in selected_columns:
        try:
            all_authors = df['Authors'].dropna().apply(lambda x: [author.strip() for author in x.split(',')])
            unique_authors = sorted(set([author for sublist in all_authors for author in sublist]))

            # unique_authors = set(author.strip().lower() for authors in df['Authors'].str.split(',') for author in authors if author.strip())
        except Exception as e:
            st.sidebar.error(f"Error processing authors: {e}")
            unique_authors = []
        selected_authors = st.sidebar.multiselect('Filter by Authors', sorted(list(unique_authors)))

        if selected_authors: 
            filtered_df = filtered_df[filtered_df['Authors'].apply(lambda x: any(author.strip() in selected_authors for author in x.split(',')))]

    return filtered_df

# Function to display the selected columns in the main content area
def display_selected_columns(df, selected_columns):
    st.header("Articles found :")
    st.write(df[selected_columns])

# Streamlit app starts here
def main():
    st.set_page_config(layout="wide", page_title="SOTA Review Crew", page_icon=":rocket:")
    st.title("State-of-the-Art Review Crew")
    st.sidebar.header("Configuration")
    
    # User input for the topic
    topic = st.sidebar.text_input("Enter the review topic:")
    start_date = (datetime.now() - pd.DateOffset(years=5))
    end_date = datetime.now()
    selected_min_date_for_search = st.sidebar.date_input("Select Minimum Publication Date", max_value=end_date, value=start_date , format="DD/MM/YYYY")
    selected_max_date_for_search  = st.sidebar.date_input("Select Maximum Publication Date", min_value=selected_min_date_for_search, max_value=end_date, value=end_date, format="DD/MM/YYYY")
    
    if st.sidebar.button("Run Review"):
        with st.spinner("🤖 **Agents at work...**"):
            if os.path.isfile("./pubMedResults.csv"): os.remove("./pubMedResults.csv")
            sota_review_crew = SotaReviewCrew(topic, start_date=selected_min_date_for_search.strftime("%d/%m/%Y"), end_date=selected_max_date_for_search.strftime("%d/%m/%Y"))
            results = sota_review_crew.run()
        st.success("Review Completed!")

    if os.path.isfile("pubMedResults.csv"):
        # result = pd.read_csv("pubMedResults.csv", encoding="utf8").applymap(lambda x: x.decode('utf-8', 'replace') if isinstance(x, bytes) else x)
        
        # Preprocess 'Publication Date' column
        # result['Publication Date'] = result['Publication Date'].replace("Not Available", pd.NaT)
        
        df = preprocess_data("pubMedResults.csv")


        # Multiselect to choose columns to display
        selected_columns = st.sidebar.multiselect("Select Columns to Display", df.columns, default=df.columns.tolist())

        # Display selected columns
        if selected_columns:
            filtered_df = display_filters(df, selected_columns)
            display_selected_columns(filtered_df, selected_columns)

            # Export filtered data
            if st.button('Export Filtered Data'):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label='Download CSV',
                    data=csv,
                    file_name='filtered_data.csv',
                    mime='text/csv'
                )

if __name__ == "__main__":
    if os.path.isdir("__pycache__"): 
        shutil.rmtree("__pycache__")
    main()
