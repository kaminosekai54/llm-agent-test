import streamlit as st
import os
from textwrap import dedent
from crewai import Agent
from pubmedTool import PubMedArticleSearchTool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from crewai_tools import CSVSearchTool
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from tools import pubMedArticleSearch
#  env variables    
load_dotenv()
 
# llm_model = AzureChatOpenAI(
    # openai_api_version=os.environ.get("AZURE_OPENAI_VERSION"),
    # azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    # azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
# )
llm_model =ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="mixtral-8x7b-32768"
        ) 
# pubmedTool = PubMedArticleSearchTool()
pubmedTool = pubMedArticleSearch


def streamlit_callback(step_output):
    # This function will be called after each step of the agent's execution
    st.markdown("---")
    for step in step_output:
        if isinstance(step, tuple) and len(step) == 2:
            action, observation = step
            if isinstance(action, dict) and "tool" in action and "tool_input" in action and "log" in action:
                st.markdown(f"# Action")
                st.markdown(f"**Tool:** {action['tool']}")
                st.markdown(f"**Tool Input** {action['tool_input']}")
                st.markdown(f"**Log:** {action['log']}")
                st.markdown(f"**Action:** {action['Action']}")
                st.markdown(
                    f"**Action Input:** ```json\n{action['tool_input']}\n```")
            elif isinstance(action, str):
                st.markdown(f"**Action:** {action}")
            else:
                st.markdown(f"**Action:** {str(action)}")

            st.markdown(f"**Observation**")
            if isinstance(observation, str):
                observation_lines = observation.split('\n')
                for line in observation_lines:
                    if line.startswith('Title: '):
                        st.markdown(f"**Title:** {line[7:]}")
                    elif line.startswith('Link: '):
                        st.markdown(f"**Link:** {line[6:]}")
                    elif line.startswith('Snippet: '):
                        st.markdown(f"**Snippet:** {line[9:]}")
                    elif line.startswith('-'):
                        st.markdown(line)
                    else:
                        st.markdown(line)
            else:
                st.markdown(str(observation))
        else:
            st.markdown(step)

