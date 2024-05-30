#%%
from bs4 import BeautifulSoup  # Importing BeautifulSoup for HTML parsing
import os
import pandas as pd
import re
from edgar_parse_fx import find_section_heading, find_section_heading2, find_following_section, extract_section_text,extract_toc_section_names,normalize_space_characters,find_next_section,remove_tags,extract_toc_section_names2, extract_toc_section_names3, find_section_heading3, find_section_heading4, clean_section_text, extract_text_between_sections
import json

input_folder_path = 'SPAC424B4_full/'
# dataframe to collect output status
df = pd.DataFrame(columns=['Filename', 'Status', 'Size'])

# this is for risk factors section.
start_section = 'risk factors'
output_folder_path = 'SPAC424BX_RiskFactors/'

os.makedirs(output_folder_path, exist_ok=True)

# %% get toc of the filings
toc_dict = {}  # Step 1: Initialize the dictionary
df = pd.DataFrame(columns=['Filename', 'this section', 'next section'])
for filename in os.listdir(input_folder_path):
    if filename.endswith(".txt"):  # Check for text files
        with open(os.path.join(input_folder_path, filename), "r", encoding='utf-8') as file:
            html_content = file.read()
            
        soup = BeautifulSoup(normalize_space_characters(html_content), 'lxml')
        toc, risk_section_name = extract_toc_section_names3(soup)
        #this_section_name = 'risk factors'
        next_section_name=find_next_section(toc, risk_section_name)

        # Update toc_dict with ToC for this filename
        toc_dict[filename] = toc  # Step 2: Update dictionary

        if next_section_name:
            # Add to DataFrame
            new_row = pd.DataFrame({'Filename': [filename], 'this section': [risk_section_name], 'next section': [next_section_name]})
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            new_row = pd.DataFrame({'Filename': [filename], 'this section': [risk_section_name], 'next section': ['not found']})
            df = pd.concat([df, new_row], ignore_index=True)

# After the loop, write toc_dict to a JSON file
with open('SPAC424BX_toc.json', 'w') as json_file:  # Step 3: Write the JSON file
    json.dump(toc_dict, json_file)

df.to_excel('SPAC424BX_RiskFactors.xlsx', index=False)

#%% extract section text data
for filename in os.listdir(input_folder_path):
    if filename.endswith(".txt"):  # Check for text files
        with open(os.path.join(input_folder_path, filename), "r", encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(normalize_space_characters(html_content), 'lxml')

        toc, risk_section_name = extract_toc_section_names3(soup)
        #this_section_name = 'risk factors'
        next_section_name=find_next_section(toc, risk_section_name)
        
        # use section names in toc to define section range
        start_element = find_section_heading4(soup, risk_section_name)
        end_element = find_section_heading4(soup, next_section_name) 

        section_text = extract_text_between_sections(soup, start_element, end_element)
        
        #text_size = len(section_text.encode('utf-8'))

        if section_text.strip():
            with open(os.path.join(output_folder_path, filename), "w", encoding='utf-8') as output_file:
                output_file.write(section_text)

# %%query the json toc: 

# Load the filings from the JSON file
with open('SPAC424BX_RiskFactors_toc.json', 'r') as file:
    filings = json.load(file)

# Keyword to search for in the ToC sections
search_keyword = "risk"

# Search for ToC sections containing the keyword and keep track of which filing they belong to
sections_with_risk = {}
for filing, toc in filings.items():
    matching_sections = [section for section in toc if search_keyword.lower() in section.lower()]
    if matching_sections:
        sections_with_risk[filing] = matching_sections

# Display the results
for filing, sections in sections_with_risk.items():
    print(f"{filing} has the following sections containing '{search_keyword}':")
    for section in sections:
        print(f" - {section}")

#%% example part
# APCAU.txt GGPIU.txt SNPRU.txt TBMCU.txt 
# ??? IMPXU.txt MRACU.txt
# RAMMU.txt: seems to messed up with sections in toc, has a few sections discussing risks
# ??? LMACU.txt
with open("SPAC424B4_full/SNPRU.txt", "r") as file:
  html_content = file.read()

soup = BeautifulSoup(normalize_space_characters(html_content), 'lxml')
remove_tags(soup)

toc, risk_section_name = extract_toc_section_names3(soup)
next_section_name=find_next_section(toc, risk_section_name)

print(risk_section_name, next_section_name)

print(find_section_heading4(soup,risk_section_name))
print(find_section_heading4(soup,next_section_name))

start_element = find_section_heading4(soup, risk_section_name)
end_element = find_section_heading4(soup, next_section_name) 

texts = []
for element in start_element.next_elements:
    if element == end_element:
        break  # Stop capturing when end_element is reached
    if isinstance(element, str):  # Check if the element is a NavigableString (text)
        texts.append(element.strip())
    # Note: This loop will capture text of elements between start_element and end_element,
    # but it will exclude the text directly within end_element.

combined_text = " ".join(texts)
section_text = clean_section_text(combined_text)

print(section_text[-100:-1])