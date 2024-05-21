import streamlit as st
import os
from textwrap import dedent
from crewai import Agent
from pubmedTool import PubMedArticleSearchTool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import config

configs = config.getConfigs()
from crewai_tools import CSVSearchTool
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from tools import pubMedArticleSearch
#  env variables    
load_dotenv()
 
# llm_model =ChatGroq(
            # api_key=os.getenv("GROQ_API_KEY"),
            # model="mixtral-8x7b-32768"
            # model="llama2-70b-4096"
            # model="llama3-70b-8192"
        # ) 
pubmedTool = pubMedArticleSearch

def getLLMModel(modelName):
    llm_model = "not defind"
    if modelName == "llama3_groq":
        llm_model =ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama3-70b-8192"
        )
    elif modelName == "mixtrale_groq" :
        llm_model =ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="mixtral-8x7b-32768"
        )

    elif modelName == "azure_gpt4":
        llm_model = AzureChatOpenAI(
    openai_api_version=os.environ.get("AZURE_OPENAI_VERSION"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
)
    
    return llm_model





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
            llm=getLLMModel(configs["agents"]["headManagerAgent"]["model"]),

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
            llm=getLLMModel(configs["agents"]["pubmedDataCollectorAgent"]["model"]),

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
            llm=getLLMModel(configs["agents"]["headManagerAgent2"]["model"]),
                            #  step_callback=streamlit_callback,
                             )
    
    def pubmedDataSearcherAgent(self, topic):
        return Agent(
            role='Keyword Discovery Specialist',
            goal=f"Efficiently identify and select potent keywords to optimize the search and retrieval of relevant articles on {topic}.",
            backstory=dedent(f"""
                                Entrusted as a Keyword Discovery Specialist on {topic}, your adeptness at pinpointing exact keywords revolutionizes the way articles are searched and found.
                                Your insights derive from a profound understanding of diverse topics, enabling the extraction of the most impactful search terms.
                                Be careful to not be to generalist, stay close to the specific topic.
                                This skill not only enhances search efficiency but also elevates the relevance of the retrieved articles.
                             Your role is pivotal in streamlining research processes, ensuring only the most pertinent information is accessed.
                                """ ),
            allow_delegation=False,
            verbose=True,
            llm=getLLMModel(configs["agents"]["pubmedDataSearcherAgent"]["model"]),
            # step_callback=streamlit_callback,
            )
 