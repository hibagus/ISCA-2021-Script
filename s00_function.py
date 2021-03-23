# Project: ISCA 2021 Script
# Filename: s00_function.py
# Date: March 16, 2021
# Author: Bagus Hanindhito (hanindhito[at]bagus[dot]my[dot]id)
# Title: Python Function File for ISCA 2021 Script
# Description:
## This script contains callable functions used by other Python scripts.
## You don't need to run this script since it will be called by other Python scripts.

#%% Import some libraries that are needed
import urllib.request
import json
import unidecode
import os
from fuzzywuzzy import fuzz
import xmltodict
import hashlib

#%% Function to Retrieve DBLP Person ID
## This function is used to retrieve DBLP Person ID using DBLP API based on Person Name
## Since there is a possibility that multiple people own same name, the function will return
## JSON file that contains all possible people.
def request_author_key(firstname, lastname, retry_num=2, outputtype='json'):
    if not os.path.exists('.cache'):
        os.makedirs('.cache')
    if not os.path.exists('.cache/person_id'):
        os.makedirs('.cache/person_id')
    # Define the DBLP API URL to retrieve the autor
    api_url = 'https://dblp.org/search/author/api?'
    # Define the format, currently it is json
    format_url= ('format=%s' % (outputtype))
    # If firstname consists of multiple words, then use only the first word
    req_firstname = firstname.split()[0]
    # lastname is ready to use
    req_lastname = lastname
    # Construct the query, please refer to https://dblp.org/faq/1474589.html
    req_query = ('q=$%s$+$%s$' % (urllib.parse.quote(req_firstname), urllib.parse.quote(req_lastname)))
    req_url = ('%s%s&%s' % (api_url, req_query, format_url))
    req_hash= hashlib.sha256(req_query.encode('utf-8')).hexdigest()

    # Check if the request is already cached:
    if os.path.isfile('.cache/person_id/'+req_hash+'.json'):
        with open('.cache/person_id/'+req_hash+'.json', 'r') as fp:
            json_dict = json.load(fp)
    else:
        # Try to fetch author data using DBLP API
        resource = urllib.request.urlopen(req_url)
        # Get the JSON data
        raw_str = resource.read()
        # Sanitize string
        decoded_string = raw_str.decode('utf-8')
        #decoded_string = unidecode.unidecode(html.unescape(raw_str.decode('utf-8')))
        # Convert JSON to Python Dictionary
        #try:
        json_dict = json.loads(decoded_string)
        # cache
        with open('.cache/person_id/'+req_hash+'.json', 'w') as fp:
            json.dump(json_dict, fp)
        #except:
        #    print(raw_str)
    return json_dict

#%% Function to merge affiliation
# DBLP may return multiple affiliations. This function will merge all affiliation into a list of string
def merge_affiliation(pc_json, entrynum):
    affiliation_dblp_list = []
    if 'notes' in pc_json['result']['hits']['hit'][entrynum]['info']:
        if 'note' in pc_json['result']['hits']['hit'][entrynum]['info']['notes']:
            if isinstance(pc_json['result']['hits']['hit'][entrynum]['info']['notes']['note'], dict):
                pc_json['result']['hits']['hit'][entrynum]['info']['notes']['note'] = [pc_json['result']['hits']['hit'][entrynum]['info']['notes']['note']]
            number_of_notes = len(pc_json['result']['hits']['hit'][entrynum]['info']['notes']['note'])
            if(number_of_notes!=0):
                for note_dict in pc_json['result']['hits']['hit'][entrynum]['info']['notes']['note']:
                    if (note_dict['@type'] == 'affiliation'):
                        affiliation_dblp_list.append(note_dict['text'])
    return affiliation_dblp_list

#%% Function to Convert JSON returned by DBLP to Python Dictionary
# This function converts each possible person with a given name returned by DBLP to Python Dictionary
def convert_to_dict(pc_member, pc_json):
    pc_member_dblp_list = []
    number_of_hits = int(pc_json['result']['hits']['@sent'])
    if(number_of_hits==0):
        affiliation_dblp_list = []
        pc_member_dblp_dict = \
        {
            "full_name"        : pc_member['full'],
            "first_name"       : pc_member['first'],
            "last_name"        : pc_member['last'],
            "affiliation"      : pc_member['affiliation'],
            "email"            : pc_member['email'],
            "isUnique"         : 0,
            "isError"          : 1,
            "entrynum"         : 0,
            "name_confidence"  : 0,
            "affl_confidence"  : 0,
            "name_dblp"        : '',
            "url_dblp"         : '',
            "affiliation_dblp" : affiliation_dblp_list
        }
        pc_member_dblp_list.append(pc_member_dblp_dict)
    else:
        if (number_of_hits==1):
            isUnique=1
        else:
            isUnique=0
        # iterate over each entry in JSON file
        for entrynum in range(0, number_of_hits):
            # use to merge multiple affiliation (if any)
            affiliation_dblp_list = merge_affiliation(pc_json, entrynum) 
            pc_member_dblp_dict = \
            {
                "full_name"        : pc_member['full'],
                "first_name"       : pc_member['first'],
                "last_name"        : pc_member['last'],
                "affiliation"      : pc_member['affiliation'],
                "email"            : pc_member['email'],
                "isUnique"         : isUnique,
                "isError"          : 0,
                "entrynum"         : entrynum,
                "name_confidence"  : 0,
                "affl_confidence"  : 0,
                "name_dblp"        : pc_json['result']['hits']['hit'][entrynum]['info']['author'],
                "url_dblp"         : pc_json['result']['hits']['hit'][entrynum]['info']['url'],
                "affiliation_dblp" : affiliation_dblp_list
            }
            pc_member_dblp_list.append(pc_member_dblp_dict)           
    return pc_member_dblp_list

