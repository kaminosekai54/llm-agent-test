from metapub import PubMedFetcher
import pandas as pd
from datetime import datetime
from crewai_tools import tool
import os
import shutil
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
os.environ["NCBI_API_KEY"] = "6361fb3062c6904a3bdda0295e65998f0408"

@tool("pubMedArticleSearch")
def pubMedArticleSearch(keywords: str) -> str:
    """
    Executes a PubMed article search using provided keywords. Keywords should be provided as a pipe (|) separated string, representing each keyword or phrase.
    For example, 'cancer treatment|genome|mutation' will search articles related to 'cancer treatment', 'genome', and 'mutation' from the last 5 years.
    The function compiles results into a string that represents a DataFrame of search results, including details like article ID, title, journal, authors, publication date, and more.
    """
    try:
        # Convert keywords string to list if necessary
        keywords_list = keywords.split("|") if isinstance(keywords, str) else keywords

        # Set your Entrez email here
        PubMedFetcher.email = "alexis.culpin@cri-paris.org"
        start_date = (datetime.now() - pd.DateOffset(years=5)).strftime("%Y/%m/%d")
        end_date = datetime.now().strftime("%Y/%m/%d")
        if os.path.isdir("cachedir"):
            shutil.rmtree("cachedir")
        fetcher = PubMedFetcher(cachedir='./cachedir')
        all_articles = []
        nb_article_per_keywords = 5
        for kw in keywords_list:
            try:
                search_results = fetcher.pmids_for_query(kw, retmax=nb_article_per_keywords, mindate=start_date, maxdate=end_date)
                for pmid in tqdm(search_results, desc="Fetching articles"):
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
                            pub_date = article.history['pubmed'].strftime("%Y-%m-%d") if article.history.get('pubmed') else "Not Available"
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
                            'Article ID': article_id,
                            'Title': title,
                            'Journal': journal,
                            'Authors': authors,
                            'Publication Date': pub_date,
                            'Article Type': article_type,
                            'DOI': doi,
                            'Abstract': abstract,
                        }
                        all_articles.append(article_data)
                    except Exception as e:
                        print(f"Error while fetching article data for PMID {pmid}: {e}")
            except Exception as e:
                print(f"Error while querying PubMed for keyword '{kw}': {e}")

        df = pd.DataFrame(all_articles)
        if not df.empty:
            df.drop_duplicates(inplace=True)
            df.to_csv("./pubMedResults.csv", sep=",", index=False)
            return "CSV created"
        else:
            return "No articles found for the given keywords."
    except Exception as e:
        return f"An error occurred: {e}"