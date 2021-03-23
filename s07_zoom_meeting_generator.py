# Project: ISCA 2021 Script
# Filename: s07_zoom_meeting_generator.py
# Date: March 16, 2021
# Author: Bagus Hanindhito (hanindhito[at]bagus[dot]my[dot]id)
# Title: PC Meeting - Zoom Breakout Room Generator
# Description:
## This script will generate zoom breakout room configuration for each paper based on PC conflict

#%% Import some libraries that are needed
import pandas as pd
import numpy as np
import tqdm
import re
import hashlib
import os
from fuzzywuzzy import process

#%% Define the input and output CSV filename
# Input CSV filename
## Note: Sample data is unavailable
paper_authors_filename        = 'sample-data/input/isca2021-authors.csv'
paper_data_filename           = 'sample-data/input/isca2021-paperdata.csv'
paper_pc_conflict_filename    = 'sample-data/input/isca2021-pcconflicts.csv'
pcpc_conflict_info_filename   = 'sample-data/output/isca2021-pcconflict-crosscheck.csv'
pc_member_zoom_info_filename  = 'sample-data/input/isca2021-pczoom.csv' 

# Output CSV filename
zoom_csv_config_non_hash_folder = 'sample-data/output/zoom'
zoom_csv_config_hash_folder     = 'sample-data/output/zoom_hashed'
conflict_csv_non_hash_folder    = 'sample-data/output/conflict'
conflict_csv_hash_folder        = 'sample-data/output/conflict_hashed'
paper_summary_filename          = 'sample-data/output/isca2021-paper-summary.csv'

#%% Define constant
# Predefined Email
lizy_discussion_account    = 'ljohn@eid.utexas.edu' 
lizy_conflict_account      = 'lizy.john@gmail.com'
sandhya_discussion_account = 'sandhya.dwarkadas@rochester.edu'
bagus_discussion_account   = 'bh29293@eid.utexas.edu'
aman_discussion_account    = 'aa36432@eid.utexas.edu'
bagus_hotcrp_email         = 'hanindhito@bagus.my.id'
aman_hotcrp_email          = 'aman.kbm@utexas.edu'
lizy_hotcrp_email          = 'ljohn@ece.utexas.edu'
sandhya_hotcrp_email       = 'sandhya@cs.rochester.edu'

#Define Room Name
discussion_room = 'Discussion Room'
conflict_room   = 'Conflict Room'

#%% Load CSV to Pandas DF

# Load the Paper Authors
paper_authors_df = pd.read_csv(paper_authors_filename)

# Load the Paper Data
paper_data_df = pd.read_csv(paper_data_filename)

# Load the Paper PC Conflict
paper_pc_conflict_df = pd.read_csv(paper_pc_conflict_filename)

# Load the PC PC Conflict Info
pcpc_conflict_info_df = pd.read_csv(pcpc_conflict_info_filename, converters={
    'conflict_only_dblp_name': eval, 
    'conflict_only_dblp_url': eval, 
    'conflict_only_hotcrp': eval}
    )

# %% Process paper authors
paper_authors_df['full name'] = paper_authors_df['first'] + ' ' + paper_authors_df['last']
paper_authors_merge_df = paper_authors_df.groupby('paper').agg({'full name': lambda x: list(x)})

# %% Process paper_data
paper_data_df['Tags'] = paper_data_df['Tags'].fillna('#NA')
paper_data_df['Tags'] = paper_data_df['Tags'].apply(lambda x: list(x.split(' ')))

# %% Process paper_pc_conflict
paper_pc_conflict_df['full name'] = paper_pc_conflict_df['first'] + ' ' + paper_pc_conflict_df['last']
paper_pc_conflict_merge_df = paper_pc_conflict_df.groupby('paper').agg({'full name': lambda x: list(x), 'email': lambda x: list(x)})
#paper_pc_conflict_merge_df.to_csv('Output-CSV/test.csv', index=False)

# %% Create new dataframe for papers data
papers_df = paper_data_df[['ID','Title','Tags']]

# Merge the authors
papers_df['authors'] = papers_df.ID.map(paper_authors_merge_df['full name'])

