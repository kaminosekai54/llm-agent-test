# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from crewai_tools import BaseTool
from Bio import Entrez
import itertools
import xmltodict
import pandas as pd
import os

class PubMedArticleSearchTool(BaseTool):
    name: str = "PubMed Article Search"
    description: str = "Searches PubMed for articles matching given keywords"

    def _run(self, keywords: str) -> str:
        """
    Executes a PubMed article search using provided keywords. Keywords should be provided as a pipe (|) separated string, representing each keyword or phrase.
    
    For example, 'cancer treatment|genome|mutation' will search articles related to 'cancer treatment', 'genome', and 'mutation' from the last 5 years.
    
    The function compiles results into a string that represents a DataFrame of search results, including details like article ID, title, journal, authors, publication date, and more.
    """
        keywords_list = keywords
        if isinstance(keywords, str) : keywords_list = keywords.split("|")
        Entrez.email = "Alexis.CULPIN@efor-group.com"  # Set your email

        def generate_keyword_combinations(keywords):
                combinations = []
                # No need to split the keywords string, as we now assume 'keywords' is already a list of keyword strings
                for L in range(1, len(keywords) + 1):
                    for subset in itertools.combinations(keywords, L):
                        combinations.append(", ".join(subset))  # Joining with ', ' for clarity, but you can adjust as needed
                return combinations


        def search_pubmed(keywords):
            current_date = datetime.now()
            date_minus_5_years = current_date.replace(year=current_date.year - 5).strftime("%Y-%m-%d")
            current_date = datetime.now().strftime("%Y-%m-%d")

            all_articles = []
            # combinations = generate_keyword_combinations(keywords)
            # print(combinations )
            # for combo in combinations:
            for kw in keywords:
                query = f"({kw})" 
                handle = Entrez.esearch(db="pubmed", term=query, retmax=5)
                record = Entrez.read(handle)
                id_list = record["IdList"]

                if id_list:
                    handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
                    articles_xml = handle.read()
                    articles_dict = xmltodict.parse(articles_xml)
                    articles = articles_dict['PubmedArticleSet']['PubmedArticle']
                    # print(articles)
                    for article in articles:
                        article_data = extract_article_data(article)
                        if article_data:
                            all_articles.append(article_data)

            return all_articles
        
        # Implement the `extract_article_data` function as previously described
        def extract_article_data(article):
            """Extract required data from a single article, including publication date, authors, type, open access status, and full text availability, with comprehensive checks for missing data."""
            try:
                # Correcting the extraction of the article ID
                article_id_dict = article['MedlineCitation'].get('PMID', {})
                article_id = article_id_dict.get('#text', "Not Available") if isinstance(article_id_dict, dict) else str(article_id_dict)

                # Handling title that might be a dictionary
                raw_title = article.get('MedlineCitation', {}).get('Article', {}).get('ArticleTitle', "Not Available")
                if isinstance(raw_title, dict):
                    # Assuming '#text' exists and optionally there are other parts marked with keys like 'i'
                    title_parts = [raw_title.get('#text')] + [part for key, part in raw_title.items() if key != '#text' for part in (part if isinstance(part, list) else [part])]
                    title = " ".join(title_parts).strip()
                else:
                    title = raw_title
                journal = article.get('MedlineCitation', {}).get('Article', {}).get('Journal', {}).get('Title', "Not Available")
                
                # Improved handling for publication date extraction
                article_date = article['MedlineCitation']['Article'].get('ArticleDate')
                pub_date = "Not Available"
                if article_date and isinstance(article_date, list) and len(article_date) > 0:
                    year = article_date[0].get('Year', '')
                    month = article_date[0].get('Month', '01')
                    day = article_date[0].get('Day', '01')
                    pub_date = f"{year}-{month}-{day}"
                else:
                    journal_issue_date = article['MedlineCitation']['Article']['Journal'].get('JournalIssue', {}).get('PubDate', {})
                    if 'Year' in journal_issue_date:
                        year = journal_issue_date.get('Year', '')
                        month = journal_issue_date.get('Month', '01')
                        day = journal_issue_date.get('Day', '01')
                        pub_date = f"{year}-{month}-{day}"

                publication_type_list = article['MedlineCitation']['Article'].get('PublicationTypeList', {}).get('PublicationType', [])
                publication_type = ", ".join(ptype['#text'] for ptype in publication_type_list if isinstance(ptype, dict))

                # Handling for DOI and abstract
                article_ids = article['PubmedData']['ArticleIdList'].get('ArticleId', [])
                doi = next((aid['#text'] for aid in article_ids if isinstance(aid, dict) and aid.get('@IdType') == 'doi'), "Not Available")

                abstract_texts = article['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', [])
                abstract = "Not Available"
                if isinstance(abstract_texts, list):
                    abstract = " ".join(part['#text'] if isinstance(part, dict) else part for part in abstract_texts)
                elif isinstance(abstract_texts, dict):
                    abstract = abstract_texts.get('#text', abstract_texts)

                # Extracting authors
                author_list = article['MedlineCitation']['Article'].get('AuthorList', {}).get('Author', [])
                authors = []
                for author in author_list:
                    if isinstance(author, dict):
                        last_name = author.get('LastName', "")
                        fore_name = author.get('ForeName', "")
                        authors.append(f"{fore_name} {last_name}".strip())

                # Open access and full-text availability
                pmc_id = next((aid['#text'] for aid in article_ids if isinstance(aid, dict) and aid.get('@IdType') == 'pmc'), None)
                open_access_status = "Yes" if pmc_id else "No"

                return {
                    'Article ID': article_id.encode('utf8', 'replace'),
                    'Title': title.encode('utf8', 'replace'),
                    'Journal': journal.encode('utf8', 'replace'),
                    'Authors': ", ".join(authors).encode('utf8', 'replace'),
                    'Publication Date': pub_date.encode('utf8', 'replace'),
                    'Article Type': publication_type.encode('utf8', 'replace'),
                    'DOI': doi.encode('utf8', 'replace'),
                    'Abstract': abstract.encode('utf8', 'replace'),
                    'Open Access': open_access_status.encode('utf8', 'replace'),
                    'Full Text Available': "Yes" if pmc_id else "No"
                }
            except Exception as e:
                print(f"Error extracting article data: {e}")
                return None


        articles = search_pubmed(keywords_list)
        df = pd.DataFrame.from_dict(articles).drop_duplicates()
        json_data = df.to_json()

        if not df.empty :
            df = df.applymap(lambda x: x.decode('utf-8', 'replace') if isinstance(x, bytes) else x)
            df.to_csv("./pubMedResults.csv", sep=",", index=False, encoding="utf8")
        return json_data

# results = PubMedArticleSearchTool().run("titanium femur implant, orthopedic titanium rod, femoral prosthesis, biocompatible femur replacement, custom femur implant")

