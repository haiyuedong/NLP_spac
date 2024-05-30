import re
from bs4 import BeautifulSoup


def normalize_space_characters(text):
    # Regular expression pattern matches various Unicode space characters
    space_chars_pattern = r'[\u0020\u00A0\u2002\u2003\u2009\u200A\u200B\u200C\u200D\u202F\u205F\u3000]+'
    # Replace matched characters with a standard space
    normalized_text = re.sub(space_chars_pattern, ' ', text)
    return normalized_text

def remove_tags(soup):
    """
    Removes specific formatting tags from a BeautifulSoup object but keeps their contents.

    Parameters:
    - soup: BeautifulSoup object to process.

    The function modifies the soup object in place.
    """
    tags_to_remove = ['b', 'strong', 'i', 'em', 'u', 'small', 'mark', 'sub', 'sup', 'span', 'font']
    # Iterate through each tag in the list and unwrap it
    for tag in tags_to_remove:
        for found_tag in soup.find_all(tag):
            found_tag.unwrap()

def clean_toc(rawtable):
    processed_cells = []
    for cell in rawtable:
        # Remove newline characters
        cleaned_cell = cell.text.replace('\n', ' ')
        # Replace any non-alphabetic characters with a space
        cleaned_cell = re.sub(r'[^a-zA-Z]', ' ', cleaned_cell)
        # Replace multiple spaces with a single space
        cleaned_cell = re.sub(r'\s+', ' ', cleaned_cell).strip()
        if cleaned_cell.lower() !='page' and cleaned_cell.lower():
            processed_cells.append(cleaned_cell.lower())
    return processed_cells

def extract_toc_section_names3(soup):
    # Define the required section names for identification of the ToC
    risk_section = ["risk factors", "risk", "risks"]
    other_section = ["underwriting", "experts", "legal matters"]

    toc_sections = []
    for table in soup.find_all('table'):
        tablelist = clean_toc(table)
        
        # check if toc contains required section
        # Initialize an empty list for matched risk sections
        matched_risk_section = []
        # Check "risk factors" first, then others
        for risk in risk_section:
            if risk in tablelist:
                matched_risk_section.append(risk)
                # If "risk factors" is found, stop looking for more.
                if risk == "risk factors":
                    break        
        matched_other_section = [other for other in other_section if other in tablelist]
        
        if matched_risk_section and matched_other_section:
            toc_sections=tablelist
            risk_section_name = matched_risk_section[0]
            return toc_sections, risk_section_name
        if toc_sections == [] and matched_risk_section:
            toc_sections.extend(tablelist)
            risk_section_name = matched_risk_section[0]
            continue
        if toc_sections != [] and matched_other_section:
            toc_sections.extend(tablelist)
            return toc_sections, risk_section_name
    return []            



def extract_toc_section_names2(soup):
    # Define the required section names for identification of the ToC
    # match either one is ok
    risk_section = ["risk", "risk factors"]
    other_section = ["underwriting", "experts"]
    required_sections = ["risk factors", "underwriting"]
    required_sections2 = ["risk factors", "experts"]

    # Iterate over each table to find one that contains all required section names
    toc_sections = []
    for table in soup.find_all('table'):
        tablelist = clean_toc(table)
        if all(section.lower() in (cell.lower() for cell in tablelist) for section in required_sections) or all(section.lower() in (cell.lower() for cell in tablelist) for section in required_sections2):
            toc_sections=tablelist
            return toc_sections
        if (toc_sections == []) and (all(section.lower() in (cell.lower() for cell in tablelist) for section in required_sections[0:1])):
            toc_sections.extend(tablelist)
            continue
        if (toc_sections != []) and ( (all(section.lower() in (cell.lower() for cell in tablelist) for section in required_sections[1:2])) or (all(section.lower() in (cell.lower() for cell in tablelist) for section in required_sections2[1:2])) ):
            toc_sections.extend(tablelist)
            return toc_sections
    return []






