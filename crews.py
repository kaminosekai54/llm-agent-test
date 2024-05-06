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
    def __init__(self, topic, start_date, end_date, streamlit_Log =False):
        self.topic = topic
        self.start_date = start_date
        self.end_date = end_date
        self.output_placeholder = ""
        self.streamlit_Log = streamlit_Log 
        if self.streamlit_Log : self.output_placeholder = st.empty()

    def run(self):
        agents = sotaAgents()
        tasks = sotaTasks()
        # defind the differents agents
        head_manager_agent = agents.headManagerAgent()
        pubmed_keywords_searcher= agents.pubmedDataSearcherAgent(self.topic)
        pubmed_data_collector_agent = agents.pubmedDataCollectorAgent(self.topic)

        # defind task to be executed
        get_keywords_task= tasks.generateKeywordsTask(pubmed_keywords_searcher)
        get_pubmed_data_task = tasks.getPubMedData(pubmed_data_collector_agent, self.start_date, self.end_date) 
        # apply_first_filter_task = tasks.applyFirstFilter2(agent=pubmed_data_reviewer_agent, topic=topic, data=pd.read_csv("pubMedResults.csv").to_json())

        #  defind crew
        crew = Crew(
            agents=[
                pubmed_keywords_searcher,
                pubmed_data_collector_agent ,
            ],
            tasks=[
                get_keywords_task,
                get_pubmed_data_task,
            ],
            verbose=True,
        )

        result = crew.kickoff()
        if self.streamlit_Log : self.output_placeholder.markdown(result)
        # for raw in pubmed_data_collector_agent.parse_raw() : print(raw)
        # with open("output.txt", "w") as f : f.write(str(pubmed_data_collector_agent.tools_handler.on_tool_use()))
        # with open("output2.txt", "w") as f : f.write(str(pubmed_data_collector_agent.json))

        return result


# if __name__ == "__main__":
#     print("## Welcome to State-of-the-Art Review Crew")
#     print('-------------------------------')

#     topic = input(
#         dedent("""
#             What is the topic for the state-of-the-art review?
#         """))
    
#     sota_review_crew = SotaReviewCrew(topic)
#     result = sota_review_crew.run()
#     print("\n\n########################")
#     print("## Here is the Report")
#     print("########################\n")
#     print(result)
