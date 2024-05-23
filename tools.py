from metapub import PubMedFetcher
from crewai_tools import BaseTool
import pandas as pd
from datetime import datetime
from crewai_tools import tool
import os
import math
import shutil
from dotenv import load_dotenv
from pydantic.config import ConfigDict
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from cachetools import cached, TTLCache
from ratelimit import limits, sleep_and_retry
from time import sleep
from backoff import on_exception, expo
from requests.exceptions import ChunkedEncodingError, ConnectionError
import time

load_dotenv()
os.environ["NCBI_API_KEY"] = "6361fb3062c6904a3bdda0295e65998f0408"
# metapub.config["NCBI_API_KEY"] = os.getenv("NCBI_API_KEY")

cache = TTLCache(maxsize=1000, ttl=3600)
MAX_CALLS_PER_SECOND = 3  # Adjust this number based on the API's allowed rate limit
SECONDS = 1



@cached(cache)
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=SECONDS)
@on_exception(expo, (ChunkedEncodingError, ConnectionError), max_tries=5)
def getpmid(keyword, year, nb_article_per_year):
    fetcher = PubMedFetcher(cachedir='./cachedir')
    try:
        return fetcher.pmids_for_query(keyword, retmax=nb_article_per_year, since=f"{year}/01/01", until=f"{year}/12/31")
    except Exception as e:
        print(f"Error while fetching article IDs for keyword '{keyword}': {e}")
        return []


@cached(cache)
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=SECONDS)
@on_exception(expo, (ChunkedEncodingError, ConnectionError), max_tries=5)
def fetch_article_ids(keyword, start_year, end_year, nb_article_per_year):
    fetcher = PubMedFetcher(cachedir='./cachedir')
    article_ids = []

    try:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(getpmid, keyword, year, nb_article_per_year) for year in range(start_year, end_year + 1)]
            for future in as_completed(futures):
                article_ids.extend(future.result())
                
        return article_ids
    except Exception as e:
        print(f"Error while fetching article IDs for keyword '{keyword}': {e}")
        return article_ids 

@cached(cache)
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=SECONDS)
@on_exception(expo, (ChunkedEncodingError, ConnectionError), max_tries=5)
def fetch_article_data(pmid):
    fetcher = PubMedFetcher(cachedir='./cachedir')
    try:
        article = fetcher.article_by_pmid(pmid)
                        # Intermediate variables with default values
        article_id = "No ID available"
        title = "No title available"
        journal = "No journal available"
        authors = "No authors listed"
        pub_date = "Not Available"
        article_type = "Article type "
        doi = "No doi found"
        abstract = "No abstract available"
        # Try to retrieve attribute values
        try:
            article_id = getattr(article, 'pmid', 'No ID available')
        except Exception as e:
            print(f"Error while retrieving article ID for PMID {pmid}: {e}")

        try:
            title = getattr(article, 'title', 'No title available')
        except Exception as e:
            print(f"Error while retrieving title for PMID {pmid}: {e}")

        try:
            journal = getattr(article, 'journal', 'No journal available')
        except Exception as e:
            print(f"Error while retrieving journal for PMID {pmid}: {e}")

        try:
            authors = ", ".join(article.authors) if article.authors else "No authors listed"
        except Exception as e:
            print(f"Error while retrieving authors for PMID {pmid}: {e}")

        try:
            if article.history["pubmed"]:
                pub_date = article.history['pubmed'].strftime("%d/%m/%Y") if article.history.get('pubmed') else "Not Available"
            elif article.history["entrez"]:
                pub_date = article.history['entrez'].strftime("%d/%m/%Y") if article.history.get('entrez') else "Not Available"
            elif article.history["medline"]:
                pub_date = article.history['medline'].strftime("%d/%m/%Y") if article.history.get('medline') else "Not Available"
            elif article.history["accepted"]:
                pub_date = article.history['accepted'].strftime("%d/%m/%Y") if article.history.get('accepted') else "Not Available"
            elif article.history[""]:
                pub_date = article.history['revised'].strftime("%d/%m/%Y") if article.history.get('revised') else "Not Available"
            elif article.year:
                pub_date  = f"31/12/{article.year}"

        except Exception as e:
            print(f"Error while retrieving publication date for PMID {pmid}: {e}")

        try:
            article_type = getattr(article, 'pubmed_type', 'Article type ')
        except Exception as e:
            print(f"Error while retrieving article type for PMID {pmid}: {e}")

        try:
            doi = article.doi
        except Exception as e:
            print(f"Error while retrieving DOI for PMID {pmid}: {e}")

        try:
            abstract = getattr(article, 'abstract', 'No abstract available')
        except Exception as e:
            print(f"Error while retrieving abstract for PMID {pmid}: {e}")

        # Construct article data dictionary
        article_data = {
            'Article ID': article_id.replace(",", ""),
            'Title': title,
            'Journal': journal,
            'Authors': authors,
            'Publication Date': pub_date,
            'Article Type': article_type,
            'DOI': doi,
            'Abstract': abstract,
            }
        return article_data

    except Exception as e:
        print(f"Error while fetching article data for PMID {pmid}: {e}")
        return {}

