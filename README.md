# ISCA-2021-Script


<br />
<p align="center">

  <h3 align="center">ISCA 2021 Script</h3>

  <p align="center">
    A collection of redistributable Python script to help organize ISCA 2021 </br>
    (The 48th International Symposium on Computer Architecture)
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#introduction">Introduction</a>
      <ul>
        <li><a href="#description">Description</a></li>
        <li><a href="#scripts">Scripts</a></li>
        <li><a href="#authors">Authors</a></li>
        <li><a href="#acknowledgements">Credits</a></li>
        <li><a href="#license">License</a></li>
        <li><a href="#contributing">Contributing</a></li>
        <li><a href="#citing">Citing</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#recommendation">Recommendation</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#sample-data">Sample Data</a></li>
      </ul>
    </li>
    <li>
      <a href="#conflict-of-interest-crosscheck">Conflict of Interest Crosscheck</a>
      <ul>
        <li><a href="#getting-dblp-person-id">Getting DBLP Person ID</a></li>
        <li><a href="#getting-dblp-coauthors">Getting DBLP Coauthors</a></li>
        <li><a href="#merge-dblp-conflict-to-hotcrp">Merge DBLP Conflict to HotCRP</a></li>
      </ul>
    </li>
    <li>
      <a href="#paper-topic-assignment">Paper Topic Assignment</a>
    </li>
    <li>
      <a href="#paper-discussion-scheduler">Paper Discussion Scheduler</a>
    </li>
    <li>
      <a href="#zoom-meeting-config-generator">Zoom Meeting Config Generator</a>
    </li>
  </ol>
</details>



<!-- INTRODUCTION -->
## Introduction

### Description
This repository contains some Python scripts that we used to help us manage the ISCA 2021 conference. We use the scripts to manage the following things for ISCA 2021 Conference:

* Conflict of Interest Crosscheck

  We use DBLP to crosscheck the conflict list entered by each PC. The scripts will try to match each PC name, fetch DBLP profile, and gather all of the co-authors. The scripts are not yet perfect; there are still some manual works to do.

* Paper Topic Assignment

  The paper topic assignment is used to prioritize paper topic to help with reviewer assignment.

* Paper Discussion Scheduler

  Based on the availability of its PC reviewer, the script try to find possible window for paper discussion during PC meeting. The script is not perfect yet, so some manual adjustment maybe required. The output of the scripts can be used as starting point. 

* Zoom Meeting Config Generator

  Based on the conflict information of each paper, the script generate the list of attendance for conflict room and discussion room to separate the meeting participant during PC meeting. 

Our conference uses HotCRP to manage the submission, and thus our scripts are created to be compatible with the HotCRP v3.0b1. Unfortunately, as HotCRP is updated regularly, the scripts may not be compatible with future version of HotCRP. We recommend that you save your HotCRP states and configurations before making any changes or uploading any CSV files generated by these scripts.

We use the email address registered with HotCRP to uniquelly identify each person. Therefore, it is recommended that you collect the HotCRP email address everytime you create a form to collect information outside HotCRP (e..g, meeting availability, zoom email address, etc.).

### Scripts
There are xx Python scripts provided in this repository.
* 00_function.py
  This script contains all of the functions that will be called by other script. You don't need to run this script unless you need to debug its functionality.

* 01_pcname_to_dblp_person_id.py
  This script is used to find DBLP person id based on the given first name and last name.


### Authors

* Bagus Hanindhito, PhD Student
* Lizy Kurian John, PC Chair of ISCA 2021

Laboratory for Computer Architecture, Department of Electrical and Computer Engineering </br>
The University of Texas at Austin, Austin, The United States of America

