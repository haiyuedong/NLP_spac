# only used to identify spacs in the file nyseipo_wcik.xlsx

#%% load modules & functions
import json
from operator import index
from matplotlib.pyplot import axis
from numpy import column_stack
import numpy as np
import pandas as pd
import requests
import os
import io
import time
import datetime
import re
#import regex
#import unidecode
from difflib import SequenceMatcher
from bs4 import BeautifulSoup, Comment
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

#import functions processing edgar filings
from edgar_fx import edgar_html_preserve_tables, edgar_fetch_company_info, edgar_fetch_424b4, edgar_fetch_424b4_or_s1, analyze_entity_type1,analyze_entity_type2

#%%
nyseipo = pd.read_excel('nyseipo_wcik.xlsx')
def clean_cik(cik):
    # Extract numeric values from the string, assuming CIK is always a number
    match = re.search(r'\d+', cik)
    return match.group(0) if match else None

# Clean the 'cik' column
nyseipo['cik'] = nyseipo['cik'].apply(clean_cik)
#%%
# Initialize the 'no_424b4_or_S1' column to False for all rows
nyseipo['no_424b4_or_S1'] = False

# Create empty lists to store the analysis results
entity_types = []
spac_statuses = []
filing_dates = [] 

# Iterate over each row in the DataFrame
for index, row in nyseipo.iterrows():
    cik = str(row['cik'])  # Ensure CIK is a string
    cikinfo = edgar_fetch_company_info(cik)
    if cikinfo:
        # Analyze entity type
        entity_type = analyze_entity_type1(cikinfo)
        entity_types.append(entity_type)

        f424B4_file, filing_date = edgar_fetch_424b4_or_s1(cik, cikinfo)
        filing_dates.append(filing_date)
        
        # Check if f424B4_file is None, indicating no filing was found
        if f424B4_file is None:
            # Mark the 'no_424b4_or_S1' flag as True for this row
            nyseipo.at[index, 'no_424b4_or_S1'] = True
            # Since no filing was found, set the filing content to a placeholder or leave it
            cleaned_f424B4_file = None  # Or, you could use a placeholder like "No Filing Found"
            spac_statuses.append(False)  # Assuming False as the default SPAC status when no filing is found
        else:
            # If a filing was found, proceed with cleaning and analysis
            cleaned_f424B4_file = edgar_html_preserve_tables(f424B4_file)
            # Determine if the company is a SPAC
            is_spac = analyze_entity_type2(cleaned_f424B4_file[0:2000] if cleaned_f424B4_file else "")
            spac_statuses.append(is_spac)
    else:
        # Append None or appropriate default values if cikinfo is not found
        entity_types.append(None)
        spac_statuses.append(None)
        filing_dates.append(None)

# Add the analysis results as new columns to the DataFrame
nyseipo['Entity Type'] = entity_types
nyseipo['Is SPAC'] = spac_statuses
nyseipo['Filing Date'] = filing_dates



# %%
nyseipo.to_excel('nyseipo_wcik_spacs.xlsx',index=False)
# %%
