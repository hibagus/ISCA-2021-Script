# Project: ISCA 2021 Script
# Filename: s03_pcconflict_crosscheck.py
# Date: March 16, 2021
# Author: Bagus Hanindhito (hanindhito[at]bagus[dot]my[dot]id)
# Title: PC Member Conflict Crosscheck DBLP and HotCRP
# Description:
## This script is used to crosscheck the conflict entered by each PC member on HotCRP
## and the co-author list from DBLP. It will create the diff between collaborators list from
## HotCRP and co-author list from DBLP.

#%% Import some libraries that are needed
import pandas as pd
import numpy as np
import tqdm
import re
from fuzzywuzzy import process
#%% Define the input and output CSV filename
# Input CSV filename
pc_info_hotcrp_filename = 'sample-data/input/isca2021-pcinfo.csv'

pc_coauthors_dblp_filename = 'sample-data/output/isca2021-pccoauthors.csv'

# Output CSV filename
pc_coauthors_conflict_crosscheck_filename = 'sample-data/output/isca2021-pcconflict-crosscheck.csv'

# %%# Load Input CSV to Pandas Dataframe
# Load the PC Info HotCRP
pc_info_hotcrp_df = pd.read_csv(pc_info_hotcrp_filename)

# Load the PC Coauthors DBLP
pc_coauthors_dblp_df = pd.read_csv(pc_coauthors_dblp_filename, converters={
    'name_dblp': eval, 
    'url_dblp': eval, 
    'affiliation_dblp': eval,
    'coauthors_name_dblp': eval, 
    'coauthors_url_dblp': eval}
    )

# %% Sanitize PC Info HotCRP Collaborator (e.g., convert to list)

# Fill NA
pc_info_hotcrp_df['collaborators'] = pc_info_hotcrp_df['collaborators'].fillna(' ')

# Remove affiliation name
pc_info_hotcrp_df['collaborators_name'] = pc_info_hotcrp_df.apply(lambda row: re.sub(r'\s\([^)]*\)', '', row['collaborators']), axis=1)
pc_info_hotcrp_df['collaborators_name'] = pc_info_hotcrp_df.apply(lambda row: re.sub(r'\([^)]*\)', '', row['collaborators_name']), axis=1)
pc_info_hotcrp_df['collaborators_name'] = pc_info_hotcrp_df.apply(lambda row: row['collaborators_name'].split('\n'), axis=1)

# %% Cross Check HotCRP to DBLP
hotcrp_to_dblp_crosschecks_list = []
for index,pc_member in tqdm.tqdm(pc_info_hotcrp_df.iterrows(), total=pc_info_hotcrp_df.shape[0]):
    conflict_only_on_hotcrp = []
    email = pc_member['email']
    conflicts_from_dblp = pc_coauthors_dblp_df.loc[pc_coauthors_dblp_df['email']==email]['coauthors_name_dblp'].to_list()[0] 

    if(len(conflicts_from_dblp)!=0):
        for conflict_hotcrp in pc_member['collaborators_name']:
            highest = process.extractOne(conflict_hotcrp,conflicts_from_dblp)
            if(highest[1]<90):
                conflict_only_on_hotcrp.append(conflict_hotcrp)

    hotcrp_to_dblp_crosschecks_dict = \
    {
        "email"                : email,
        "conflict_only_hotcrp" : conflict_only_on_hotcrp
    }
    hotcrp_to_dblp_crosschecks_list.append(hotcrp_to_dblp_crosschecks_dict)

# %% Cross Check DBLP to HotCRP
dblp_to_hotcrp_crosschecks_list = []
for index,pc_member in tqdm.tqdm(pc_coauthors_dblp_df.iterrows(), total=pc_coauthors_dblp_df.shape[0]):
    conflict_only_on_dblp_name = []
    conflict_only_on_dblp_url = []
    email = pc_member['email']
    conflicts_from_hotcrp= pc_info_hotcrp_df.loc[pc_info_hotcrp_df['email']==email]['collaborators_name'].to_list()[0] 
    if(len(conflicts_from_hotcrp)!=0):
        for name_dblp,url_dblp in zip(pc_member['coauthors_name_dblp'],pc_member['coauthors_url_dblp']) :
            highest = process.extractOne(name_dblp,conflicts_from_hotcrp)
            if(highest[1]<90):
                conflict_only_on_dblp_name.append(name_dblp)
                conflict_only_on_dblp_url.append(url_dblp)
    dblp_to_hotcrp_crosschecks_dict = \
    {
        "email"                  : email,
        "conflict_only_dblp_name": conflict_only_on_dblp_name,
        "conflict_only_dblp_url" : conflict_only_on_dblp_url
    }
    dblp_to_hotcrp_crosschecks_list.append(dblp_to_hotcrp_crosschecks_dict)
# %% Combine all of them
hotcrp_to_dblp_crosschecks_df = pd.DataFrame(hotcrp_to_dblp_crosschecks_list)
dblp_to_hotcrp_crosschecks_df = pd.DataFrame(dblp_to_hotcrp_crosschecks_list)

pc_conflict_crosscheck_df = pc_coauthors_dblp_df[['full_name','email']]
pc_conflict_crosscheck_df['conflict_only_dblp_name'] = dblp_to_hotcrp_crosschecks_df['conflict_only_dblp_name']
pc_conflict_crosscheck_df['conflict_only_dblp_url'] = dblp_to_hotcrp_crosschecks_df['conflict_only_dblp_url']
pc_conflict_crosscheck_df['conflict_only_hotcrp'] = hotcrp_to_dblp_crosschecks_df['conflict_only_hotcrp']

# %% Save as CSV
pc_conflict_crosscheck_df.to_csv(pc_coauthors_conflict_crosscheck_filename, index=False)

# %%
