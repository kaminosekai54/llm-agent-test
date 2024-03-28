import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from pubmedTool import PubMedArticleSearchTool
# from langchain_openai import AzureChatOpenAI
# from dotenv import load_dotenv

os.environ["SERPER_API_KEY"] = "e486cce5438cd0aa67f552e97c91b3ca853f4606" # serper.dev API key

# You can choose to use a local model through Ollama for example. See https://docs.crewai.com/how-to/LLM-Connections/ for more information.

os.environ["OPENAI_API_BASE"] = 'http://localhost:11434/v1'
os.environ["OPENAI_MODEL_NAME"] ='mistral'  # Adjust qbased on available model
# os.environ["OPENAI_API_KEY"] ='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'
os.environ["OPENAI_API_KEY"] =''

# os.environ["AZURE_OPENAI_KEY"]="ccdcc67fa8f9415aba782b04fa8650de"

search_tool = SerperDevTool()
pubmedTool = PubMedArticleSearchTool()

# Define your agents with roles and goals
researcher = Agent(
  role='Expert data collector',
  goal='make a selection of article of cuttingedge discovery in cancer treatment',
  backstory="""You work as a cancer researcher in curie institute.
  Your expertise lies in identifying articles presenting innovative and new cancer treatments.
  You are an expert in choosing appropriate keywords and identifying relevant article for any topic.""",
  verbose=True,
  allow_delegation=False,
  tools=[pubmedTool],
)
# Create tasks for your agents
task1 = Task(
  description="""Conduct a comprehensive state of the art report.
  Using a list of apropriate keywords to find the most relevant articles,
  Go through articles and select the most relevant and apropriate ones, combine all search result to create a csv file called resultats.csv.
  """,
  expected_output="csv file of the selected articles metadata",
  agent=researcher
)

# task2 = Task(
  # description="""Using the insights provided, develop an engaging blog
  # post that highlights the most significant AI advancements.
  # Your post should be informative yet accessible, catering to a tech-savvy audience.
  # Make it sound cool, avoid complex words so it doesn't sound like AI.""",
  # expected_output="Full blog post of at least 4 paragraphs",
  # agent=writer
# )

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher],
  tasks=[task1],
  verbose=1, # You can set it to 1 or 2 to different logging levels
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)