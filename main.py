import os
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama, OpenAI
from textwrap import dedent
from agents import sotaAgents
from tasks import sotaTasks
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')
load_dotenv()

class SotaReviewCrew:
    def __init__(self, topic):
        self.topic = topic

    def run(self):
        agents = sotaAgents()
        tasks = sotaTasks()

        head_manager_agent = agents.headManagerAgent()
        pubmed_data_collector_agent = agents.pubmedDataCollectorAgent()

        get_pubmed_data_task = tasks.getPubMedData(pubmed_data_collector_agent)  # Modified to pass topic
        apply_first_filter_task = tasks.applyFirstFilter(pubmed_data_collector_agent)  # Assuming this task also needs topic, you can modify it similarly

        crew = Crew(
            agents=[
                head_manager_agent,
                pubmed_data_collector_agent,
            ],
            tasks=[
                get_pubmed_data_task,
                apply_first_filter_task,
            ],
            verbose=True
        )

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    print("## Welcome to State-of-the-Art Review Crew")
    print('-------------------------------')
    topic = input(
        dedent("""
            What is the topic for the state-of-the-art review?
        """))
    
    sota_review_crew = SotaReviewCrew(topic)
    result = sota_review_crew.run()
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")
    print(result)
