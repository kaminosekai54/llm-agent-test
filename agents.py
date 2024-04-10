import streamlit as st
import os
from textwrap import dedent
from crewai import Agent
from pubmedTool import PubMedArticleSearchTool
from crewai_tools import CSVSearchTool
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

#  env variables    
load_dotenv()
 
llm_model = AzureChatOpenAI(
    openai_api_version=os.environ.get("AZURE_OPENAI_VERSION"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
)
pubmedTool = PubMedArticleSearchTool()


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
                                You always find the most relevant keywords and identify the most fitting articles. You always provide a well-formatted output, respecting the imposed requirements.You always give a well formated output, respecting the imposed requieredment.
                                You always make sure that your data are well formatted.
                             You only accept articles in french or english and with in a specific date range, if not specified, with in the last 5 years.
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