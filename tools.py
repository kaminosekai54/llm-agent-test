from metapub import PubMedFetcher
import pandas as pd
from datetime import datetime
from crewai_tools import tool
import os
import shutil
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from cachetools import cached, TTLCache
from ratelimit import limits, sleep_and_retry
from time import sleep
from backoff import on_exception, expo
from requests.exceptions import ChunkedEncodingError, ConnectionError

load_dotenv()
# os.environ["NCBI_API_KEY"] = "6361fb3062c6904a3bdda0295e65998f0408"
cache = TTLCache(maxsize=1000, ttl=3600)
MAX_CALLS_PER_SECOND = 3  # Adjust this number based on the API's allowed rate limit
SECONDS = 1

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
            pub_date = article.history['pubmed'].strftime("%d/%m/%Y") if article.history.get('pubmed') else "Not Available"
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

        # Set your Entrez email here
        PubMedFetcher.email = "alexis.culpin@cri-paris.org"
        if os.path.isdir("cachedir"):
            shutil.rmtree("cachedir")
        fetcher = PubMedFetcher(cachedir='./cachedir')
        all_articles = []
        nb_article_per_keywords = 5
        for kw in keywords_list:
                search_results = fetcher.pmids_for_query(kw, retmax=nb_article_per_keywords, since=datetime.strptime(startDate, "%d/%m/%Y").strftime("%Y/%m/%d"), until=datetime.strptime(endDate, "%d/%m/%Y").strftime("%Y/%m/%d"))
                with ThreadPoolExecutor() as executor:
                    futures = [executor.submit(fetch_article_data, pmid) for pmid in search_results]
                    for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching articles"):
                        article_data = future.result()
                        if article_data:
                            all_articles.append(article_data)

        df = pd.DataFrame(all_articles)
        if not df.empty:
            df.drop_duplicates(inplace=True)
            df.to_csv("./pubMedResults.csv", sep=",", index=False)
            return "CSV created"
        else:
            return "No articles found for the given keywords."
    except Exception as e:
        return f"An error occurred: {e}"
