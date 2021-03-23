# Project: ISCA 2021 Script
# Filename: s06_paper_discussion_window.py
# Date: March 16, 2021
# Author: Bagus Hanindhito (hanindhito[at]bagus[dot]my[dot]id)
# Title: Paper Discussion Window Scheduling for PC Meeting
# Description:
## This script will generate discussion schedule for each paper during PC meeting.

#%% Import some libraries that are needed
import pandas as pd
import numpy as np
import tqdm
import re
import hashlib
import os
import ast
from fuzzywuzzy import process

#%% Define the input and output CSV filename
# Input CSV filename
## Note: Sample data is unavailable
paper_authors_filename        = 'sample-data/input/isca2021-authors.csv'
paper_data_filename           = 'sample-data/input/isca2021-paperdata.csv'
paper_pc_conflict_filename    = 'sample-data/input/isca2021-pcconflicts.csv'
paper_pc_assignment_filename  = 'sample-data/input/isca2021-pcassignments.csv'
pc_avail_doodle_filename      = 'sample-data/input/isca2021-pcavailability.csv'

# Output CSV filename
schedule_filename             = 'sample-data/output/isca2021-paperschedule.csv'
# %%
# Load the PC Availability Data
pc_avail_doodle_df = pd.read_csv(pc_avail_doodle_filename)

# Load the paper assignment data
paper_pc_assignment_df = pd.read_csv(paper_pc_assignment_filename)

# Load the Paper Authors
paper_authors_df = pd.read_csv(paper_authors_filename)

# Load the Paper Data
paper_data_df = pd.read_csv(paper_data_filename)

# Load the Paper PC Conflict
paper_pc_conflict_df = pd.read_csv(paper_pc_conflict_filename)

# %% Process paper authors
paper_authors_df['full name'] = paper_authors_df['first'] + ' ' + paper_authors_df['last']
paper_authors_merge_df = paper_authors_df.groupby('paper').agg({'full name': lambda x: list(x)})

# %% Process paper_data
paper_data_df['Tags'] = paper_data_df['Tags'].fillna('#NA').str.lower()
paper_data_df['Tags'] = paper_data_df['Tags'].apply(lambda x: list(x.split(' ')))

# %% Process paper_pc_conflict
paper_pc_conflict_df['full name'] = paper_pc_conflict_df['first'] + ' ' + paper_pc_conflict_df['last']
paper_pc_conflict_merge_df = paper_pc_conflict_df.groupby('paper').agg({'full name': lambda x: list(x), 'email': lambda x: list(x)})

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

# %% Preprocess DF
# Preprocess Doodle by changing 0 to NOT_OK and nan to OK
# adjust this to match the Doodle Time Slot
pc_avail_doodle_df[['1', '2', '3','4','5','6','7','8','9','10','11','12','13','14','15','16']] = \
    pc_avail_doodle_df[['1', '2', '3','4','5','6','7','8','9','10','11','12','13','14','15','16']].replace(
        ['0',np.nan],['NOT_OK','OK']
    )

# Preprocess Paper Assignment
# Drop all rows that contains meaningless info
paper_pc_assignment_df       = paper_pc_assignment_df[~paper_pc_assignment_df['action'].isin(['clearreview'])]
# Delete all ERC based on the email available in Doodle
paper_pc_assignment_df       = paper_pc_assignment_df[paper_pc_assignment_df['email'].isin(pc_avail_doodle_df['hotcrp_email'].tolist())]
# Merge based on the paper ID
paper_pc_assignment_merge_df = paper_pc_assignment_df.groupby('paper', as_index=False).agg({'email': lambda x: list(x)})
paper_pc_assignment_merge_df.rename(columns={'paper':'ID'}, inplace=True)
paper_pc_assignment_merge_df.rename(columns={'email':'reviewer email'}, inplace=True)

# %% Iterate trough each paper
paper_window_list = []
for index,paper in tqdm.tqdm(paper_pc_assignment_merge_df.iterrows(), total=paper_pc_assignment_merge_df.shape[0]):
    # Iterate through each timeslot
    paper_window_dict = {}
    paper_window_dict['ID'] = paper['ID']
    for timeslot in range(1, 17):
        num_pc_avail = 0
        # Iterate through each reviewer
        for reviewer in paper['reviewer email']:
            status = pc_avail_doodle_df.loc[pc_avail_doodle_df['hotcrp_email'] == reviewer][str(timeslot)].tolist()[0]
            if (status == 'OK'):
                num_pc_avail = num_pc_avail - 0
            elif (status == '(OK)') :
                num_pc_avail = num_pc_avail - 1
            else:
                num_pc_avail = num_pc_avail - 2

        paper_window_dict[str(timeslot)] = num_pc_avail
    
    paper_window_list.append(paper_window_dict)

paper_window_df = pd.DataFrame(paper_window_list)

# %% Combine paper info with paper window
paper_combine_df = pd.merge(papers_df, paper_window_df, on='ID')
paper_combine_df = pd.merge(paper_combine_df, paper_pc_assignment_merge_df, on='ID')
# %% Filtering
paper_combine_filter_df = paper_combine_df.copy()
paper_combine_filter_df.sort_values(['ID'], ascending=[True], inplace=True)
paper_combine_filter_df.reset_index(drop=True, inplace=True)
# %% Allocate Paper
target_paper_per_timeslot = 6
number_of_paper = paper_combine_filter_df.shape[0]
schedule_dict = {}
stop = False
# priority 1st -> same reviewer
# priority 2nd -> same conflict

