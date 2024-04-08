from crewai import Task
from textwrap import dedent
from pubmedTool import PubMedArticleSearchTool
pubmedTool = PubMedArticleSearchTool()



class sotaTasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission ! and you will help to save the world !"

    def getPubMedData(self, agent):
        return Task(
            description=dedent(
                f"""
            Collect the most relevant articles to conduct a complete state of the art review.
            All the differents keywords will be combined during the search.
            So, give a particular attention to  use the apropriate keywords and date range.
            Save the results in a csv file called pubMedRes.csv or concatenate the results to the existing csv file
            {self.__tip_section()}
        """
            ),
            expected_output = dedent(
                f"""
                Using the output of the pubmed tool, representing the search results
                Write a csv file called pubMedResults.csv containing the following articles meta data : 
            ArticleID, Title, Journal, Authors, PublicationDate, ArticleType, DOI, Abstract, OpenAccess, FullTextAvailable
            No report are expected,
            No comments are expected
            Only the csv file of the results.
                """),

            agent=agent,
            output_file= "./res.txt",

        )

    def savePubMedData(self, agent, data):
        return Task(
            description=dedent(
                f"""
                Using the following data :
                {data}
            Save the results of the pubmed search results in a csv file called pubMedResults.csv.
            If the file already exist, concat the new data to the existing file and save it.
            {self.__tip_section()}
        """
            ),
            expected_output = dedent(
                f"""
Only a csv file called pubMedResults.csv containing the following articles meta data : 
            ArticleID, Title, Journal, Authors, PublicationDate, ArticleType, DOI, Abstract, OpenAccess, FullTextAvailable
                """),

            agent=agent,
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
