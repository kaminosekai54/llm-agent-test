from crewai import Task
from textwrap import dedent


class sotaTasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission ! and you will help to save the world !"

    def getPubMedData(self, agent):
        return Task(
            description=dedent(
                f"""
            Collect the most relevant articles to conduct a proper state of the art review.
            
            {self.__tip_section()}

            Make sure to use the apropriate keywords and date range.
            The output should be a csv file including the following informations :
            ArticleID, Title, Journal, Authors, PublicationDate, ArticleType, DOI, Abstract, OpenAccess, FullTextAvailable
        """
            ),
            expected_output = dedent(
                f"""
A csv file containing the following articles meta data : 
            ArticleID, Title, Journal, Authors, PublicationDate, ArticleType, DOI, Abstract, OpenAccess, FullTextAvailable
                """),

            agent=agent,
        )

    def applyFirstFilter(self, agent):
        return Task(
            description=dedent(
                f"""
            Using the tittle and abstract collected in the pubmed data collection task,
            Ensure that they are in the desired range of publication date, they are either in english or french and relevant to the topic asked.
            Clean the original csv and create a new csv file for the removed articles,adding a column for the reason of exclusion.

                                       
            {self.__tip_section()}

        """
            ),
            expected_output = dedent(
                f"""
2 csv file, the modified csv from the first data collection task, with the none selected article removed and a second csv file containing the none selected meta data of the none selected articles, with an extra column explaining why they are not selected
                """),
            agent=agent,
        )