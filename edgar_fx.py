# functions to process edgar filings
from bs4 import BeautifulSoup, Comment
import requests
import pandas as pd
import time
import json
import os
email = os.getenv('EMAIL')

# Define the is_comment function outside to ensure it's available when referenced
def remove_uuencoded_data(html_content):
    # Pattern to match uuencoded blocks, somewhat simplistic
    uuencoded_pattern = re.compile(r'begin \d+ .+?\n(?:[!-M].*?\n)+\n?end', re.DOTALL)
    cleaned_content = re.sub(uuencoded_pattern, '', html_content)
    return cleaned_content

def is_comment(element):
    return isinstance(element, Comment)

def edgar_html_preserve_tables(html_content):
    """
    Cleans HTML content by removing scripts, styles, comments, and unnecessary attributes from all tags,
    while aiming to preserve the basic structure of tables. Specifically removes styles from table elements.
    
    Parameters:
    - html_content (str): The original HTML content as a string.
    
    Returns:
    - str: The cleaned HTML content as a string.
    """
    # First, remove any uuencoded data from the HTML content
    cleaned_content = remove_uuencoded_data(html_content)
    
    soup = BeautifulSoup(cleaned_content, 'html.parser')

    # Remove script, style tags, and comments
    comments = soup.find_all(string=is_comment)
    for comment in comments:
        comment.extract()

    # Aggressively remove all attributes from table-related tags and
    # clear 'style' attributes to remove embedded CSS
    for tag in soup.find_all(True):  # True finds all tags
        if tag.name in ['table', 'tr', 'th', 'td']:
            tag.attrs = {}  # Remove all attributes for table-related tags
        else:
            tag.attrs.clear()  # Clear all attributes from other tags, including 'a' and 'font'
            if tag.name in ['a', 'font']:
                tag.unwrap()  # Optionally unwrap 'a' and 'font' tags, if preserving their text content is desired

    return str(soup)



def edgar_fetch_company_info(cik):
    """
    Fetches company information for a given CIK.

    Args:
    - cik (str): The Central Index Key (CIK) of the company.

    Returns:
    - dict: Company information and additional details needed to fetch the 424B4 document.
    """
    allf_url = 'https://data.sec.gov/submissions/CIK{}.json'
    thiscik_url = allf_url.format(cik)
    headers = {'User-Agent':email}
    
    thiscik_request = requests.get(thiscik_url, headers=headers)
    time.sleep(1)  # Respect the SEC's "Fair Access" rule

    try:
        thiscik_contents = thiscik_request.json()
    except json.decoder.JSONDecodeError:
        time.sleep(1)  # Try again after a delay
        thiscik_request = requests.get(thiscik_url, headers=headers)
        thiscik_contents = thiscik_request.json()

    return thiscik_contents


def edgar_fetch_424b4(cik, thiscik_contents):
    """
    Fetches the content of the most recent 424B4 document for a given company using its CIK.

    Args:
    - cik (str): The Central Index Key (CIK) of the company.
    - thiscik_contents (dict): The company information dictionary.

    Returns:
    - str: The text content of the fetched 424B4 document.
    """
    thisf_url = 'https://www.sec.gov/Archives/edgar/data/{0}/{1}.txt'
    headers = {'User-Agent': email}

    # Create a DataFrame from recent filings
    allf = thiscik_contents['filings']['recent']
    allfdf = pd.DataFrame(allf)

    # Find the latest 424B4 document
    id_424B4 = allfdf[allfdf['form'] == '424B4'].index.max()
    acc_num = allfdf.loc[id_424B4, ['accessionNumber']].item()
    filing_date = allfdf.loc[id_424B4, 'filingDate']

    # Generate the URL for the 424B4 filing
    doc_url = thisf_url.format(cik, acc_num)

    # Fetch and return the content of the 424B4 document
    f424B4_request = requests.get(doc_url, headers=headers)
    time.sleep(1)  # Respect the SEC's "Fair Access" rule

    return f424B4_request.text, filing_date

