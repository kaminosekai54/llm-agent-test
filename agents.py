import os
from textwrap import dedent
from crewai import Agent
from langchain_community.llms import Ollama
from pubmedTool import PubMedArticleSearchTool
from crewai_tools import SerperDevTool
from csvTool import csvTool
os.environ["SERPER_API_KEY"] = "e486cce5438cd0aa67f552e97c91b3ca853f4606" # serper.dev API key
#  env variables    
os.environ["OPENAI_API_BASE"] = 'http://localhost:11434/v1'
os.environ["OPENAI_API_KEY"] =''

searchTool= SerperDevTool()
pubmedTool = PubMedArticleSearchTool()
csvTool = csvTool()


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
                             llm=Ollama(model="mistral")
                             )
    

    def pubmedDataCollectorAgent(self):
        return Agent(
            role='Experience data collector',
            goal='Choose the appropriate keywords to perform a state of the art review',
            backstory=dedent("""\
                                You are an expert of the medical, bio-medical and health care domains.
                                You are the best at collecting data on pubmed. 
                                You always find the most relevant keywords and identify the most fitting articles. You always give a well formated output, respecting the imposed requieredment.
                                You always make sure that your data are formated correctly.
                             You only accept articles in french or english and with in a specific date range, if not specified, with in the last 5 years.
                             You are flexible in the selective constrinct that can be given to you.
                                """),
                                tools=[pubmedTool, csvTool],

            allow_delegation=False,

            verbose=True,

            llm=Ollama(model="mistral")
            )
