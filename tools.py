from metapub import PubMedFetcher
import pandas as pd
from datetime import datetime
from crewai_tools import tool
import os, shutil
from dotenv import load_dotenv
from tqdm import tqdm  # Import tqdm for progress bar functionality

load_dotenv()
os.environ["NCBI_API_KEY"] = "6361fb3062c6904a3bdda0295e65998f0408"

@tool("pubMedArticleSearch")
def pubMedArticleSearch(keywords: str) -> str:
    """
    Executes a PubMed article search using provided keywords. Keywords should be provided as a pipe (|) separated string, representing each keyword or phrase.
    For example, 'cancer treatment|genome|mutation' will search articles related to 'cancer treatment', 'genome', and 'mutation' from the last 5 years.
    The function compiles results into a string that represents a DataFrame of search results, including details like article ID, title, journal, authors, publication date, and more.
    """
    # Convert keywords string to list if necessary
    keywords_list = keywords.split("|") if isinstance(keywords, str) else keywords
    
    # Set your Entrez email here
    PubMedFetcher.email = "alexis.culpin@cri-paris.org"
    start_date = (datetime.now() - pd.DateOffset(years=5)).strftime("%Y/%m/%d")
    end_date = datetime.now().strftime("%Y/%m/%d")
    if os.path.isdir("cachedir") : shutil.rmtree("cachedir")
    fetcher = PubMedFetcher(cachedir='./cachedir')
    all_articles = []
    nb_article_per_keywords = 5
    for kw in keywords_list:
        try:
            search_results = fetcher.pmids_for_query(kw, retmax=nb_article_per_keywords, mindate=start_date, maxdate=end_date)
            for pmid in tqdm(search_results, desc="Fetching articles"):
                try:
                    article = fetcher.article_by_pmid(pmid)
                    article_data = {
                    'Article ID': article.pmid,
                    'Title': getattr(article, 'title', 'No title available'),
                    'Journal': getattr(article, 'journal', 'No journal available'),
                    'Authors': ", ".join(article.authors) if article.authors else "No authors listed",
                    'Publication Date': article.history['pubmed'].strftime("%Y-%m-%d") if article.history['pubmed'] else "Not Available",
                    'Article Type': getattr(article, 'pubmed_type', 'Article type '),
                    'DOI': getattr(article, 'doi', 'DOI not available'),
                    'Abstract': getattr(article, 'abstract', 'No abstract available'),
                }
                    all_articles.append(article_data)
                except Exception as e:
                    print(f"General error during query for keyword '{kw}': {e}")
    
        except Exception as e:
            print(f"General error during query for keyword '{kw}': {e}")
    df = pd.DataFrame(all_articles)
    if not df.empty:
        df.drop_duplicates(inplace=True)
        # json_data = df.to_json(orient='records')
        df.to_csv("./pubMedResults.csv", sep=",", index=False)
        return "csv created"
    else:
        return "No articles found for the given keywords."
    