import os
import shutil
import streamlit as st
import pandas as pd
from datetime import datetime
from crews import SotaReviewCrew
import warnings

warnings.filterwarnings('ignore')

# Function to display the sidebar filters based on selected columns
def display_filters(df, selected_columns):
    st.sidebar.title('Filter Data')
    filtered_df = df.copy()

    # Filter by authors
    if 'Authors' in selected_columns:
        unique_authors = set(author.strip() for authors in df['Authors'].str.split(',') for author in authors)
        selected_authors = st.sidebar.multiselect('Filter by Authors', list(unique_authors))

    # Filter by publication date
    if 'Publication Date' in selected_columns:
        min_date = pd.to_datetime(df['Publication Date']).min().date()
        max_date = pd.to_datetime(df['Publication Date']).max().date()
        selected_min_date = st.sidebar.date_input("Select Minimum Publication Date", value=min_date, format="DD/MM/YYYY")
        selected_max_date = st.sidebar.date_input("Select Maximum Publication Date", value=max_date, format="DD/MM/YYYY")

        # Filter based on selected date range
        filtered_df = filtered_df[(pd.to_datetime(filtered_df['Publication Date']) >= pd.Timestamp(selected_min_date)) & 
                                  (pd.to_datetime(filtered_df['Publication Date']) <= pd.Timestamp(selected_max_date))]

    # Filter by title
    if 'Title' in selected_columns:
        title_keyword = st.sidebar.text_input("Search by Title Keyword")
        if title_keyword:
            filtered_df = filtered_df[filtered_df['Title'].str.contains(title_keyword, case=False, na=False)]

    # Filter by abstract
    if 'Abstract' in selected_columns:
        abstract_keyword = st.sidebar.text_input("Search by Abstract Keyword")
        if abstract_keyword:
            filtered_df = filtered_df[filtered_df['Abstract'].str.contains(abstract_keyword, case=False, na=False)]

    # Apply author filters last to make sure other filters are considered first
    if 'Authors' in selected_columns and selected_authors:
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
        result = pd.read_csv("pubMedResults.csv", encoding="utf8").applymap(lambda x: x.decode('utf-8', 'replace') if isinstance(x, bytes) else x)
        
        # Preprocess 'Publication Date' column
        result['Publication Date'] = result['Publication Date'].replace("Not Available", pd.NaT)
        
        df = result

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
