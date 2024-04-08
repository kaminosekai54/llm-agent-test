import os
import streamlit as st
import pandas as pd
from crews import SotaReviewCrew
import warnings
import logging
from io import StringIO
import time  # To simulate delays for demonstrating real-time logging
warnings.filterwarnings('ignore')

def setup_logging():
    log_stream = StringIO()  # Create a stream to capture logging output
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        stream=log_stream)
    return log_stream
# Custom logging handler to integrate with Streamlit
class StreamlitLoggingHandler(logging.Handler):
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder

    def emit(self, record):
        log_entry = self.format(record)
        self.placeholder.text(log_entry)  # Update the placeholder with the log message

# Streamlit app starts here
def main():
    st.set_page_config(layout="wide", page_title="SOTA Review Crew", page_icon=":rocket:")

    st.title("State-of-the-Art Review Crew")
    st.sidebar.header("Configuration")
    
    # User input for the topic
    topic = st.sidebar.text_input("Enter the review topic:")

    if st.sidebar.button("Run Review"):
        # Placeholder for live console output
        console_output_placeholder = st.empty()

        # Set up logging with a custom handler that writes to the Streamlit placeholder
        # logger = logging.getLogger(__name__)
        # logger.setLevel(logging.INFO)
        # streamlit_handler = StreamlitLoggingHandler(console_output_placeholder)
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # streamlit_handler.setFormatter(formatter)
        # logger.addHandler(streamlit_handler)
        # logger.info("Review process started...")

        with st.spinner("Processing..."):
            # Simulated processing and logging
            sota_review_crew = SotaReviewCrew(topic).run()
            # for _ in range(5):  # Simulating the review process with some logs
                # time.sleep(1)  # Simulate time delay
                # logger.info(f"Processing {topic}...")

            st.success("Review Completed!")
            # logger.removeHandler(streamlit_handler)  # Clean up the handler

            # Display the final result (assuming it's a DataFrame)
            if os.path.isfile("pubMedResults.csv"):
                result = pd.read_csv("pubMedResults.csv")
                st.header("Articles found :")
                st.dataframe(result)
            else:
                st.header("Seams an error occured")




if __name__ == "__main__":
    main()
