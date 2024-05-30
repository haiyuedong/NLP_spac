# find cik of the nyseipo stocks


# company name and cik
# cik dic from https://www.sec.gov/os/accessing-edgar-data

#%% find SEC cik 
import json
from numpy import column_stack
import pandas as pd
import re
from difflib import SequenceMatcher
import difflib
import numpy as np
import warnings

warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)


#%% organize SEC cik finder
cik = pd.read_fwf('cik-lookup-data.txt',encoding = "ISO-8859-1",header=None)
cik.rename(columns={0:'company name'},inplace=True)

# find numbers
def findcik(x):
    match=re.findall(r'[0-9]{10}',x['company name'])
    x['cik']=match
    x['company name'] = re.sub(r'[0-9]{10}','',x['company name'])
    #if re.search(r'^[a-zA-Z]', x['company name']):
    #    x['keep']=1
    #else:
    #    x['keep']=0
    return x
cik=cik.apply(lambda x: findcik(x), axis=1)
#cik = cik[cik['keep']==1]

#break cik according to start alphabet
cikdic = {}
cik['namestart']=cik['company name'].astype(str).str[0]
#cik['namestart'] = cik['namestart'].apply(lambda x: 'ne' if not str(x).isalpha() else x)
ciknamestart = cik['namestart'].value_counts().reset_index()
# Convert 'ciknamestart' column to a list, if necessary
ciknamestart_list = ciknamestart['namestart'].tolist()
# Create a dictionary mapping each starting letter (or 'ne') to the corresponding subset of the DataFrame
cikdic = {item: cik[cik['namestart'] == item] for item in ciknamestart_list}

#%% 
nyseipo = pd.read_excel('nyseipo.xlsx')
for i in nyseipo['Company Name']:
    iind = nyseipo[nyseipo['Company Name'] == i].index.values.item()
    company_name = i.upper()
    thiscik = cikdic[company_name[0]]
    thiscik['first letter'] = thiscik['company name'].str.replace(' ', '').str[0]

    first_letter = company_name[0].upper()
    thiscik = thiscik[thiscik['first letter']==first_letter]
    if thiscik.empty:
        nyseipo.at[iind, 'cik']=np.nan
    else:
        result = difflib.get_close_matches(company_name.upper(),list(thiscik['company name']),n=1)
        if result==[]:
            nyseipo.at[iind, 'cik']=np.nan
            continue
        else:
            company_cik = thiscik.loc[thiscik['company name']==result[0],'cik']
        
        if len(company_cik)==1:
            nyseipo.at[iind, 'cik']=company_cik.item()
        else:
            nyseipo.at[iind, 'cik']=np.nan

#%%
#spacs['cik']=spacs['cik'].str.strip("['")
#spacs['cik']=spacs['cik'].str.strip("']")
nyseipo.to_excel('nyseipo_wcik.xlsx',index=False)
# %%