def extract_toc_section_names(soup):

    # Define the required section names for identification of the ToC
    required_sections = ["summary", "risk factors", "underwriting"]

    # Iterate over each table to find one that contains all required section names
    toc_sections = []
    for table in soup.find_all('table'):
        table_text = " ".join(cell.get_text(" ", strip=True).lower() for cell in table.find_all(['td', 'th']))
        
        # Proceed if all required sections are found in the table's text
        if (toc_sections==[]) and (all(section.lower() in table_text for section in required_sections)):

            # Iterate through each row in the found table
            for row in table.find_all('tr'):
                # Concatenate all cell texts in a row, then filter out numeric values
                row_text = " ".join(cell.get_text(" ", strip=True) for cell in row.find_all(['td', 'th']))
                
                # Use regex to remove standalone numeric values (assumed to be page numbers) from the row text
                filtered_text = re.sub(r'\b\d+\b', '', row_text).strip()
                filtered_text = filtered_text.replace('\n', ' ')

                #section_name = clean_text(" ".join(cell.get_text() for cell in filtered_text))
                # Check if the filtered text is not empty and add to the section list
                if filtered_text.lower() != "page" and filtered_text:
                        toc_sections.append(filtered_text)

            return toc_sections
        
        if (toc_sections==[]) and (all(section.lower() in table_text for section in required_sections[0:2])):
            for row in table.find_all('tr'):
                # Concatenate all cell texts in a row, then filter out numeric values
                row_text = " ".join(cell.get_text(" ", strip=True) for cell in row.find_all(['td', 'th']))
                
                # Use regex to remove standalone numeric values (assumed to be page numbers) from the row text
                filtered_text = re.sub(r'\b\d+\b', '', row_text).strip()
                filtered_text = filtered_text.replace('\n', ' ')

                #section_name = clean_text(" ".join(cell.get_text() for cell in filtered_text))
                # Check if the filtered text is not empty and add to the section list
                if filtered_text.lower() != "page" and filtered_text:
                        toc_sections.append(filtered_text)
            continue

        if (toc_sections!=[]) and (all(section.lower() in table_text for section in required_sections[2:3])):
            for row in table.find_all('tr'):
                # Concatenate all cell texts in a row, then filter out numeric values
                row_text = " ".join(cell.get_text(" ", strip=True) for cell in row.find_all(['td', 'th']))
                
                # Use regex to remove standalone numeric values (assumed to be page numbers) from the row text
                filtered_text = re.sub(r'\b\d+\b', '', row_text).strip()
                filtered_text = filtered_text.replace('\n', ' ')

                #section_name = clean_text(" ".join(cell.get_text() for cell in filtered_text))
                # Check if the filtered text is not empty and add to the section list
                if filtered_text.lower() != "page" and filtered_text:
                        toc_sections.append(filtered_text)
            return toc_sections

    # Return an empty list if no matching table is found
    return []


def find_section_heading2(soup, this_section):
    this_section = this_section.lower()
    for element in soup.find_all(['p', 'div']):
        text = element.get_text(strip=True).lower()
        # Check if any ancestor is a table
        in_table = False
        for parent in element.parents:
            if parent.name == 'table':
                in_table = True
                break

        if not in_table:
            # Check if the section heading should start with "cautionary note regarding"
            if this_section.startswith("cautionary note regarding"):
                if text.startswith("cautionary note regarding"):
                    return element
            else:
                if text == this_section:
                    return element


def find_section_heading(soup, this_section):
    this_section = this_section.lower()
    # Compile a regular expression pattern for flexible matching, accounting for variable whitespace
    pattern = re.compile(r'\b{}\b'.format(re.escape(this_section)), re.IGNORECASE | re.DOTALL)
    
    for element in soup.find_all(['p', 'div']):
        text = re.sub(r'\s+', ' ', element.get_text(strip=True).lower()).strip()
        # Check if any ancestor is a table
        in_table = False
        for parent in element.parents:
            if parent.name == 'table':
                in_table = True
                break

        if not in_table:
            # Use the regular expression search instead of exact string match
            if pattern.search(text):
                return element


# find next section name by going into the toc:
def find_next_section(toc, this_section):
    # Convert the input section to lowercase for case-insensitive comparison
    this_section_lower = this_section.lower()
    # Use a lowercase version of the toc for finding the index
    toc_lower = [section.lower() for section in toc]
    try:
        # Find the index of the given section
        index = toc_lower.index(this_section_lower)
        # Check if this is not the last element
        if index + 1 < len(toc_lower):
            # Return the next section
            return toc_lower[index + 1]
        else:
            # If it's the last element, there's no next section
            return None
    except ValueError:
        # If the section is not found in the list
        return None


