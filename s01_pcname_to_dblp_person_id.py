# Project: ISCA 2021 Script
# Filename: s01_pcname_to_dblp_person_id.py
# Date: March 16, 2021
# Author: Bagus Hanindhito (hanindhito[at]bagus[dot]my[dot]id)
# Title: PC Member Name to DBLP Person ID Lookup Script
# Description:
## This script is used to look-up appropriate DBLP Person ID that match
## with a given name (first name and last name). The script uses fuzzy match
## to match the given person name with the DBLP person name. Because of homonym 
## (i.e., multiple persons with the same name), the script may output multiple 
## person with the same name and requires a bit of manual works to choose the 
## correct person. 

#%% Import some libraries that are needed
import pandas as pd
import numpy as np
import tqdm
import os
from fuzzywuzzy import fuzz
from s00_function import request_author_key
from s00_function import merge_affiliation
from s00_function import convert_to_dict
from s00_function import filter_name
from s00_function import filter_affiliation

#%% Define the input and output CSV filename
# Input CSV filename
## This is CSV file obtained from HotCRP by going to Users and select 'Program Committee' in the
## filter. At the bottom of page, click Select All then Download 'PC info' and click 'Go'
## 
pc_info_hotcrp_filename = 'sample-data/input/isca2021-pcinfo.csv'

# Output CSV filename
pc_to_dblp_filename = 'sample-data/output/isca2021-pc-to-dblp.csv'

# %% Load Input CSV to Pandas Dataframe
# Load the PC Info from HotCRP
pc_info_hotcrp_df = pd.read_csv(pc_info_hotcrp_filename)

# %% Sanitize
# Construct and Sanitize First name and Last name
pc_members_name = pd.DataFrame(pc_info_hotcrp_df['first'] + " " + pc_info_hotcrp_df['last'], columns = ['full'])
pc_members_name['split'] = pc_members_name['full'].str.split()
pc_members_name['last'] = pc_members_name['split'].str[-1]
pc_members_name['first'] = pc_members_name.apply(lambda x: x['full'].replace(" " + x['last'],""), axis=1)
pc_members_name['affiliation'] = pc_info_hotcrp_df['affiliation']
pc_members_name['email'] = pc_info_hotcrp_df['email']
del pc_members_name['split']

# %% Request DBLP Person ID for each PC Members
pc_members_list = []

for index,pc_member in tqdm.tqdm(pc_members_name.iterrows(), total=pc_members_name.shape[0]):
    pc_json = request_author_key(pc_member["first"], pc_member["last"])    
    pc_member_dblp_list = convert_to_dict(pc_member, pc_json)
    confidence_level=100
    pc_member_dblp_list_filtered = []
    
    # Filtering by name with the highest confidence level
    # then gradually reducing the confidence level until at least one item come up.
    # This is not 100% perfect.
    while(len(pc_member_dblp_list_filtered)<1):
        pc_member_dblp_list_filtered=filter_name(pc_member_dblp_list, confidence_level)
        confidence_level=confidence_level-1
    pc_member_dblp_list = pc_member_dblp_list_filtered   
    pc_member_dblp_list_filtered = filter_affiliation(pc_member_dblp_list)
    
    # Filtering by Affiliation
    if(len(pc_member_dblp_list_filtered)>0):
        pc_member_dblp_list = pc_member_dblp_list_filtered
    
    # Add to the Final List
    pc_members_list = pc_members_list + pc_member_dblp_list

# %% Write Output to CSV
# This CSV needs to be inspected manually.
## NOTE: To avoid overwritting, rename the final CSV file to something else.
pc_members_df = pd.DataFrame(pc_members_list)
pc_members_df.to_csv(pc_to_dblp_filename, index=False)

# %%
