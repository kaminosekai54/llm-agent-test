import os
import shutil
import streamlit as st
import pandas as pd
from datetime import datetime
from crews import SotaReviewCrew
import warnings

warnings.filterwarnings('ignore')

# @ st.cache_data # Cache the processed dataframe
def preprocess_data(filepath):
    """
    Preprocesses the dataframe by converting date columns and ensuring correct types for other columns.
    """
    df = pd.read_csv(filepath, encoding="utf8").applymap(lambda x: x.decode('utf-8', 'replace') if isinstance(x, bytes) else x)
    # df['Publication Date'] = pd.to_datetime(df['Publication Date'].replace("Not Available", pd.NaT), errors='coerce', format="%d/%m/%Y")
    df['Publication Date'] = df['Publication Date'].replace("Not Available", pd.NaT)
    df['Authors'] = df['Authors'].astype(str)
    df['Article ID'] = df['Article ID'].replace(",", "")

    return df

# Function to display the sidebar filters based on selected columns
def display_filters(df, selected_columns):
    st.sidebar.title('Filter Data')
    filtered_df = df.copy()

    # Filter by authors
    if 'Authors' in selected_columns:
        try:
            all_authors = filtered_df['Authors'].dropna().apply(lambda x: [author.strip() for author in x.split(',')])
            unique_authors = sorted(set([author for sublist in all_authors for author in sublist]))

            # unique_authors = set(author.strip().lower() for authors in df['Authors'].str.split(',') for author in authors if author.strip())
        except Exception as e:
            st.sidebar.error(f"Error processing authors: {e}")
            unique_authors = []
        selected_authors = st.sidebar.multiselect('Filter by Authors', sorted(list(unique_authors)))

        if selected_authors:
            print(selected_authors)
            print({author: author in unique_authors for author in selected_authors})

            filtered_df = filtered_df[filtered_df['Authors'].apply(lambda x: any(author.strip() in selected_authors for author in x.split(',')))]
            print("after author filter:")
            print(filtered_df)

    # Filter by publication date
    if 'Publication Date' in selected_columns:
        print("in date filtering")
        try:
            print("before min date")
            min_date = pd.to_datetime(df['Publication Date'], dayfirst=True).min().date()
            print(min_date)
            max_date = pd.to_datetime(df['Publication Date'], dayfirst=True).max().date()
            print(max_date)
            selected_min_date = st.sidebar.date_input("Select Minimum Publication Date", min_value=min_date, max_value=max_date, value=min_date, format="DD/MM/YYYY")
            selected_max_date = st.sidebar.date_input("Select Maximum Publication Date", min_value=min_date, max_value=max_date, value=max_date, format="DD/MM/YYYY")
            filtered_df = filtered_df[(pd.to_datetime(filtered_df['Publication Date'], dayfirst=True) >= pd.Timestamp(selected_min_date)) & 
                                  (pd.to_datetime(filtered_df['Publication Date'], dayfirst=True) <= pd.Timestamp(selected_max_date))]
        except Exception as e:
            st.sidebar.error(f"Error processing dates: {e}")

    # Filter by title
    if 'Title' in selected_columns:
        title_keyword = st.sidebar.text_input("Search by Title Keyword")
        if title_keyword:
            print("filtering by title apply")
            print(title_keyword)
            filtered_df = filtered_df[filtered_df['Title'].str.contains(title_keyword, case=False, na=False)]
            print("filtering after title key word applied")
            print(filtered_df)

    # Filter by abstract
    if 'Abstract' in selected_columns:
        abstract_keyword = st.sidebar.text_input("Search by Abstract Keyword")
        if abstract_keyword:
            print("filter by abstract")
            print(abstract_keyword)
            filtered_df = filtered_df[filtered_df['Abstract'].str.contains(abstract_keyword, case=False, na=False)]
            print("after abstract filtering")
            print(filtered_df)

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

    # Custom CSS for the top-right button
    st.markdown(
        """
        <style>
        .top-right-button {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Load CSV Button
    uploaded_file = st.file_uploader("", type="csv", label_visibility='collapsed', key='top_right_csv')
    st.markdown('<div class="top-right-button">Load CSV</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        df = preprocess_data(uploaded_file)

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
    
    # User input for the topic
    topic = st.sidebar.text_input("Enter the review topic:")
    start_date = (datetime.now() - pd.DateOffset(years=5))
    end_date = datetime.now()
    selected_min_date_for_search = st.sidebar.date_input("Select Minimum Publication Date", max_value=end_date, value=start_date , format="DD/MM/YYYY")
    selected_max_date_for_search  = st.sidebar.date_input("Select Maximum Publication Date", min_value=selected_min_date_for_search, max_value=end_date, value=end_date, format="DD/MM/YYYY")
    
    if st.sidebar.button("Run Review"):
        with st.spinner("🤖 **Agents at work...**"):
            if os.path.isfile("./pubMedResults.csv"): os.remove("./pubMedResults.csv")
            print("topic choose :", topic)
            print(selected_min_date_for_search.strftime("%d/%m/%Y"))
            print(selected_max_date_for_search.strftime("%d/%m/%Y"))
            sota_review_crew = SotaReviewCrew(topic, start_date=selected_min_date_for_search.strftime("%d/%m/%Y"), end_date=selected_max_date_for_search.strftime("%d/%m/%Y"))
            results = sota_review_crew.run()
        st.success("Review Completed!")
        fileList = sorted([file for file in os.listdir("searchResults/") if topic.replace(" ", "-") in file])
        if len(fileList) > 0:
            # Preprocess 'Publication Date' column
            df = preprocess_data(f"searchResults/{fileList[-1]}")


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
        if os.path.isdir("__pycache__"): shutil.rmtree("__pycache__")
    main()
