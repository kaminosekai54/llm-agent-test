import os
import pandas as pd
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama, OpenAI
from textwrap import dedent
from agents import sotaAgents
from tasks import sotaTasks
import warnings
warnings.filterwarnings('ignore')



class SotaReviewCrew:
    def __init__(self, topic):
        self.topic = topic

    def run(self):
        agents = sotaAgents()
        tasks = sotaTasks()

        # head_manager_agent = agents.headManagerAgent()
        pubmed_data_collector_agent = agents.pubmedDataCollectorAgent(self.topic)
        # pubmed_data_reviewer_agent = agents.pubmedDataReviewerAgent(topic)

        get_pubmed_data_task = tasks.getPubMedData(pubmed_data_collector_agent)  # Modified to pass topic
        # get_pubmed_data_task = tasks.test(pubmed_data_collector_agent)  

        # apply_first_filter_task = tasks.applyFirstFilter2(agent=pubmed_data_reviewer_agent, topic=topic, data=pd.read_csv("pubMedResults.csv").to_json())

        crew = Crew(
            agents=[
                # head_manager_agent,
                pubmed_data_collector_agent,
                # pubmed_data_reviewer_agent ,
            ],
            tasks=[
                get_pubmed_data_task,
                # save_pubmed_data_task,
                # apply_first_filter_task,
            ],
            verbose=True,
            # process="hierarchical",
            # manager_llm = head_manager_agent,
        )

        result = crew.kickoff() 
        # for raw in pubmed_data_collector_agent.parse_raw() : print(raw)
        # with open("output.txt", "w") as f : f.write(str(pubmed_data_collector_agent.tools_handler.on_tool_use()))
        # with open("output2.txt", "w") as f : f.write(str(pubmed_data_collector_agent.json))

        return result