### Acknowledgements
We would like to thank the following persons that give us ideas during the development of these scripts.
* Mario Drumond for PC Chair Kit (https://github.com/mdrumond/pc-chair-kit)
* Emery Berger for ASPLOS-21 scripts (https://github.com/emeryberger/ASPLOS-2021)
* Othneil Drew for README Template (https://github.com/othneildrew/Best-README-Template)

### License

These scripts are licensed under GNU General Public License v2.0. 
Feel free to modify, use, and distribute these scripts. 

### Contributing
The scripts may not suite your needs and may also contain some bugs and imperfections.
We encourage users to actively participating these scripts and add more features into them.
Feel free to open a pull request should you want to add new features to the scripts or just do a little bug fixing.
Every contribution will definitely be helpful for our communities and future conferences. 

### Citing
If they are useful for you and your works, we would be happy if you could cite us.

<!-- GETTING STARTED -->
## Getting Started

Please follow the steps below to obtain the scripts and run them locally at your own machine.

### Prerequisites

The scripts are developed under Ubuntu 20.04.1 LTS running on Windows Subsystem Linux 2 (WSL2). </br>
We use Python 3.6.12 64-bit with the following packages installed:
* pandas: 1.1.4
* numpy: 1.19.4
* tqdm: 4.51.0
* fuzzywuzzy: 0.18.0
* urllib: 1.25.11
* json5: 0.9.5
* jsonschema: 3.2.0
* Unidecode: 1.1.1
* xmltodict: 0.12.0

### Recommendation

#### IDE/Editor
The scripts are compatible with Visual Studio Code with Python plugin (v2021.2.633441544) and Jupyter Extension (v2021.2.576440691) for Visual Studio Code. It is recommended to use Visual Studio Code with these plugins to run the script cell-by-cell (just like in Jupyter Notebook). This makes it easier to debug the script should there is any error. Visual Studio Code also has a reliable interface with Windows Subsystem Linux 2 which is very useful if you use Windows Subsystem Linux 2 as your development environment.

![VSCode Compatible Feature](img/IDEVScode.png)

1. Interface seamlessly with Windows Subsystem Linux 2.
2. Integration with Git version control system.
3. Integration with Conda virtual environment for Python.
4. Interactive Shell.
5. Text editor with syntax highlighting.
6. Cell-based code execution.
7. Interactive variable inspection.
8. Interactive output shell.

#### Virtual Environment
We recommend to use virtual environment (e.g., Anaconda) to install the required packages to avoid version conflict.

#### CSV Editor
We recommend to use CSV Editor that can support UTF-8 encoding to avoid any miss-interpreted characters. We use Microsoft Office Excel 2019 to edit CSV downloaded from HotCRP and to prepare CSV to be uploaded to HotCRP.

1. Load CSV to Excel

    ![Import CSV To Excel](img/ImportCSV.png)

    Please do not directly open the CSV file using Excel since it will be wrongly decoded. Open a blank Excel workbook and go to ``Data`` on the tab menu (1). Select ``Get Data`` (2), ``From File`` (3), ``From Text/CSV`` (4). An open file dialog will appear to let you choose which CSV file you want to load. 
    
    Then, data preview dialog will open as shown above. Please select ``File Origin`` as ``65001: Unicode (UTF-8)`` (5) and ``Delimiter`` as ``Comma`` (6). Finally, click ``Load`` (7) to load the CSV into a worksheet. Now, you can manipulate the CSV data using Excel.

2. Save CSV from Excel

    ![Export CSV From Excel](img/ExportCSV.png)

    To save the data from Excel (.xlsx) to CSV, please select ``File`` (not shown, it should be located on the top left), then ``Save as`` (1). Select ``Browse`` (2) to find the folder where you want to save the CSV into. Then, select ``CSV UTF-8 (Comma delimited) (*.csv)`` on the ``Save as type:`` (3) dropdown box. Finally, click ``Save`` (4). This CSV file can now be uploaded into HotCRP or can be used as input to our Python scripts. 

### Installation

1. Clone the github repository
   ```sh
   git clone https://github.com/hibagus/ISCA-2021-Script.git
   ```

2. Prepare and activate the virtual environment (We use Anaconda).
   ```sh
   conda create -n COI_Redistributable python=3.6.12
   conda activate COI_Redistributable
   ```

3. Install required packages
   ```sh
   pip install -r requirements.txt
   ```

### Sample Data
We provide some sample CSV data inside the directory ``sample-data`` to make you easier to use these scripts. 

<!-- CONFLICT OF INTEREST CROSSCHECK -->
## Conflict of Interest Crosscheck
This section is used to do a Conflict of Interest Crosscheck between the conflict list entered by each PC member in HotCRP and the list of co-authors from all of the publications of each PC member listed in DBLP. It consists of three steps as follows.

### Getting DBLP Person ID
* Script
  
  Use script ``s01_pcname_to_dblp_person_id.py`` to accomplish this task.

* Input
  
  The input to this script is a CSV file contains the PC info from HotCRP. To obtain this CSV file, go to the ``Users`` on the side-panel of your HotCRP conference page which will bring you to the list of users registered. In the ``User Selection`` on the top, select ``Program committee`` and click ``Go`` which will display all PC members. Then, go to the bottom of the page, click ``select all xxx, then Download:`` and choose ``PC info``. Click ``Go`` to download the CSV file.

  The header of this CSV file is shown below.
  ```sh
  first,last,email,affiliation,country,roles,tags,collaborators,follow,"topic: ...","topic: ...",...
  ```

* Output
  
  The script will output a CSV file that contains several fields, including the URL to the DBLP database. The header of this CSV file is shown below. Each field will be explained afterwards.
  ```sh
  full_name,first_name,last_name,affiliation,email,isUnique,isError,entrynum,name_confidence,affl_confidence,name_dblp,url_dblp,affiliation_dblp
  ```

    * ``isUnique`` 
    
      Indicates that the entry for a particular PC member is unique (i.e., no homonym) if it has value of ``1``. If it is not unique, then you will need to manually select the correct entry for a particular PC member. We suggest that you check both unique and not unique entries if you have time.

    * ``isError``

      Indicates that the script is unable to fetch the URL to the DBLP database. It may be because the person does not exist in DBLP database. You may need to manually check the entry that has ``isError`` value of ``1``.

    * ``entrynum``

      Indicates the number of entry for a particular PC member. If there is no homonym, the entry number should only be ``0``. Anything larger than ``0`` indicates that there are some homonym for a particular PC member that need to be solved. 

    * ``name_confidence``
    
      Indicates the fuzzymatch filtering confidence based on the first name and last name. The script tries to remove all non-relevant entries of homonym for each PC member. If the confidence level is lower than a predefined threshold, the entries will be removed, otherwise be kept. It is up to you to define the threshold; the higher the threshold, the less homonym entries will make through the output CSV file. We recommend to keep the threshold around 80 to 90. 

    * ``affl_confidence``

      Indicates the fuzzymatch filtering confidence based on the affiliation. The script tries to remove all non-relevant entries of homonym for each PC member. If the confidence level is lower than a predefined threshold, the entries will be removed, otherwise be kept. It is up to you to define the threshold; the higher the threshold, the less homonym entries will make through the output CSV file. We recommend to keep the threshold around 80 to 90. 

    * ``name_dblp``

      Name of PC member based on the DBLP

    * ``url_dblp``

      The URL to the DBLP database.

    * ``affiliation_dblp``

      Affiliation of PC member based on the DBLP

  Please use Excel to inspect and modify the output CSV file. Follow the ``Recommendation`` above on how to import CSV into Excel with UTF-8 encoding and export CSV from Excel with UTF-8 encoding. 





First, we need to get correct DBLP Person ID for each PC member.

* []()
* []()
* []()

### Getting DBLP Coauthors

* []()
* []()
* []()

### Merge DBLP Conflict to HotCRP

* []()
* []()
* []()

<!-- PAPER TOPIC ASSIGNMENT -->
## Paper Topic Assignment

<!-- PAPER DISCUSSION SCHEDULER -->
## Paper Discussion Scheduler

<!-- ZOOM MEETING CONFIG GENERATOR -->
## Zoom Meeting Config Generator



Downloading and Extracting Packages
VScode Integration
ipython_genutils-0.2 | 27 KB     |  | 100% 
ipython-7.16.1       | 999 KB    |  | 100% 
pexpect-4.8.0        | 53 KB     |  | 100% 
decorator-4.4.2      | 12 KB     |  | 100% 
pyzmq-20.0.0         | 438 KB    |  | 100% 
traitlets-4.3.3      | 140 KB    |  | 100% 
jupyter_client-6.1.7 | 77 KB     |  | 100% 
zeromq-4.3.4         | 331 KB    |  | 100% 
parso-0.8.1          | 69 KB     |  | 100% 
jupyter_core-4.7.1   | 68 KB     |  | 100% 
prompt-toolkit-3.0.1 | 256 KB    |  | 100% 
pickleshare-0.7.5    | 13 KB     |  | 100% 
tornado-6.1          | 581 KB    |  | 100% 
backcall-0.2.0       | 13 KB     |  | 100% 
ipykernel-5.3.4      | 181 KB    |  | 100% 
pygments-2.8.1       | 703 KB    |  | 100% 
six-1.15.0           | 27 KB     |  | 100% 
python-dateutil-2.8. | 221 KB    |  | 100% 
jedi-0.17.0          | 780 KB    |  | 100% 
ptyprocess-0.7.0     | 17 KB     |  | 100

Pandas
numpy-1.19.5 
pandas-1.1.5 
pytz-2021.1

tqdm
tqdm-4.59.0

fuzzywuzzy
fuzzywuzzy-0.18.0

unidecode
unidecode-1.2.0