class sotaAgents():
    def headManagerAgent(self):
        return Agent(
            role='Senior manager',
            goal='Accurately assign tasks and assess the quality of task executions, Provide valuable insights and make good decisions to get the job done.',
            backstory=dedent("""\
                             You are a Senior manager of a renowned research team.
                             You are an expert at assigning the right person to the right task.
                             You perfectly know how to follow guidelines, review other people's work.
                             You always give amazing advice and insight to achieve the best outcomes possible.
                             """),
                             allow_delegation=True,
                             verbose=True,
                                tools=[pubmedTool],
                             llm=llm_model,
                            #  step_callback=streamlit_callback,
                             )
    

    def pubmedDataCollectorAgent(self, topic):
        return Agent(
            role='Experience data collector',
            goal=f"Choose the appropriate keywords to perform a state of the art review of {topic}",
            backstory=dedent(f"""
                                You are an expert in the {topic}
                                You are the best at collecting scientific articles on pubmed. 
                                You always find the most relevant keywords and identify the most fitting articles. You always provide a well-formatted output, respecting the imposed requirements.
                                You always make sure that your data are well formatted.
                             You only accept articles in french or english.
                                """),
                                tools=[pubmedTool],

            allow_delegation=False,

            verbose=True,

            llm=llm_model,
            # step_callback=streamlit_callback,
            )

    def pubmedDataReviewerAgent(self, topic):
        return Agent(
            role='Experience data reviewer',
            goal=f"Review the collected data on {topic}",
            backstory=dedent(f"""
                                You are an expert in the {topic}.
                                You are the best at evaluating if an article fit a topic or not and is relevant to use for a state of the art report. 
                                You always review carefully the each data before deciding to keep it or not.
                             You only accept articles in french or english and with in a specific date range, if not specified, with in the last 5 years.
                                """),
                                tools=[csvTool],

            allow_delegation=False,
            verbose=True,
            llm=llm_model,
            # step_callback=streamlit_callback,
            )
    
    def headManagerAgent2(self):
        return Agent(
            role='Head Manager ',
            goal='Enable efficient team coordination and enhance decision-making by accurately delegating tasks, evaluating execution quality, and delivering actionable insights.',
            backstory=dedent("""\
                             You helm a top-tier research team, recognized for groundbreaking work.
                             With a talent for task delegation, you pair each challenge with the perfect candidate.
                             Your mastery in following and enforcing guidelines ensures flawless project execution.
                             You are known for insightful feeback that transforms obstacles into opportunities.
                             Achieving excellence is your standard, guided by your strategic decisions and advice.
                             """),
                             allow_delegation=True,
                             verbose=True,
                                tools=[pubmedTool],
                             llm=llm_model,
                            #  step_callback=streamlit_callback,
                             )
    

    def pubmedDataCollectorAgent2(self, topic):
        return Agent(
            role='Strategic Insight Gatherer',
            goal=f"Select the optimal keywords to conduct a comprehensive review of the current state of the art of {topic}",
            backstory=dedent(f"""
                                You are an expert in {topic}, known for your unparalleled ability to navigate PubMed for scientific literature.
                                Your skill in selecting the most relevant keywords ensures you always identify the articles that matter.
                                Precision in formatting means your outputs consistently meets the highest standards.
                                You specialize in articles in French or English, focusing on works from the last five years unless otherwise specified.
                             Your commitment to quality and relevance in data collection sets you appart in the field.
                                """),
                                tools=[pubmedTool],

            allow_delegation=False,

            verbose=True,

            llm=llm_model,
            step_callback=streamlit_callback,
            )

    def pubmedDataReviewerAgent2(self, topic):
        return Agent(
            role='Comprehensive Data Evaluation Expert',
            goal=f"Critically analyze and validate gathered data on {topic} to ensure its accuracy, relevance, and contribution to knowledge enhancement.",
            backstory=dedent(f"""
                                As an authority on {topic}, your expertise shines in identifying articles that precisely match the thematic requirements for cutting-edge research compilations.
                                With a discerning eye, you meticulously evaluate each piece of data, ensuring its utmost relevance and reliability before inclusion. 
                                Your preference for articles in French or English, coupled with a steadfast focus on works published within the most recent five year period, underscores your commitment to contemporary relevance.
                             This methodical approach solidifies your status as a beacon of excellence in data verification and selection.
                                """),
                                tools=[csvTool],

            allow_delegation=False,
            verbose=True,
            llm=llm_model,
            step_callback=streamlit_callback,
            )
    
    def pubmedDataSearcherAgent(self, topic):
        return Agent(
            role='Keyword Discovery Specialist',
            goal=f"Efficiently identify and select potent keywords to optimize the search and retrieval of relevant articles on {topic}.",
            backstory=dedent(f"""
                                Entrusted as a Keyword Discovery Specialist on {topic}, your adeptness at pinpointing exact keywords revolutionizes the way articles are searched and found.
                                Your insights derive from a profound understanding of diverse topics, enabling the extraction of the most impactful search terms.
                                This skill not only enhances search efficiency but also elevates the relevance of the retrieved articles.
                             Your role is pivotal in streamlining research processes, ensuring only the most pertinent information is accessed.
                                """ ),
            allow_delegation=False,
            verbose=True,
            llm=llm_model,
            # step_callback=streamlit_callback,
            )
    
    def pubmedDataResearchAnalystAgent(self, topic):
        return Agent(
            role='Strategic Research Analyst',
            goal=f"Leverage expertly selected keywords to conduct deep and comprehensive research, uncovering the most relevant and insightful articles.",
            backstory=dedent(f"""
                                As a Strategic Research Analyst on {topic}, you wield the power of meticulously chosen keywords to navigate vast information, unearthing articles that are gems of knowledge and insight.
                                Your methodology is refined, drawing on the precision work of your predecessor, the Keyword Discovery Specialist, to target your searches with unparalleled accuracy.
                                Your role bridges the gap between broad data pools and specific informational needs, ensuring research efforts are efficient.
                             Through your expertise, the process of transforming raw data into actionable intelligence is both streamlined and elevated, making you an invaluable asset to the research initiative.
                               """),
                               tools=[pubmedTool],

            allow_delegation=False,
            verbose=True,
            llm=llm_model,
            # step_callback=streamlit_callback,
            )