def edgar_fetch_424other(cik, form, thiscik_contents):
    """
    Fetches the content of the most recent 424B4 document for a given company using its CIK.

    Args:
    - cik (str): The Central Index Key (CIK) of the company.
    - thiscik_contents (dict): The company information dictionary.

    Returns:
    - str: The text content of the fetched 424B4 document.
    """
    thisf_url = 'https://www.sec.gov/Archives/edgar/data/{0}/{1}.txt'
    headers = {'User-Agent': email}

    # Create a DataFrame from recent filings
    allf = thiscik_contents['filings']['recent']
    allfdf = pd.DataFrame(allf)

    # Find the latest 424B4 document
    id_424B4 = allfdf[allfdf['form'] == form].index.max()
    acc_num = allfdf.loc[id_424B4, ['accessionNumber']].item()
    filing_date = allfdf.loc[id_424B4, 'filingDate']

    # Generate the URL for the 424B4 filing
    doc_url = thisf_url.format(cik, acc_num)

    # Fetch and return the content of the 424B4 document
    f424B4_request = requests.get(doc_url, headers=headers)
    time.sleep(1)  # Respect the SEC's "Fair Access" rule

    return f424B4_request.text, filing_date

def edgar_fetch_424b4_or_s1(cik, thiscik_contents):
    """
    Fetches the content of the most recent 424B4 document, or the earliest S-1 document if 424B4 is not available,
    for a given company using its CIK.

    Args:
    - cik (str): The Central Index Key (CIK) of the company.
    - thiscik_contents (dict): The company information dictionary.

    Returns:
    - str: The text content of the fetched document.
    """
    thisf_url = 'https://www.sec.gov/Archives/edgar/data/{0}/{1}.txt'
    headers = {'User-Agent': email}

    # Create a DataFrame from recent filings
    allf = thiscik_contents['filings']['recent']
    allfdf = pd.DataFrame(allf)

    # Try to find the latest 424B4 document
    id_424B4 = allfdf[allfdf['form'] == '424B4'].index.max()
    
    # Check if 424B4 document exists
    if pd.notna(id_424B4):
        acc_num = allfdf.loc[id_424B4, ['accessionNumber']].item()
        filing_date = allfdf.loc[id_424B4, 'filingDate']

    else:
        # If no 424B4 found, look for the earliest S-1 document
        id_S1 = allfdf[allfdf['form'] == 'S-1'].index.max()
        if pd.notna(id_S1):
            acc_num = allfdf.loc[id_S1, ['accessionNumber']].item()
            filing_date = allfdf.loc[id_S1, 'filingDate']

        else:
            return None, None  # No 424B4 or S-1 document found

    # Generate the URL for the document
    doc_url = thisf_url.format(cik, acc_num)

    # Fetch and return the content of the document
    document_request = requests.get(doc_url, headers=headers)
    time.sleep(1)  # Respect the SEC's "Fair Access" rule

    return document_request.text, filing_date



def analyze_entity_type1(cikinfo):
    """
    Determines the type of entity based on its SIC or former names.

    Args:
    - cikinfo (dict): A dictionary containing information about the entity, including
                      'sicDescription' and 'formerNames'.

    Returns:
    - str: A string indicating the type of entity.
    """
    # List of SIC codes indicating specific types of entities, as strings
    sic_codes = ['6770', '6726', '6799', '6719']

    # Check the SIC code and determine if it's a Blank Check company or other specified types
    sic_code = cikinfo.get('sic', "")
    if sic_code in sic_codes:
        # Special handling for Blank Check companies
        if sic_code == '6770':
            return "Blank Checks"
        else:
            return "Special Financial Entity"
    
    # Check if 'formerNames' is present and not empty
    former_names = cikinfo.get('formerNames', [])
    if former_names:
        return "Entity with Former Names"

    # Default return value if none of the conditions are met
    return "General Entity"

import re

def analyze_entity_type2(text):
    # Define the regex patterns to match variations of the target phrases
    # Patterns account for optional hyphens and plural forms
    patterns = [
        r"blank\s*-?\s*checks?",  # Matches "blank check", "blank-check", "blank checks", etc.
        r"special\s+acquisition\s+companies?",  # Matches "special acquisition company", "special acquisition companies", etc.
    ]
    
    # Combine the patterns into a single pattern with the 'or' operator
    combined_pattern = "|".join(patterns)
    
    # Search for the combined pattern in the text
    if re.search(combined_pattern, text, re.IGNORECASE):
        return True  # Found a match
    else:
        return False  # No match found



