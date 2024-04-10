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
                sota_review_crew = SotaReviewCrew(topic)
                results = sota_review_crew.run()
                print(results)


        st.success("Review Completed!")

        if os.path.isfile("pubMedResults.csv"):
            result = pd.read_csv("pubMedResults.csv", encoding="utf8")
            st.header("Articles found :")
            st.dataframe(result, hide_index=True)
        else:
            st.header("Seams an error occured")




if __name__ == "__main__":
    main()