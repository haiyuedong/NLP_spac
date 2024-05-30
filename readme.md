##  Steps
1. List of SPAC IPOs and their ciks
2. Download IPO filings
3. Prepare sections of filings
4. Text analysis of Risk Factors section 

## Contents

edgar_nyseipo_cik.py: find cik of IPO companies using the cik-look-up txt provided by EDGAR and save new data to nyseipo_wcik.xlsx.

nyseipo_identify_spacs.py: identify spacs in nyseipo_wcik.xlsx by using cik and edgar filing info. Output saved to nyseipo_wcik_spacs.xlsx

edgar_fx.py: functions dowloading and processing edgar filings.

edgar_download_compare_dates.py: (1) download spacs s_1 or 424b4 for those in nyseipo_wcik_spacs.xlsx sheet spacs. (2) compare date difference of the filings and ipo dates to see if the correct filings are downloaded. usually if the dates are within 2 weeks, should be correct. (3) There are 17 spacs whose final prospectus is 424bX (X not 4). Their corresponding forms and txt files are downloaded. Output saved to folder SPAC424B4_full.

edgar_parse_fx.py: functions processing downloaded local filings. mainly to get table of contents of filings (SPAC424B4_toc.json) and `risk factors' parts in the filings.

prospectus_put2folders.py: processing downloaded local filings and save risk factors parts  (all saved to SPAC424BX_RiskFactors folder).

