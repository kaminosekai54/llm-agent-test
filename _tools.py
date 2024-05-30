from crewai_tools import tool
from datetime import datetime
import itertools
import xmltodict
import pandas as pd
import os
from Bio import Entrez
from dotenv import load_dotenv

load_dotenv()

def generate_keyword_combinations(keywords):
    """Generate all possible combinations of keywords."""
    combinations = []
    for L in range(1, len(keywords) + 1):
        for subset in itertools.combinations(keywords, L):
            combinations.append(", ".join(subset))

    print(combinations)
    return combinations


def extract_article_data(article):
    """Extract required data from a single article, including publication date, authors, type, open access status, and full text availability, with comprehensive checks for missing data."""
    def extract_article_data(article):
        """Extract required data from a single article by searching through multiple potential sources for each data field."""
    data = {
        'Article ID': "Not Available",
        'Title': "Not Available",
        'Journal': "Not Available",
        'Authors': "Not Available",
        'Publication Date': "Not Available",
        'Article Type': "Not Available",
        'DOI': "Not Available",
        'Abstract': "Not Available",
        'Open Access': "No",
        'Full Text Available': "No"
    }

    try:
        article_id_dict = article['MedlineCitation'].get('PMID', {})
        article_id = article_id_dict.get('#text', "Not Available") if isinstance(article_id_dict, dict) else str(article_id_dict)
        data['Article ID'] = article_id 
    except Exception as e:
        print(f"Error extracting Article ID: {e}")
        print(dict(article))
        print(article['MedlineCitation'])
        return

    try:
        raw_title = article.get('MedlineCitation', {}).get('Article', {}).get('ArticleTitle')
        if isinstance(raw_title, dict):
            title_parts = [raw_title.get('#text', '')] + [part for key, part in raw_title.items() if isinstance(part, list) for part in part]
            data['Title'] = " ".join(title_parts).strip()
        elif isinstance(raw_title, str):
            data['Title'] = raw_title
    except Exception as e:
        print(f"Error extracting Title: {e}")

    try:
        journal_info = article.get('MedlineCitation', {}).get('Article', {}).get('Journal', {})
        data['Journal'] = journal_info if isinstance(journal_info, str) else journal_info.get('Title', "Not Available")
    except Exception as e:
        print(f"Error extracting Journal: {e}")

    try:
        publication_date = article.get('MedlineCitation', {}).get('Article', {}).get('ArticleDate', [])
        if publication_date and isinstance(publication_date, list) and publication_date:
            date_info = publication_date[0]
            data['Publication Date'] = f"{date_info.get('Year', 'YYYY')}-{date_info.get('Month', 'MM')}-{date_info.get('Day', 'DD')}"
    except Exception as e:
        print(f"Error extracting Publication Date: {e}")

    try:
        publication_type_list = article.get('MedlineCitation', {}).get('Article', {}).get('PublicationTypeList', {}).get('PublicationType', [])
        if publication_type_list and isinstance(publication_type_list, list):
            data['Article Type'] = ", ".join(ptype.get('#text', "Unknown Type") for ptype in publication_type_list if isinstance(ptype, dict))
    except Exception as e:
        print(f"Error extracting Article Type: {e}")

    try:
        article_ids = article.get('PubmedData', {}).get('ArticleIdList', {}).get('ArticleId', [])
        data['DOI'] = next((aid.get('#text', "Not Available") for aid in article_ids if isinstance(aid, dict) and aid.get('@IdType') == 'doi'), "Not Available")
    except Exception as e:
        print(f"Error extracting DOI: {e}")

    try:
        abstract_texts = article.get('MedlineCitation', {}).get('Article', {}).get('Abstract', {}).get('AbstractText', [])
        if abstract_texts and isinstance(abstract_texts, list):
            data['Abstract'] = " ".join(part.get('#text', part) if isinstance(part, dict) else part for part in abstract_texts)
    except Exception as e:
        print(f"Error extracting Abstract: {e}")

    try:
        author_list = article.get('MedlineCitation', {}).get('Article', {}).get('AuthorList', {}).get('Author', [])
        if author_list and isinstance(author_list, list):
            authors = []
            for author in author_list:
                if isinstance(author, dict):
                    last_name = author.get('LastName', "")
                    fore_name = author.get('ForeName', "")
                    authors.append(f"{fore_name} {last_name}".strip())
            data['Authors'] = ", ".join(authors)
    except Exception as e:
        print(f"Error extracting Authors: {e}")

    try:
        if not article_ids:  # Re-fetch if not fetched earlier
            article_ids = article.get('PubmedData', {}).get('ArticleIdList', {}).get('ArticleId', [])
        pmc_id = next((aid.get('#text', None) for aid in article_ids if isinstance(aid, dict) and aid.get('@IdType') == 'pmc'), None)
        data['Open Access'] = "Yes" if pmc_id else "No"
        data['Full Text Available'] = "Yes" if pmc_id else "No"
    except Exception as e:
        print(f"Error extracting Open Access and Full Text Availability: {e}")

    return data