# Merge PC Conflict Name
papers_df['pc conflict name'] = papers_df.ID.map(paper_pc_conflict_merge_df['full name']).fillna("#NA")
papers_df['pc conflict email'] = papers_df.ID.map(paper_pc_conflict_merge_df['email']).fillna("#NA")

# Generate Paper Hash based on Title and Paper ID
#hashlib.sha256().hexdigest()
papers_df['hash'] = papers_df.apply(lambda x: hashlib.sha256((str(x.ID) + '@' + x.Title).encode('utf-8')).hexdigest()[:6], axis=1)
papers_df['hash'] = papers_df['hash'].astype(str)
#papers_df.to_csv('Output-CSV/test.csv', index=False)

# %% Load PC Zoom Info
pc_member_zoom_info_df = pd.read_csv(pc_member_zoom_info_filename)
#pc_member_zoom_info_df['Zoom email 1'] = pc_member_zoom_info_df.apply(lambda x:  x[x.last_valid_index()], axis=1)
#pc_member_zoom_info_df['Zoom email 2'] = pc_member_zoom_info_df.apply(lambda x:  x[x.last_valid_index()], axis=1)
pc_member_zoom_info_df['Zoom email 2'] = pc_member_zoom_info_df['Zoom email 2'].fillna('#na')

# %% Merge PC Zoom Info and PC Conflict Info
pcpc_merged_info_df = pd.merge(pc_member_zoom_info_df, pcpc_conflict_info_df, on='hotcrp_email')

# %% Make Folder 
if not os.path.exists(zoom_csv_config_non_hash_folder):
    os.makedirs(zoom_csv_config_non_hash_folder)
if not os.path.exists(zoom_csv_config_hash_folder):
    os.makedirs(zoom_csv_config_hash_folder)
if not os.path.exists(conflict_csv_non_hash_folder):
    os.makedirs(conflict_csv_non_hash_folder)
if not os.path.exists(conflict_csv_hash_folder):
    os.makedirs(conflict_csv_hash_folder)

