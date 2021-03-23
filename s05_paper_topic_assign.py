# Project: ISCA 2021 Script
# Filename: s05_paper_topic_assign.py
# Date: March 16, 2021
# Author: Bagus Hanindhito (hanindhito[at]bagus[dot]my[dot]id)
# Title: Paper Topic Assignment Based on Topic Priority
# Description:
## This script is used to assign topic of each paper based on predefined topic priority.
## The output of the script can be used to guide the reviewer assignment to each paper.

#%% Import some libraries that are needed
import pandas as pd
import numpy as py

#%% Define the filename
list_of_papers_topics='sample-data/input/isca2021-topics.csv'
list_of_topics_priority='sample-data/input/isca2021-topics-priority.csv'
result_of_paper_topics_assigned='sample-data/output/isca2021-papers-topics-assigned.csv'

#%% Load the paper list from HotCRP
papers_topics_df = pd.read_csv(list_of_papers_topics)

#%% load topics priority list
topics_priority_df = pd.read_csv(list_of_topics_priority)

#%%  sort topics by priority
topics_priority_df = topics_priority_df.sort_values('priority').reset_index()

#%%  Group the Paper List based on topic priority
result=papers_topics_df.drop_duplicates(subset = ['paper']).reset_index()[['paper','title']]
result['topic']=papers_topics_df.groupby('paper')['topic'].apply(lambda x: sorted(list(x), key=lambda y: topics_priority_df['topics'].to_list().index(y))[0]).reset_index()['topic']

#%% Save the result to CSV
result.to_csv(result_of_paper_topics_assigned,index=False)

# Display statistics
result[['title','topic']].groupby(['topic']).agg(['count'])
# %%