@tool("pubMedArticleSearch")
def pubMedArticleSearch(keywords: str, startDate : str, endDate : str ) -> str:
    """
    Executes a PubMed article search using provided keywords with in the specified date range. 
    Keywords should be provided as a pipe (|) separated string, representing each keyword or phrase.
    startDate and endDate should be given in the dd/mm/yyyy format.
    For example, 'cancer treatment|genome|mutation', 01/01/2019, 01/01/2024 will search articles related to 'cancer treatment', 'genome', and 'mutation' from the last 5 years.
    The function compiles results into a string that represents a DataFrame of search results, including details like article ID, title, journal, authors, publication date, and more.
    """
    try:
        # Convert keywords string to list if necessary
        keywords_list = keywords.split("|") if isinstance(keywords, str) else keywords
        start_datetime = datetime.strptime(startDate, "%d/%m/%Y")
        end_datetime = datetime.strptime(endDate, "%d/%m/%Y")

        # Set your Entrez email here
        PubMedFetcher.email = "alexis.culpin@cri-paris.org"
        PubMedFetcher.API_KEY=os.getenv("NCBI_API_KEY")
        if os.path.isdir("cachedir"):
            shutil.rmtree("cachedir")
        fetcher = PubMedFetcher(cachedir='./cachedir')
        all_articles = []
        nb_article_per_keywords = 5
        nb_article_pear_year = math.ceil((end_datetime.year - start_datetime.year) / nb_article_per_keywords)
        if nb_article_pear_year  <= 0 : nb_article_pear_year  = nb_article_per_keywords

        # allIds = []
        t1 = time.time()
        # search_results  = []
        for kw in keywords_list:
                search_results = fetch_article_ids(kw, start_datetime.year, end_datetime.year, nb_article_pear_year)
                # for year in range(start_datetime.year, end_datetime.year + 1):
                    # search_results.extend(fetcher.pmids_for_query(kw, retmax=nb_article_pear_year , since=f"{year}/01/01", until=f"{year}/12/31"))
                    # if len(search_results) < MAX_CALLS_PER_SECOND : continue
                # search_results = fetcher.pmids_for_query(kw, retmax=nb_article_per_keywords, since=datetime.strptime(startDate, "%d/%m/%Y").strftime("%Y/%m/%d"), until=datetime.strptime(endDate, "%d/%m/%Y").strftime("%Y/%m/%d"))
                try:
                    with ThreadPoolExecutor() as executor:
                        futures = [executor.submit(fetch_article_data, pmid) for pmid in search_results]
                        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching articles"):
                            try:
                                article_data = future.result()
                                if article_data:
                                    pub_date = article_data.get("Publication Date")
                                    if pub_date != "Not Available":
                                        article_pub_date = datetime.strptime(pub_date, "%d/%m/%Y")
                                        if start_datetime <= article_pub_date <= end_datetime:
                                            all_articles.append(article_data)
                            except Exception as data_error:
                                print(f"Error processing data for PMID: {data_error}")
                except Exception as exc:
                    print(f"Error fetching data for keyword '{kw}': {exc}")
    
        print("the all process took : ", time.time() - t1)
        df = pd.DataFrame(all_articles)
        if not df.empty:
            if not os.path.isdir("searchResults/") : os.mkdir("searchResults/")
            df.drop_duplicates(inplace=True)
            fileName = f"pubmedResults_{keywords_list[0].replace(' ', '-')}"
            if fileName in os.listdir("searchResults/"):
                for i in range(1000):
                    nFileName= fileName + f"_{i}"
                    if not nFileName in os.listdir("searchResults/"):
                        fileName = nFileName
                        break


            df.to_csv(f"searchResults/{fileName }.csv", sep=",", index=False)
            print(  pd.to_datetime(df["Publication Date"]).dt.year.value_counts().to_dict())

            return fileName
        else:
            return "No articles found for the given keywords."
    except Exception as e:
        return f"An error occurred: {e}"
    

# class PubMedArticleSearchTool(BaseTool):
#     name: str = "PubMed Article Search"
#     description: str = """
#         Executes a PubMed article search using provided keywords with in the specified date range. 
#         Keywords should be provided as a pipe (|) separated string, representing each keyword or phrase.
#         startDate and endDate should be given in the dd/mm/yyyy format.
#         For example, 'cancer treatment|genome|mutation', 01/01/2019, 01/01/2024 will search articles related to 'cancer treatment', 'genome', and 'mutation' from the last 5 years.
#         The function compiles results into a string that represents a DataFrame of search results, including details like article ID, title, journal, authors, publication date, and more.
#             """
#     return_direct : bool = True
#     # def __init__(self):
#         # super().__init__()
#         # print(dir(self))
#         # self.return_direct = True


#     def _run(self, keywords: str, startDate : str, endDate : str) -> str:
#         """
#         Executes a PubMed article search using provided keywords with in the specified date range. 
#         Keywords should be provided as a pipe (|) separated string, representing each keyword or phrase.
#         startDate and endDate should be given in the dd/mm/yyyy format.
#         For example, 'cancer treatment|genome|mutation', 01/01/2019, 01/01/2024 will search articles related to 'cancer treatment', 'genome', and 'mutation' from the last 5 years.
#         The function compiles results into a string that represents a DataFrame of search results, including details like article ID, title, journal, authors, publication date, and more.
#         """
#         return runPubMedArticleSearch(keywords, startDate, endDate)