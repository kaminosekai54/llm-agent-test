import os, sys
import streamlit as st
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
        self.output_placeholder = st.empty()

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
        self.output_placeholder.markdown(result)
        # for raw in pubmed_data_collector_agent.parse_raw() : print(raw)
        # with open("output.txt", "w") as f : f.write(str(pubmed_data_collector_agent.tools_handler.on_tool_use()))
        # with open("output2.txt", "w") as f : f.write(str(pubmed_data_collector_agent.json))

        return result

# Streamlit app starts here
def main():
    st.set_page_config(layout="wide", page_title="SOTA Review Crew", page_icon=":rocket:")

    st.title("State-of-the-Art Review Crew")
    st.sidebar.header("Configuration")
    
    # User input for the topic
    topic = st.sidebar.text_input("Enter the review topic:")
    

    if st.sidebar.button("Run Review"):
        with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
                with st.container(height=500, border=False):
                    sota_review_crew = SotaReviewCrew(topic)
                    results = sota_review_crew.run()
                status.update(label="✅ Articles for sota found !",
                      state="complete", expanded=False)

        st.success("Review Completed!")

        if os.path.isfile("pubMedResults.csv"):
            result = pd.read_csv("pubMedResults.csv")
            st.header("Articles found :")
            st.dataframe(result)
        else:
            st.header("Seams an error occured")




if __name__ == "__main__":
    main()
