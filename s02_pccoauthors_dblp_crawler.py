# Project: ISCA 2021 Script
# Filename: s02_pccoauthors_dblp_crawler.py
# Date: March 16, 2021
# Author: Bagus Hanindhito (hanindhito[at]bagus[dot]my[dot]id)
# Title: PC Member Co-Authors Crawler
# Description:
## This script is used to collect all co-authors for each PC member from DBLP.
## The name of co-authors are determined from the publications listed on DBLP.
## This script will only take publications not older than the predefined threshold_year year.

#%% Import some libraries that are needed
import pandas as pd
import numpy as np
import tqdm
from datetime import datetime
from s00_function import request_publication_list

#%% Define the input and output CSV filename
# Input CSV filename
## This is CSV contains the PC members Person ID in the form of DBLP link.
## It is obtained after sanitized and manually checked the result of s01_pcname_to_dblp_person_id.py.
pc_to_dblp_filename = 'sample-data/output/isca2021-pc-to-dblp.csv'

# Output CSV filename
pc_coauthors_dblp_filename = 'sample-data/output/isca2021-pccoauthors.csv'

# %% Set the Threshold Date
# This date is to limit the oldest publication that is still considered as conflict
threshold_year = 2016

# %%# Load Input CSV to Pandas Dataframe
# Load the PC DBLP 
pc_to_dblp_df = pd.read_csv(pc_to_dblp_filename, converters={
    'affiliation_dblp': eval
    })

# %% Fetch all co-authors for each PC member.
# Initialize Empty List
pc_coauthors_list = []
for index,pc_member in tqdm.tqdm(pc_to_dblp_df.iterrows(), total=pc_to_dblp_df.shape[0]):
    xml_dict = request_publication_list(pc_member['url_dblp'])
    list_pub = xml_dict['dblpperson']['r']
    # For single publication, only dictionary is returned. We need to convert to list.
    if isinstance(list_pub, dict):
        list_pub = [list_pub]
    # Prepare coauthors list for pc_member
    coauthors_name_list = []
    coauthors_url_list  = []
    # Initiliaze the list with the PC's name and dblp url to avoid entering PC's name to the list
    # We will remove this at the end of the process.
    coauthors_name_list.append(pc_member['name_dblp'])
    coauthors_url_list.append(pc_member['url_dblp'])
    
    # Loop through all publications
    for pub in list_pub:
        for bib in pub.items():
            # Check the publication date whether it is younger than threshold
            #bib_date = datetime.strptime(bib[1]['@mdate'], '%Y-%m-%d')
            bib_year = int(bib[1]['year'])
            # If younger, then store the co-authors
            if(bib_year>=threshold_year): 
                # Sometimes they use key 'author' or 'editor'
                # We need to check both of them
                try:
                    authors = bib[1]['author']
                except:
                    authors = bib[1]['editor']
                # Sometime, only single author is returned, and thus a dict is returned.
                # We need to convert it to list.
                if isinstance(authors, dict):
                    authors = [authors]
                
                # Now, loop for each authors
                for author in authors:
                    url_dblp  = 'https://dblp.org/pid/' + author['@pid']
                    name_dblp = author['#text'].translate({ord(ch): None for ch in '0123456789'}).rstrip()
                    # Make sure the list always contains unique value
                    if url_dblp not in coauthors_url_list:
                        coauthors_name_list.append(name_dblp)
                        coauthors_url_list.append(url_dblp)
    
    # Remove the PC's name and dblp url.
    coauthors_name_list.pop(0)
    coauthors_url_list.pop(0)
    # Construct Dictionary
    pc_member_dblp_dict = \
    {
        "full_name"             : pc_member['full_name'],
        "first_name"            : pc_member['first_name'],
        "last_name"             : pc_member['last_name'],
        "affiliation"           : pc_member['affiliation'],
        "email"                 : pc_member['email'],
        "name_dblp"             : pc_member['name_dblp'],
        "url_dblp"              : pc_member['url_dblp'],
        "affiliation_dblp"      : pc_member['affiliation_dblp'],
        "coauthors_name_dblp"   : coauthors_name_list,
        "coauthors_url_dblp"    : coauthors_url_list
    }
    # Put into the list
    pc_coauthors_list.append(pc_member_dblp_dict)

# %% Convert pc_coauthors_list to Pandas DF and remove duplicates
pc_coauthors_df = pd.DataFrame(pc_coauthors_list)

# Convert Name DBLP and URL DBLP to List
pc_coauthors_df['name_dblp'] = pc_coauthors_df.apply(lambda row : [row['name_dblp']], axis = 1)
pc_coauthors_df['url_dblp'] = pc_coauthors_df.apply(lambda row : [row['url_dblp']], axis = 1)

# Merge based on email
pc_coauthors_df = pc_coauthors_df.groupby(['full_name','first_name','last_name','affiliation','email'], as_index=False).sum()

# %% Save the pc_coauthors_list to CSV
pc_coauthors_df.to_csv(pc_coauthors_dblp_filename, index=False)

# %%
