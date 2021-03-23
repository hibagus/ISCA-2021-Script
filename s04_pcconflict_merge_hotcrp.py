# Project: ISCA 2021 Script
# Filename: s04_pcconflict_merge_hotcrp.py
# Date: March 16, 2021
# Author: Bagus Hanindhito (hanindhito[at]bagus[dot]my[dot]id)
# Title: PC Member Co-Authors DBLP Merge to HotCRP
# Description:
## This script is used to merge co-authors list obtained from DBLP that has not been included 
## in collaborators list in HotCRP.
## Please make sure to backup HotCRP configuration before uploading the CSV file generated by this script.

#%% Import some libraries that are needed
import pandas as pd
import numpy as np
import tqdm

from s00_function import request_affiliation

#%% Define the input and output CSV filename
# Input CSV filename
pc_info_hotcrp_filename = 'sample-data/input/isca2021-pcinfo.csv'
pc_conflict_crosscheck_filename = 'sample-data/output/isca2021-pcconflict-crosscheck.csv'

# Output CSV filename
pc_info_hotcrp_update_filename = 'sample-data/output/isca2021-pcinfo-update.csv'

# %%# Load Input CSV to Pandas Dataframe
# Load the PC Info HotCRP
pc_info_hotcrp_df = pd.read_csv(pc_info_hotcrp_filename)
pc_info_hotcrp_df['collaborators'] = pc_info_hotcrp_df['collaborators'].fillna(' ')

# Load the PC Conflict Crosscheck
pc_conflict_crosscheck_df = pd.read_csv(pc_conflict_crosscheck_filename, converters={
    'conflict_only_dblp_name': eval, 
    'conflict_only_dblp_url': eval, 
    'conflict_only_hotcrp': eval}
    )
# %% Iterate over PC member
new_collaborators_list = []
for index,pc_member in tqdm.tqdm(pc_info_hotcrp_df.iterrows(), total=pc_info_hotcrp_df.shape[0]):
    email = pc_member['email']
    dblp_only_conflict_name = pc_conflict_crosscheck_df.loc[pc_conflict_crosscheck_df['email']==email]['conflict_only_dblp_name'].to_list()[0]
    dblp_only_conflict_url = pc_conflict_crosscheck_df.loc[pc_conflict_crosscheck_df['email']==email]['conflict_only_dblp_url'].to_list()[0]
    new_conflict_strings = ''
    if(len(dblp_only_conflict_name)!=0):
        new_conflict_strings = '\n'
        for name_dblp,url_dblp in zip(dblp_only_conflict_name,dblp_only_conflict_url):

            # !!! THIS WILL TAKE VERY LONG TIME !!!
            # comment these two lines below if you don't want affiliation information
            affiliation = request_affiliation(url_dblp)
            conflict_string = name_dblp + ' (' + affiliation + ')\n'

            # uncomment this line below to put generic affiliation to reduce runtime
            #conflict_string = name_dblp + ' (NONE <dblp>)\n'
            new_conflict_strings = new_conflict_strings + conflict_string
            
    new_collaborators_dict = \
    {
        "email"             : pc_member['email'],
        "new_collaborators" : pc_member['collaborators'] + new_conflict_strings[:-1]
    }
    new_collaborators_list.append(new_collaborators_dict)

new_collaborators_df = pd.DataFrame(new_collaborators_list)
pc_info_hotcrp_df['collaborators'] = new_collaborators_df['new_collaborators']
# %% Dump to CSV and Post-Processing
#print(pc_info_hotcrp_df.dtypes)
pc_info_hotcrp_df.to_csv(pc_info_hotcrp_update_filename, index=False)

# post-processing to match the CSV header
with open(pc_info_hotcrp_filename) as orig_file:
    lines_orig = orig_file.readlines()

with open(pc_info_hotcrp_update_filename) as target_file:
    lines_targ = target_file.readlines()

lines_targ[0] = lines_orig[0]

with open(pc_info_hotcrp_update_filename, "w") as target_file:
    target_file.writelines(lines_targ)
# %%