# %% Iterate through each paper
for index,paper in tqdm.tqdm(papers_df.iterrows(), total=papers_df.shape[0]):
    participant_list = []
    conflict_list = []
    conflict_email_list = []
    discussion_email_list = []
    
    # Loop through PC Member
    for index,pc_member in pcpc_merged_info_df.iterrows():
        is_this_pc_conflict = False
        # Check author-side conflict
        if(pc_member['hotcrp_email'] in paper['pc conflict email']):
            # This pc member has conflict with the paper
            is_this_pc_conflict = True
        
        # Check pc-side conflict
        # DBLP
        #if(is_this_pc_conflict == False):
        #    for author in paper['authors']:
        #        if(pd.isna(author)):
        #            continue
        #        highest = process.extractOne(author,pc_member['conflict_only_dblp_name'])
        #        if highest is not None:            
        #            if(highest[1]>=95):
        #                ## Possible Conflict with author
        #                print("["+str(paper['ID']) + "] Possible DBLP conflict author " + author + " with pcpc " + pc_member['Name'] + " with probability " + str(highest[1]) +"\n")
        #                is_this_pc_conflict = True

        # HOTCRP
        #if(is_this_pc_conflict == False):
        #    for author in paper['authors']:
        #        if(pd.isna(author)):
        #            continue
        #        highest = process.extractOne(author,pc_member['conflict_only_hotcrp'])
        #        if highest is not None: 
        #            if(highest[1]>=95):
        #                ## Possible Conflict with author
        #                print("["+str(paper['ID']) + "] Possible HOTCRP conflict author " + author + " with pcpc " + pc_member['Name'] + " with probability " + str(highest[1]) +"\n")
        #                is_this_pc_conflict = True

        # Register PC Member as Conflict or Discussion
        if(is_this_pc_conflict == True):
            # Conflict
            conflict_email_list.append(pc_member['hotcrp_email'])
            participant_dict = \
            {
                "Pre-assign Room Name" : conflict_room,
                "Email Address"        : pc_member['Zoom email 1']
            }
            participant_list.append(participant_dict)

            if(pc_member['Zoom email 1']!=pc_member['Zoom email 2'] and pc_member['Zoom email 2'] != '#na'):
                # Multiple zoom account handle
                participant_dict = \
                {
                    "Pre-assign Room Name" : conflict_room,
                    "Email Address"        : pc_member['Zoom email 2']
                }
                participant_list.append(participant_dict)
            conflict_list.append(pc_member['Name'] + " (" + pc_member['Institution'] + ")")
        else :
            # No Conflict
            discussion_email_list.append(pc_member['hotcrp_email'])
            participant_dict = \
            {
                "Pre-assign Room Name" : discussion_room,
                "Email Address"        : pc_member['Zoom email 1']
            }
            participant_list.append(participant_dict)

            if(pc_member['Zoom email 1']!=pc_member['Zoom email 2'] and pc_member['Zoom email 2'] != '#na'):
                # Multiple zoom account handle
                participant_dict = \
                {
                    "Pre-assign Room Name" : discussion_room,
                    "Email Address"        : pc_member['Zoom email 2']
                }
                participant_list.append(participant_dict)

    # post Processing
    # make sure lizy email is in discussion room
    if(lizy_hotcrp_email not in discussion_email_list):
        if(sandhya_hotcrp_email in discussion_email_list):
            print("["+str(paper['ID']) + "] Lizy conflict is detected and Sandhya replaces Lizy\n")
        else:
            print("["+str(paper['ID']) + "] !!!! Something Has Gone Wrong !!!!\n")

    # Second, default assignment for bagus discussion account and lizy conflict account
    # Always add Bagus Discussion Account to Discussion Room
    participant_dict = \
    {
        "Pre-assign Room Name" : discussion_room,
        "Email Address"        : bagus_discussion_account
    }
    participant_list.append(participant_dict)
    # Keep Lizy Gmail Account in the Main Room
    ## Always add Lizy Conflict Account to Conflict Room
    #participant_dict = \
    #{
    #    "Pre-assign Room Name" : conflict_room,
    #    "Email Address"        : lizy_conflict_account
    #}
    #participant_list.append(participant_dict)

    # Always add Lizy Conflict Account to Conflict Room
    participant_dict = \
    {
        "Pre-assign Room Name" : discussion_room,
        "Email Address"        : 'zoom@bagus.my.id'
    }
    participant_list.append(participant_dict)

    # Then, handle Aman Conflict
    # Does not need to be so precise -- depends only on the authors-side 
    # since he will not be able to see the paper on HotCRP.
    if(aman_hotcrp_email in paper['pc conflict email']) :
        # Aman is in conflict with the paper
        # Add Aman to Conflict Room
        participant_dict = \
        {
            "Pre-assign Room Name" : conflict_room,
            "Email Address"        : aman_discussion_account
        }
        participant_list.append(participant_dict)
        participant_dict = \
        {
            "Pre-assign Room Name" : conflict_room,
            "Email Address"        : 'zjs362@eid.utexas.edu'
        }
        participant_list.append(participant_dict)
        #conflict_list.append("Aman Arora (UT Austin)")
    else :
        # Aman is not in conflict with the paper
        # Add Aman to Discussion Room
        participant_dict = \
        {
            "Pre-assign Room Name" : discussion_room,
            "Email Address"        : aman_discussion_account
        }
        participant_list.append(participant_dict)
        participant_dict = \
        {
            "Pre-assign Room Name" : discussion_room,
            "Email Address"        : 'zjs362@eid.utexas.edu'
        }
        participant_list.append(participant_dict)


    # Write the data to the output
    participant_df = pd.DataFrame(participant_list)
    conflict_df    = pd.DataFrame(conflict_list)

    participant_df.to_csv(zoom_csv_config_non_hash_folder+"/"+str(paper['ID'])+".csv", index=False)
    participant_df.to_csv(zoom_csv_config_hash_folder+"/"+paper['hash']+".csv", index=False)

    conflict_df.to_csv(conflict_csv_non_hash_folder+"/"+str(paper['ID'])+".csv", index=False, header=False)
    conflict_df.to_csv(conflict_csv_hash_folder+"/"+paper['hash']+".csv", index=False, header=False)

# %% Save Paper Summary
papers_df.rename(columns={'authors':'Authors'}, inplace=True)
papers_df.to_csv(paper_summary_filename, index=False)