#%% Function to Filter the returned list of people based on the name.
# This filter is not perfect. It uses fuzzy match to the string.
def filter_name(pc_member_dblp_list, confidence_threshold=90):
    original_list_length = len(pc_member_dblp_list)
    # only filter if multiple entries are found
    if(original_list_length>1): 
        pc_member_dblp_list_filtered = []
        for pc_member_dict in pc_member_dblp_list:
            string_1 = pc_member_dict['full_name'].lower()
            string_2 = pc_member_dict['name_dblp'].lower()
            confidence_level = fuzz.ratio(string_1, string_2)
            if(confidence_level>=confidence_threshold):
                pc_member_dict['name_confidence'] = confidence_level
                pc_member_dblp_list_filtered.append(pc_member_dict)
                #print('%s vs %s == %d' % (string_1, string_2, confidence_level))
    else:
        pc_member_dblp_list_filtered = pc_member_dblp_list
    return pc_member_dblp_list_filtered

#%% Function to Filter the returned list of people based on the affiliation.
# This filter is not perfect. It uses fuzzy match to the string.
# Use this filter after filtering based on the name
def filter_affiliation(pc_member_dblp_list, confidence_threshold=80):
    original_list_length = len(pc_member_dblp_list)
    # only filter if multiple entries are found
    if(original_list_length>1): 
        pc_member_dblp_list_filtered = []
        for pc_member_dict in pc_member_dblp_list:
            max_confidence = 0
            string_1 = pc_member_dict['affiliation'].lower()
            for affiliation_dblp in pc_member_dict['affiliation_dblp']:
                string_2 = affiliation_dblp.lower()
                confidence_level = fuzz.partial_ratio(string_1, string_2)
                max_confidence = max(max_confidence, confidence_level)
            if(max_confidence>=confidence_threshold):
                pc_member_dict['affl_confidence'] = max_confidence 
                pc_member_dblp_list_filtered.append(pc_member_dict)
                #print('%s vs %s == %d' % (string_1, string_2, confidence_level))
            # inconclusive filtering since affiliation information is not available on DBLP
            if(len(pc_member_dict['affiliation_dblp'])==0):
                pc_member_dblp_list_filtered.append(pc_member_dict)
    else:
        pc_member_dblp_list_filtered = pc_member_dblp_list
    return pc_member_dblp_list_filtered


#%% Function to retrieve PC member's all publications from DBLP
def request_publication_list(dblp_link, retry_num=2, outputtype='xml'):
    if not os.path.exists('.cache'):
        os.makedirs('.cache')
    if not os.path.exists('.cache/pub_id'):
        os.makedirs('.cache/pub_id')
    # Construct the query, please refer to https://dblp.org/faq/1474589.html
    req_url = ('%s.xml' % (dblp_link))
    req_hash= hashlib.sha256(req_url.encode('utf-8')).hexdigest()
    # Cache
    if os.path.isfile('.cache/pub_id/'+req_hash):
        with open('.cache/pub_id/'+req_hash, 'r') as fp:
            xml_dict = xmltodict.parse(fp.read(), dict_constructor=dict)
    else:
        # Try to fetch author data using DBLP API
        resource = urllib.request.urlopen(req_url)
        # Get the XML data
        raw_str = resource.read()
        # Sanitize string
        decoded_string = raw_str.decode('utf-8')
        # Convert XML to Python Dictionary
        xml_dict = xmltodict.parse(decoded_string, dict_constructor=dict)
        with open('.cache/pub_id/'+req_hash, 'w') as fp:
            fp.write(xmltodict.unparse(xml_dict))
    return xml_dict

#%% Function to retrieve PC member's all publications from DBLP
def request_affiliation(dblp_link, retry_num=2, outputtype='xml'):
    if not os.path.exists('.cache'):
        os.makedirs('.cache')
    if not os.path.exists('.cache/pub_id'):
        os.makedirs('.cache/pub_id')
    # Construct the query, please refer to https://dblp.org/faq/1474589.html
    req_url = ('%s.xml' % (dblp_link))
    req_hash= hashlib.sha256(req_url.encode('utf-8')).hexdigest()
    # Try to fetch author data using DBLP API
    try:
        if os.path.isfile('.cache/pub_id/'+req_hash):
            with open('.cache/pub_id/'+req_hash, 'r') as fp:
                xml_dict = xmltodict.parse(fp.read(), dict_constructor=dict)
        else:
            resource = urllib.request.urlopen(req_url)
            # Get the JSON data
            raw_str = resource.read()
            # Sanitize string
            decoded_string = raw_str.decode('utf-8')
            # Convert XML to Python Dictionary
            xml_dict = xmltodict.parse(decoded_string, dict_constructor=dict)
            with open('.cache/pub_id/'+req_hash, 'w') as fp:
                fp.write(xmltodict.unparse(xml_dict))

        affiliation_list=[]
        affiliation_str = ''
        try:
            notes = xml_dict['dblpperson']['person']['note']
            if(isinstance(notes,dict)):
                notes = [notes]
            for note in notes:
                if (note['@type']=='affiliation'):
                    affiliation_list.append(note['#text'])
            affiliation_str=','.join(affiliation_list)
            affiliation_str= affiliation_str + ' <DBLP>'
        except:
            affiliation_str = 'NONE <DBLP>'
    except:
        affiliation_str = 'NONE <DBLP>'
    return affiliation_str