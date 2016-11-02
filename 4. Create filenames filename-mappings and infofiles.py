
# coding: utf-8

# In[1]:

import pandas as pd
import os


# In[ ]:

def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text


# In[2]:

mexiko = pd.read_excel("excel-export.xls",sheetname="Mexiko")
mexiko_arkiv = pd.read_excel("excel-export.xls",sheetname="Mexiko-Arkiv")
cypern = pd.read_excel("excel-export.xls", sheetname="Cypern")


# In[4]:

cypern.columns


# In[ ]:

it_converters = {"Folder":strip,"Filename":strip,"Nome foto":strip,"Anno":strip,"Luogo":strip,"Nome monumento":strip,"Descrizione":strip,"Nome autore":strip}


# In[1]:

def save_filename_to_filename_file(filname_file, filename):
    """Create a file mapping original filenames and their folders with new
    Commons filenames according to <Task X on Phabricator>"""
    folder = row["Folder"]
    file = row["Filename"]
    # Filename: <Filename_1_clean>_-_DecArch_-_<Folder_#>-<Filename_0_clean>.<ext>
    
    #print("filename: {}".format(filename))
    filenames_file.write("{}|{}|{}\n".format(row["Folder"],row["Filename"],filename))


# In[ ]:

filenames_file = open("./filenames_mapping.csv","w")
filenames_file.write("Folder|Original|Commons\n")


# Infobox mapping is available on [Phabricator](https://phabricator.wikimedia.org/T144485)
# 
# # Cypern-samlingen

# In[ ]:

filenames_dict = {}
for index, row in cypern.iterrows():
    