previous_conflict = []
previous_reviewer = []

for current_threshold in tqdm.tqdm(range(0,-12,-1)):
    for phase in range(1,3):
        for timeslot in range(1, 17):
            ## Check if this timeslot is already full
            #if timeslot in schedule_dict.keys():
            #    if(len(schedule_dict[timeslot])>=target_paper_per_timeslot):
            #        continue
            for subslot in range (1,target_paper_per_timeslot):
                if (not previous_reviewer): 
                    # first element
                    paper_found = False
                    row_index = 0
                    while not paper_found:
                        current_paper = paper_combine_filter_df.iloc[[row_index]]
                        if(current_paper[str(timeslot)].iloc[0]==current_threshold):
                            paper_found = True
                        else:
                            row_index = row_index+1
                            if(row_index>=number_of_paper):
                                # if the row index larger than the number of paper
                                print("Warning! No more paper that can be scheduled on timeslot " + str(timeslot) + " with threshold " + str(current_threshold) + "\n")
                                stop = True
                                break
                    if paper_found:
                        current_paper = paper_combine_filter_df.iloc[[row_index]]
                        previous_conflict = current_paper['pc conflict email'].iloc[0]
                        previous_reviewer = current_paper['reviewer email'].iloc[0]
                        #schedule_dict.setdefault(timeslot, []).append(current_paper['ID'].iloc[0])
                        schedule_dict.setdefault(timeslot, []).append([current_paper['ID'].iloc[0], current_paper[str(timeslot)].iloc[0]])
                        paper_combine_filter_df.drop(row_index, inplace=True) 
                        paper_combine_filter_df.reset_index(drop=True, inplace=True)
                        #print(schedule_dict)
                else:
                    # find list of paper that satisfy the threshold
                    papers = []
                    paper_found = False
                    while not paper_found:
                        for index, paper in paper_combine_filter_df.iterrows():
                            if(paper[str(timeslot)]==current_threshold):
                                papers.append(paper)
        
                        if (not papers):
                            print("Warning! No more paper that can be scheduled on timeslot " + str(timeslot) + " with threshold " + str(current_threshold) + "\n")
                            stop = True
                            break
                        else:
                            paper_found = True
                    
                    if (paper_found):
                        if(len(papers) == 1):
                            # Only single paper is available on the particular timeslot
                            current_paper = papers[0]
                            previous_conflict = current_paper['pc conflict email']
                            previous_reviewer = current_paper['reviewer email']
                            #schedule_dict.setdefault(timeslot, []).append(current_paper['ID'])
                            schedule_dict.setdefault(timeslot, []).append([current_paper['ID'],current_paper[str(timeslot)]])
                            row_index = paper_combine_filter_df[paper_combine_filter_df['ID']==current_paper['ID']].index
                            paper_combine_filter_df.drop(row_index, inplace=True) 
                            paper_combine_filter_df.reset_index(drop=True, inplace=True)
                            #print(schedule_dict)
                        else:
                            # Let's decide :) 
                            papers_df = pd.DataFrame(papers)
                            papers_df['lowest_threshold']= (papers_df.loc[:,str(timeslot):'16'] == current_threshold).sum(axis=1)
                            papers_df['common_reviewer'] = papers_df['reviewer email'].apply(lambda x: len(set(x) & set(previous_reviewer)))
                            papers_df['common_conflict'] = papers_df['pc conflict email'].apply(lambda x: len(set(x) & set(previous_conflict)))
                            papers_df.sort_values(['lowest_threshold','common_reviewer', 'common_conflict'], ascending=[True, False, False], inplace=True)
                            papers_df.reset_index(drop=True, inplace=True)
        
                            current_paper = papers_df.iloc[[0]]
                            previous_conflict = current_paper['pc conflict email'].iloc[0]
                            previous_reviewer = current_paper['reviewer email'].iloc[0]
                            #schedule_dict.setdefault(timeslot, []).append(current_paper['ID'].iloc[0])
                            schedule_dict.setdefault(timeslot, []).append([current_paper['ID'].iloc[0],current_paper[str(timeslot)].iloc[0]])
                            row_index = paper_combine_filter_df[paper_combine_filter_df['ID']==current_paper['ID'].iloc[0]].index
                            paper_combine_filter_df.drop(row_index, inplace=True) 
                            paper_combine_filter_df.reset_index(drop=True, inplace=True)
                            #print(schedule_dict)
    
                # if no more papers that can be scheduled on current time slots
                if (stop):
                    break
    
            number_of_paper = paper_combine_filter_df.shape[0]
            if(number_of_paper==0):
                print("No more unscheduled paper\n")
                break

    number_of_paper = paper_combine_filter_df.shape[0]
    if(number_of_paper==0):
        print("No more unscheduled paper\n")
        break

# %% Post Processing the Schedule Dictionary
schedule_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in schedule_dict.items() ]))
schedule_df.to_csv(schedule_filename, index=False)

# %%
