import os
import pandas as pd
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama, OpenAI
from textwrap import dedent
from agents import sotaAgents
from tasks import sotaTasks
import streamlit as st
import streamlit.components.v1 as components
import warnings
warnings.filterwarnings('ignore')

class SotaReviewCrew:
    def __init__(self, topic, start_date, end_date, streamlit_Log=False):
        self.topic = topic
        self.start_date = start_date
        self.end_date = end_date
        self.output_placeholder = ""
        self.streamlit_Log = streamlit_Log
        if self.streamlit_Log:
            self.output_placeholder = st.empty()

    def initialize_session_state(self):
        if "results" not in st.session_state:
            st.session_state.results = []
        if "feedback" not in st.session_state:
            st.session_state.feedback = ""
        if "iteration" not in st.session_state:
            st.session_state.iteration = 0
        if "satisfied" not in st.session_state:
            st.session_state.satisfied = False

    def interactive_chat(self, agent):
        self.initialize_session_state()
        try:
            t = sotaTasks()
            st.write("Tasks object created successfully")

            try:
                task = t.generateKeywordsTask(agent, self.topic)
                st.write("Keywords task generated successfully")
            except Exception as e:
                st.error(f"An error occurred while generating the keywords task: {str(e)}")
                return

            try:
                crew = Crew(
                    agents=[agent],
                    tasks=[task],
                    process=Process.sequential,
                    verbose=True
                )
                st.write("Crew created successfully")
            except Exception as e:
                st.error(f"An error occurred while creating the Crew: {str(e)}")
                return

            try:
                result = crew.kickoff(inputs={'topic': self.topic})
                st.session_state.results.append(f"Here is the proposed key words for your search: {result}")
                st.write("Initial task executed successfully")
            except Exception as e:
                st.error(f"An error occurred during the initial task execution: {str(e)}")
                return

            for message in st.session_state.results:
                st.chat_message("assistant").write(message)

            while not st.session_state.satisfied:
                feedback = st.chat_input("Please provide your feedback:")
                if feedback:
                    st.session_state.feedback = feedback
                    st.session_state.results.append(f"User Feedback: {feedback}")
                    st.chat_message("user").write(feedback)

                    new_task = t.generateKeywordsTask(agent, self.topic)
                    crew.tasks = [new_task]
                    result = crew.kickoff(inputs={'topic': self.topic})
                    st.session_state.results.append(f"Updated Task Result: {result}")
                    st.chat_message("assistant").write(f"Updated Task Result: {result}")

                    st.session_state.feedback = ""
                    st.experimental_rerun()  # Rerun to clear feedback input

                if st.button("Launch Search"):
                    st.session_state.satisfied = True

            return result
        except Exception as e:
            st.error(f"An error occurred during the interactive chat: {str(e)}")

    def run(self):
        try:
            agents = sotaAgents()
            tasks = sotaTasks()
            # Define the different agents
            head_manager_agent = agents.headManagerAgent()
            pubmed_keywords_searcher = agents.pubmedDataSearcherAgent(self.topic)
            pubmed_data_collector_agent = agents.pubmedDataCollectorAgent(self.topic)

            # Interactive chat for refining keywords
            refined_keywords_result = self.interactive_chat(pubmed_keywords_searcher)

            # Define tasks to be executed
            get_pubmed_data_task = tasks.getPubMedData(pubmed_data_collector_agent, self.start_date, self.end_date)

            # Define crew with updated agents and tasks
            crew = Crew(
                agents=[
                    pubmed_keywords_searcher,
                    pubmed_data_collector_agent,
                ],
                tasks=[
                    get_pubmed_data_task,
                ],
                verbose=True,
            )

            result = crew.kickoff()
            if self.streamlit_Log:
                self.output_placeholder.markdown(result)

            return result
        except Exception as e:
            st.error(f"An unexpected error occurred while running the review: {str(e)}")