# the function returns the name of the following section after the input section. this is done by looking at the toc
def find_following_section(soup, this_section):
   found_this_section_in_toc = False
   for tr in soup.find_all('tr'):
        if found_this_section_in_toc:
            for tag in tr.find_all(['p', 'div']):
                text = tag.get_text(strip=True)
                if re.fullmatch(r'[A-Za-z ]+', text):
                    return text
            continue
        if tr.find_all(['p', 'div'], string=lambda text: text and this_section in text.lower()):
            found_this_section_in_toc = True  
            continue


def clean_pdiv(pdiv):
    # Remove newline characters
    cleaned_pdiv = pdiv.replace('\n', ' ')
    # Replace any non-alphabetic characters with a space
    cleaned_pdiv = re.sub(r'[^a-zA-Z]', ' ', cleaned_pdiv)
    # Replace multiple spaces with a single space
    cleaned_pdiv = re.sub(r'\s+', ' ', cleaned_pdiv).strip()

    return cleaned_pdiv

def find_section_heading3(soup, this_section_name):
    this_section_name = this_section_name.lower()
    for element in soup.find_all(['p', 'div']):
        text = element.get_text(strip=True).lower()
        # Check if any ancestor is a table
        in_table = False
        for parent in element.parents:
            if parent.name == 'table':
                in_table = True
                break

        if not in_table:
            cleaned_pdiv=clean_pdiv(text)
            # Check if the section heading should start with "cautionary note regarding"
            if this_section_name.startswith("cautionary note regarding"):
                if cleaned_pdiv.startswith("cautionary note regarding"):
                    return element
            else:
                if cleaned_pdiv == this_section_name:
                    return element


def find_section_heading4(soup, this_section_name):
    this_section_name = this_section_name.lower()
    best_match = None  # Initialize with None to indicate no match found yet

    for element in soup.find_all(['p', 'div']):
        text = element.get_text(strip=True).lower()

        # Check if any ancestor is a table
        in_table = False
        for parent in element.parents:
            if parent.name == 'table':
                in_table = True
                break

        if not in_table:
            cleaned_pdiv = clean_pdiv(text)

            # Check for match based on this_section_name criteria
            is_match = False
            if this_section_name.startswith("cautionary note regarding") and cleaned_pdiv.startswith("cautionary note regarding"):
                is_match = True
            elif cleaned_pdiv == this_section_name:
                is_match = True

            # Update best_match if this element is a better match
            if is_match:
                if best_match is None or len(cleaned_pdiv) < len(clean_pdiv(best_match[1].get_text(strip=True).lower())):
                    best_match = (len(cleaned_pdiv), element)

    # Return the element of the best match, if any
    return best_match[1] if best_match else None



def extract_section_text(soup, start_section, end_section):
    # Find the start and end elements using find_section_heading
    start_element = find_section_heading4(soup, start_section)
    end_element = find_section_heading4(soup, end_section) if end_section else None
    
    if not start_element:
        return "Start section not found."
    
    # Initialize a list to hold all the text from the start to the end section
    texts = []
    
    # Flag to start capturing text
    capture = False
    
    for element in soup.find_all(['p', 'div']):
        # When the start element is reached, begin capturing text
        if element == start_element:
            capture = True
        # If capturing and the end element is reached, stop capturing
        if capture and element == end_element:
            break
        # If we are capturing, add the element's text to the texts list
        if capture:
            texts.append(element.get_text(strip=True))
    
    # Combine all captured texts into a single string
    return " ".join(texts)


def clean_section_text(rawtext):

    # Remove newline characters
    cleaned_rawtext = rawtext.replace('\n', ' ')
    # Replace multiple spaces with a single space
    cleaned_rawtext = re.sub(r'\s+', ' ', cleaned_rawtext).strip()

    return cleaned_rawtext

def extract_text_between_sections(soup, start_element, end_element):
    texts = []  # Initialize a list to hold all the text between the start and end elements

    # Check if start_element is found; if not, return an appropriate message
    if not start_element:
        return "Start section not found."

    for element in start_element.next_elements:
        if element == end_element:
            break  # Stop capturing when end_element is reached
        if isinstance(element, str):  # Check if the element is a NavigableString (text)
            texts.append(element.strip())

    combined_text = " ".join(texts)
    # Clean the captured text using clean_section_text function
    section_text = clean_section_text(combined_text)

    return section_text




