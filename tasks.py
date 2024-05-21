from crewai import Task
from textwrap import dedent
from pubmedTool import PubMedArticleSearchTool
pubmedTool = PubMedArticleSearchTool()



class sotaTasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission ! and you will help to save the world !"

    def getPubMedData(self, agent, start_date, end_date):
        return Task(
            description=dedent(
                f"""
                Find relevant articles on pubmed in the following date range :
                start_date = {start_date}
end_date = {end_date}
            {self.__tip_section()}
        """
            ),
            expected_output = dedent(
                f"""
Yes if the data could be retreaved, no overwise
                """),

            agent=agent,
            # output_file= "./res.txt",
        )


    def applyFirstFilter(self, agent, topic, context):
        return Task(
            description=dedent(
                f"""
                Parse a csv file line by line to ensure the validity of data.
                If the data are not respecting the following exclusion criteria, remove it from the original file and add it to another one, adding a column for the exclusion reason.
            
                Base your choice on the tittle and abstract values.

                Exclusion criteria :
                - no abstract.
                - article not published with in the past 5 years.
                - article not in english or french.
                - tittle or abstract not relevant for a state of the art review on {topic}.
            {self.__tip_section()}
        """
            ),
            expected_output = dedent(
                f"""
2 list in json format :
The first one correspond to the articles id of the selected articles.
The second one correspond to the list of the none selected articles and the reason of the none selection.
                """),
            agent=agent,
            context=context 
        )
    
    def test(self, agent):
        return Task(
            description=dedent(
                f"""
            Search PubMed for specific articles and return results as JSON.
            {self.__tip_section()}
        """
            ),
            expected_output = dedent(
                f"""
            JSON file with search results.
                """),

            agent=agent,
            tools=[pubmedTool],
            output_file= "./res.txt",
        )



    def applyFirstFilter2(self, agent, topic, data):
        return Task(
            description=dedent(
                f"""
                Given the provided data in json format ensure the validity of data.
                For all data entree check If the data are not respecting the following exclusion criteria, remove it from the original file and add it to another one, adding a column for the exclusion reason.
            
                Base your choice on the tittle and abstract values.

                Exclusion criteria :
                - no abstract.
                - article not published with in the past 5 years.
                - article not in english or french.
                - tittle or abstract not relevant for a state of the art review on {topic}.
            {self.__tip_section()}

data: 
{data}
        """
            ),
            expected_output = dedent(
                """
A json file containing the id of selected article, the id of none selected article and the reason why.
For example :
[
    {"selectedArticle":["1", "2",]},
    {"notSelectedArticle":[ 
     {"id":"3", "reason":"wrong langage"}, {"id":"6", "reason":"not related to the topic"}
    ]
    }
]

                """),
            agent=agent,
            output_file= "./res.txt",
        )

    def generateKeywordsTask(self, agent):
        return Task(
            description=dedent(
                f"""
                generate a list of primary and secondary keywords that are currently used to find articles on the topic, ensuring a blend of broad and specific terms.
                Also find intresting combinaison of those keywords.
 
            {self.__tip_section()}
        """
            ),
            expected_output = dedent(
                f"""
                A string containing a pipe -separated list of keywords relevant to the topic.
                The format should be as follows: "keyword1 | keyword2 | keyword3 | keywordN".
                It should contain 5 to 20 key words, including combinaisons if relevant..
                """),
 
            agent=agent,
        )