# download all spacs' 424b4 filings from edgar and preprocess and save to local.

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
from edgar_fx import edgar_html_preserve_tables, edgar_fetch_company_info, edgar_fetch_424b4, edgar_fetch_424b4_or_s1, analyze_entity_type1,analyze_entity_type2, edgar_fetch_424other


# Load the DataFrame
nyseipo = pd.read_excel('nyseipo_wcik_spacs.xlsx', usecols=range(20), sheet_name='spacs', dtype={'cik': str})

#%%
# Ensure there's a directory to store the files
output_dir = "SPAC424B4_full"
os.makedirs(output_dir, exist_ok=True)
#%% 
for index, row in nyseipo.iterrows():
    cik = str(row['cik']).strip()  # Ensure CIK is a string and remove any surrounding whitespace
    symbol = str(row['Symbol']).strip()  # Get the symbol and remove any surrounding whitespace
    cikinfo = edgar_fetch_company_info(cik)
    
    if cikinfo:
        f424B4_file, _ = edgar_fetch_424b4_or_s1(cik, cikinfo)  # Ignore the filing date
        
        if f424B4_file is not None:
            cleaned_f424B4_file = edgar_html_preserve_tables(f424B4_file)
            
            # Define a file name using the symbol, saving as .txt
            filename = f"{symbol}.txt"
            filepath = os.path.join(output_dir, filename)
            print(filename)

            # Write the cleaned filing to a file
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(cleaned_f424B4_file)


# %% compare date difference between ipo and filing dates

# Step 1: Convert ['MONTH', 'DAY', 'YEAR'] to a single datetime column
nyseipo['DATE'] = pd.to_datetime(nyseipo[['YEAR', 'MONTH', 'DAY']])
# Step 2: Ensure 'Filing Date' is in datetime format
nyseipo['Filing Date'] = pd.to_datetime(nyseipo['Filing Date'])
# Step 3: Calculate the difference
nyseipo['Difference'] = (nyseipo['Filing Date'] - nyseipo['DATE']).dt.days
# Filter the DataFrame for the desired condition
filtered_nyseipo = nyseipo[(nyseipo['Difference'] > 7) | (nyseipo['Difference'] < -7)]

# Display the 'cik' column for these filtered rows
filtered_cik = filtered_nyseipo['cik']
# If you want to see the whole DataFrame with just the 'cik' for these conditions
print(filtered_cik)


# %% The 17 spacs used different form other than 424b4/S-1 as the "final" prospectus. The ones downloaded previously in the loop are their S-1. Add their updated filings..
# Already checked the reason for the large date difference and write notes in nyseipo_wcik_spacs.xlsx
output_dir = "SPAC424B4_full"
os.makedirs(output_dir, exist_ok=True)

# Define the categorized_ciks dictionary
categorized_ciks = {
    '424B2': ['0001835567'],
    '424B3': [
        '0001691936', '0001752474', '0001757932', '0001807707',
        '0001814287', '0001820209', '0001843249', '0001853775',
        '0001841425', '0001851182', '0001903464'
    ],
    '424B5': ['0001723580', '0001854270', '0001896212', '0001907223'],
    '424B8': ['0001842219'],
}

for index, row in filtered_nyseipo.iterrows():
    cik = str(row['cik']).strip()  # Ensure CIK is a string and remove any surrounding whitespace
    symbol = str(row['Symbol']).strip()  # Get the symbol and remove any surrounding whitespace
    cikinfo = edgar_fetch_company_info(cik)
    
    # Determine the form type to use based on the CIK
    form2use = None
    for form_type, ciks in categorized_ciks.items():
        if cik in ciks:
            form2use = form_type
            break
     
    if cikinfo:
        f424B4_file, _ = edgar_fetch_424other(cik, form2use, cikinfo)  # Ignore the filing date
        
        if f424B4_file is not None:
            cleaned_f424B4_file = edgar_html_preserve_tables(f424B4_file)
            
            # Define a file name using the symbol, saving as .txt
            filename = f"{symbol}.txt"
            filepath = os.path.join(output_dir, filename)
            print(filename)

            # Write the cleaned filing to a file
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(cleaned_f424B4_file)




# %%
