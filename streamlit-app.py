import os, sys
import streamlit as st
import pandas as pd
from crewai import Agent, Task, Crew, Process
from textwrap import dedent
from agents import sotaAgents
from tasks import sotaTasks
from crews import SotaReviewCrew
import warnings
warnings.filterwarnings('ignore')

# Streamlit app starts here
def main():
    st.set_page_config(layout="wide", page_title="SOTA Review Crew", page_icon=":rocket:")

    st.title("State-of-the-Art Review Crew")
    st.sidebar.header("Configuration")
    
    # User input for the topic
    topic = st.sidebar.text_input("Enter the review topic:")
    

    if st.sidebar.button("Run Review"):
        with st.spinner("🤖 **Agents at work...**"):
            if os.path.isfile("./pubMedResults.csv"): os.remove("./pubMedResults.csv")
            sota_review_crew = SotaReviewCrew(topic)
            results = sota_review_crew.run()
            # print(results)
        st.success("Review Completed!")

        if os.path.isfile("pubMedResults.csv"):
            result = pd.read_csv("pubMedResults.csv", encoding="utf8").applymap(lambda x: x.decode('utf-8', 'replace') if isinstance(x, bytes) else x)
            st.header("Articles found :")
            #st.dataframe(result, hide_index=True)
            df = result
            # Sidebar for selecting columns and filtering values
            st.sidebar.title('Filter Data')
            selected_columns = st.sidebar.multiselect('Select Columns', df.columns)
            filters = {}
            for column in selected_columns:
                filters[column] = st.sidebar.multiselect(f'Select {column}', df[column].unique())

            # Apply filters
            filtered_df = df
            for column, values in filters.items():
                if values:
                    filtered_df = filtered_df[filtered_df[column].isin(values)]

            # Display filtered data
            st.write('Filtered Data:', filtered_df)

            # Export filtered data
            if st.button('Export Filtered Data'):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label='Download CSV',
                    data=csv,
                    file_name='filtered_data.csv',
                    mime='text/csv'
                )
        else:
            st.header("Seams an error occured")




if __name__ == "__main__":
    main()
