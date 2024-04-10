import os
import pandas as pd
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama, OpenAI
from textwrap import dedent
from agents import sotaAgents
from tasks import sotaTasks
import streamlit as st
import warnings
warnings.filterwarnings('ignore')




class SotaReviewCrew:
    def __init__(self, topic, streamlit_Log =False):
        self.topic = topic
        self.output_placeholder = ""
        if streamlit_Log  : self.output_placeholder = st.empty()

    def run(self):
        agents = sotaAgents()
        tasks = sotaTasks()
        # defind the differents agents
        head_manager_agent = agents.headManagerAgent()
        pubmed_data_collector_agent = agents.pubmedDataCollectorAgent(self.topic)
        # pubmed_data_reviewer_agent = agents.pubmedDataReviewerAgent(topic)

        # defind task to be executed
        get_pubmed_data_task = tasks.getPubMedData(pubmed_data_collector_agent)  # Modified to pass topic
        # apply_first_filter_task = tasks.applyFirstFilter2(agent=pubmed_data_reviewer_agent, topic=topic, data=pd.read_csv("pubMedResults.csv").to_json())

        #  defind crew
        crew = Crew(
            agents=[
                pubmed_data_collector_agent,
            ],
            tasks=[
                get_pubmed_data_task,
            ],
            verbose=True,
        )

        result = crew.kickoff()
        if streamlit_Log : self.output_placeholder.markdown(result)
        # for raw in pubmed_data_collector_agent.parse_raw() : print(raw)
        # with open("output.txt", "w") as f : f.write(str(pubmed_data_collector_agent.tools_handler.on_tool_use()))
        # with open("output2.txt", "w") as f : f.write(str(pubmed_data_collector_agent.json))

        return result


# if __name__ == "__main__":
    # print("## Welcome to State-of-the-Art Review Crew")
    # print('-------------------------------')
    # topic = "cancert treatment"

    # topic = input(
        # dedent("""
            # What is the topic for the state-of-the-art review?
        # """))
    
    # sota_review_crew = SotaReviewCrew(topic)
    # result = sota_review_crew.run()
    # print("\n\n########################")
    # print("## Here is the Report")
    # print("########################\n")
    # print(result)