# Use this function with an article dictionary to extract data
# example_article = {'MedlineCitation': {...}, 'PubmedData': {...}}
# result = extract_article_data(example_article)
# print(result)
    data = {
        'Article ID': "Not Available",
        'Title': "Not Available",
        'Journal': "Not Available",
        'Authors': "Not Available",
        'Publication Date': "Not Available",
        'Article Type': "Not Available",
        'DOI': "Not Available",
        'Abstract': "Not Available",
        'Open Access': "No",
        'Full Text Available': "No"
    }

    try:
        article_id_dict = article['MedlineCitation'].get('PMID', {})
        data["Article ID"] = article_id_dict.get('#text', "Not Available") if isinstance(article_id_dict, dict) else str(article_id_dict)
    except Exception as e:
        print(f"Error extracting Article ID: {e}")

                # Handling title that might be a dictionary
    try: 
        raw_title = article.get('MedlineCitation', {}).get('Article', {}).get('ArticleTitle', "Not Available")
        if isinstance(raw_title, dict):
            # Assuming '#text' exists and optionally there are other parts marked with keys like 'i'
            title_parts = [raw_title.get('#text')] + [part for key, part in raw_title.items() if key != '#text' for part in (part if isinstance(part, list) else [part])]
            data["Title"] = " ".join(title_parts).strip()
        else:
            data["Title"] = raw_title
    except Exception as e:
        print(f"Error extracting Title: {e}")

    try:
        data['Journal'] =article.get('MedlineCitation', {}).get('Article', {}).get('Journal', {}).get('Title', "Not Available")
        data['Journal'] = journal_info if isinstance(journal_info, str) else journal_info.get('Title', "Not Available")
    except Exception as e:
        print(f"Error extracting Journal: {e}")

    try:
        # Improved handling for publication date extraction
        article_date = article['MedlineCitation']['Article'].get('ArticleDate')
        if article_date and isinstance(article_date, list) and len(article_date) > 0:
            data['Publication Date'] = f"{article_date[0].get('Year', 'YYYY')}-{article_date[0].get('Month', 'MM')}-{article_date[0].get('Day', 'DD')}"
        else:
            journal_issue_date = article['MedlineCitation']['Article']['Journal'].get('JournalIssue', {}).get('PubDate', {})
            if 'Year' in journal_issue_date:
                data['Publication Date'] = f"{journal_issue_date.get('Year', 'YYYY')}-{journal_issue_date.get('Month', 'MM')}-{journal_issue_date.get('Day', 'DD')}"
    except Exception as e:
        print(f"Error extracting Publication Date: {e}")

    try:
        publication_type_list = article['MedlineCitation']['Article'].get('PublicationTypeList', {}).get('PublicationType', [])
        data["Article Type"]= ", ".join(ptype['#text'] for ptype in publication_type_list if isinstance(ptype, dict))
    except Exception as e:
        print(f"Error extracting Article Type: {e}")

    try:
        article_ids = article['PubmedData']['ArticleIdList'].get('ArticleId', [])
        data["DOI"] = next((aid['#text'] for aid in article_ids if isinstance(aid, dict) and aid.get('@IdType') == 'doi'), "Not Available")
    except Exception as e:
        print(f"Error extracting DOI: {e}")

    try:
        abstract_texts = article['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', [])
        if isinstance(abstract_texts, list):
            data['Abstract'] = " ".join(part['#text'] if isinstance(part, dict) else part for part in abstract_texts)
        elif isinstance(abstract_texts, dict):
            data['Abstract']= abstract_texts.get('#text', abstract_texts)
    except Exception as e:
        print(f"Error extracting Abstract: {e}")

        # Extracting authors
    try:
        author_list = article['MedlineCitation']['Article'].get('AuthorList', {}).get('Author', [])
        authors = []
        for author in author_list:
            if isinstance(author, dict):
                authors.append(f"{author.get('ForeName', '')} {author.get('LastName', '')}".strip())
        data['Authors'] = ", ".join(authors)
    except Exception as e:
        print(f"Error extracting Authors: {e}")

        # Open access and full-text availability
    try:
        pmc_id = next((aid['#text'] for aid in article_ids if isinstance(aid, dict) and aid.get('@IdType') == 'pmc'), None)
        data['Open Access'] = "Yes" if pmc_id else "No"
        data['Full Text Available'] = "Yes" if pmc_id else "No"
    except Exception as e:
        print(f"Error extracting Open Access and Full Text Availability: {e}")

    return data
    

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
    Entrez.email = "your_email@example.com"
    start_date = (datetime.now() - pd.DateOffset(years=5)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
        
    all_articles = []
    for kw in keywords_list:
        query = f"({kw})"
        handle = Entrez.esearch(db="pubmed", term=query, retmax=5)
        record = Entrez.read(handle)
        id_list = record["IdList"]
            
        if id_list:
            handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
            articles_xml = handle.read()
            articles_dict = xmltodict.parse(articles_xml)
            articles = articles_dict.get('PubmedArticleSet', {}).get('PubmedArticle', [])
            print(articles )
            for article in articles:
                print(article)
                article_data = extract_article_data(article)
                all_articles.append(article_data)

    df = pd.DataFrame(all_articles)
    if not df.empty: 
        df.drop_duplicates(inplace=True)
        json_data = df.to_json(orient='records')
        df.to_csv("./pubMedResults.csv", sep=",", index=False)
        return json_data
    else:
        return "No articles found for the given keywords."




# results = pubMedArticleSearch("titanium femur implant, orthopedic titanium rod, femoral prosthesis, biocompatible femur replacement, custom femur implant")
# print(results)