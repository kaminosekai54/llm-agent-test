import os
from textwrap import dedent
from crewai import Agent
from langchain_community.llms import Ollama
from pubmedTool import PubMedArticleSearchTool
from crewai_tools import SerperDevTool
from csvTool import csvTool
from crewai_tools import CSVSearchTool

# from langchain_community.tools.pubmed.tool import PubmedQueryRun
# tool = PubmedQueryRun()
os.environ["SERPER_API_KEY"] = "e486cce5438cd0aa67f552e97c91b3ca853f4606" # serper.dev API key
#  env variables    
os.environ["OPENAI_API_BASE"] = 'http://localhost:11434/v1'
os.environ["OPENAI_API_KEY"] =''

searchTool= SerperDevTool()
pubmedTool = PubMedArticleSearchTool()
# pubmedTool = PubmedQueryRun()
# csvTool = csvTool()
# retool = CSVSearchTool(csv='pubMedResults.csv ')

llm_model = Ollama(model="mistral")

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
                             llm=llm_model
                             )
    

    def pubmedDataCollectorAgent(self, topic):
        return Agent(
            role='Experience data collector',
            goal=f"Choose the appropriate keywords to perform a state of the art review of {topic}",
            backstory=dedent(f"""
                                You are an expert in the {topic}
                                You are the best at collecting data on pubmed. 
                                You always find the most relevant keywords and identify the most fitting articles. You always provide a well-formatted output, respecting the imposed requirements.You always give a well formated output, respecting the imposed requieredment.
                                You always make sure that your data are well formatted.
                             You only accept articles in french or english and with in a specific date range, if not specified, with in the last 5 years.
                                """),
                                tools=[pubmedTool],

            allow_delegation=False,

            verbose=True,

            llm=llm_model
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
            llm=llm_model
            )