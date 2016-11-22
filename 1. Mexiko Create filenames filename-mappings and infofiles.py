
# coding: utf-8

# In[7]:

get_ipython().system('pip install https://github.com/lokal-profil/BatchUploadTools/tarball/0.0.1')


# In[1]:

import batchupload.helpers as helpers


# In[1]:

import pandas as pd
from collections import Counter
import os
from textblob import TextBlob
import regex
import operator
import pickle

# For bigrams creation
import nltk
from nltk import word_tokenize
from nltk.util import ngrams

mexiko = pickle.load(open("./mexiko_df_final.pickle","rb"))


# In[2]:

pd.describe_option()


# In[3]:

pd.set_option('display.max_rows', 5)
pd.set_option('max_seq_items', 10)

# Ensure this computer has got NLTK tokenizers
nltk.download()
# The metadata file on [Google Docs](https://docs.google.com/spreadsheets/d/1YXusiepersJ6_XGoUVEE0jfGh5NJs-5Rds2_l5ZbGik/edit?usp=sharing)
# 
# The collection object "Linné-Mexiko" from Etnografiska Museet is [on Carlotta](http://collections.smvk.se/carlotta-em/web/object/1460547)
# 
# A list of all the photographs is listed [on Carlotta](http://collections.smvk.se/carlotta-em/web/object/1460547/CHILDREN/9)
# 
# Here is the full search in the Database from Etnografiska Museet [in K-SAMSOK](http://www.varldskulturmuseerna.se/etnografiskamuseet/forskning-samlingar/sok-i-samlingarna1/?ksamsearchtext=mexiko+sigvald+tula&radio-group=andmatch&itemtype=samling&ksamsubmit=S%C3%B6k)

# # 0. Read in the metadata

# In[4]:

mexiko_test = pd.read_excel("excel-export.xls", sheetname="Mexiko")
mexiko_test.columns


# In[5]:

def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text
    
mexiko_converters = {"Fotonummer":strip,"Postnr":strip,"Motivord":strip,"Beskrivning":strip,"Land, foto":strip,
                     "Region, foto":strip,"Ort, foto":strip,"Etnisk grupp, avb.":strip,"Fotodatum":strip,
                    "Personnamn / fotograf":strip, "Personnamn / avbildad":strip, "Sökord":strip,
                    "Händelse / var närvarande vid":strip, "Länk":strip}

mexiko = pd.read_excel("excel-export.xls", sheetname="Mexiko", converters=mexiko_converters)


# # Inspect keywords in column "Motivord"

# In[6]:

mexiko.Motivord.value_counts()[:10]


# In[7]:

motivord_count = Counter()

for index, string in mexiko.Motivord.iteritems():
    if pd.notnull(string):
        tokens = string.split(", ")
        tokens = [token.strip() for token in tokens]
        for token in tokens:
            motivord_count[token] += 1
motivord_count.most_common(10)


# ## Add sub-collection metadata field "description"
# 
# * Add these to the final images in the infobox

# In[8]:

a_str = "1234.j.345432"


# In[9]:

a_str.partition(".")


# In[10]:

sub_desc = {"a":"Teotihuacan (241) utgrävningar, fornlämningar, invånare",
"b": "Mexiko (29) utgrävningar, fornlämningar mm",
"c": "Tula (32) landskap, miljöer, invånare, fornlämningar",
"d": "Oaxaca (54) fornlämningar, invånare, miljöer mm. Nr.1 saknas",
"e": "Teopanzolco, Xochicalco (50) fornlänningar nr.51 saknas",
"f": "Yucatan, Chichen Itza fornlämningar, landskap. Två kartonger, 352 saknas",
"g": "Yucatan, Uxmal (113) fornlämningar",
"h": "Yucatan, Sayil (9) fornlämningar",
"i": "Yucatan, Kabah (59) fornlämningar",
"j": "Yucatan, Labna (90) fornlämningar, bilresa längs landsvägen",
"k": "Yucatan, Merida (42) miljöer, invånare",
"l": "Yucatan, Mona (11) invånare, miljöer",
"m": "Yucatan, Ticul (2) boskap",
"n": "Yucatan, Dzitas (5) miljöer",
"o": "Yucatan, Villa Hermosa (14) flygfoton",
"p": "Yucatan, skilda orter (25) tågresan Vera Cruz- Mexico",
"q": "Teotihuacan (156) arkeologiska föremål"}


# In[11]:

mexiko["subcol_desc"] = 0
for index, row in mexiko.iterrows():
    #print(mexiko.loc[index,"subcol_desc"])
    for key in sub_desc:
        #print(type(row.Fotonummer))
        initial_numbers, left_dot, letter_plus_last_numbers = row.Fotonummer.partition(".")
        letter, dot, last_numbers = letter_plus_last_numbers.partition(".")
        #print(letter)
        if letter == key:
            #print("Match! index: {} letter:{} key:{} desc: {}".format(index, letter, key, sub_desc[key]))
            mexiko.loc[index, "subcol_desc"] = sub_desc[key] 
mexiko.subcol_desc.value_counts()        


# # Add wiki-formatted URL-link
# 
# * Use existing helper [template](https://commons.wikimedia.org/wiki/Template:SMVK-EM-link)
# 
# ex: http://kulturarvsdata.se/SMVK-EM/fotografi/html/2786726
# 
# {{SMVK-EM-link|foto|1461871|0713.0002}}
# 
# - param 1: fotografi
# - param 2: 2786726
# - param 3: 0307.a.0001

# In[12]:

for index, row in mexiko.iterrows():
    print(row["Länk"])
    break


# In[13]:

first, slash, id_str = "http://kulturarvsdata.se/SMVK-EM/fotografi/html/2786726".rpartition("/")
id_str


# In[14]:

for index, row in mexiko.iterrows():
    url = row["Länk"]
    #first, slash, id_str = url.rpartition("/")
    #new_url = "[" + url + " Fotonummer: " + id_str + "]"
    #mexiko.loc[index, "wiki_url"] = new_url
    
    left_side, slash, id_str = url.rpartition("/")
    template = "{{SMVK-EM-link|1=foto|2=" + id_str + "|3=" + row["Fotonummer"] + "}}"
    mexiko.loc[index, "SMVK-EM-link"] = template
    
mexiko


# In[15]:

mexiko.loc[0,"SMVK-EM-link"]


# # Create list of badly filled out meatdata for WMMX

# In[16]:

mexiko["Personnamn / avbildad"].value_counts()


# In[17]:

tot_cnt = 0
bad_keywords = ["pyramid","tempel","Ciudadela","tempelpyramid", "tempelpyramider","ruiner","fornlämningar"]
for index, row in mexiko.iterrows():
    tot_cnt += 1
    if pd.isnull(row["Ort, foto"]): 
        if pd.isnull(row["Motivord"]):
            print("Both 'Ort, foto' and 'Motivord' are empty")
        elif row["Motivord"] in bad_keywords:
            print("'Ort, foto' is empty and 'Motivord' is generic: {}".format(row["Motivord"]))
        else:
            pass
            
    elif pd.notnull(row["Ort, foto"]) and row["Motivord"] in bad_keywords:
        print("Generic 'Motivord': {} but 'Ort, foto' is: {}".format(row["Motivord"], row["Ort, foto"]))


# In[18]:

bad_keywords = ["pyramid","tempel","Ciudadela","tempelpyramid", "tempelpyramider","ruiner","fornlämningar"]

motivord_count = Counter()

for index, string in mexiko.Motivord.iteritems():
    if pd.notnull(string):
        tokens = string.split(", ")
        tokens = [token.strip() for token in tokens]
        for token in tokens:
            motivord_count[token] += 1
            
file_table = ""
tot_cnt = 0
bad_cnt = 0
problematic_cnt = 0
no_keyword = 0
no_ort = 0
generic_keyword = 0
empty_ort_and_motivord = 0
no_ort_and_generic_keyword = 0
no_desc = 0
no_desc_and_no_ort = 0
no_desc_no_motivord = 0
no_desc_no_ort_no_motivord = 0
no_desc_no_ort_generic_motivord = 0


for index, row in mexiko.iterrows():
    tot_cnt += 1
    
    # Technically bad/problematic photos
    if pd.isnull(row["Beskrivning"]): # problematic
        no_desc += 1
        problematic_cnt += 1
        
        if pd.isnull(row["Ort, foto"]): # Technically bad photos
            no_desc_and_no_ort += 1
            bad_cnt += 1
            file_table += "! " + str(bad_cnt) + "\n" 
            file_table += "| " + row["SMVK-EM-link"] + "\n"
            file_table += "| " + str(row["Beskrivning"]) + "\n"
            file_table += "| " + str(row["Ort, foto"]) + "\n"
            file_table += "| " + str(row["Motivord"]) + "\n"
            file_table += "| Both 'Description' and 'Place, photo' are empty\n"
            file_table += "|\n"
            file_table += "|\n"
            file_table += "|-\n"
            
            if pd.isnull(row["Motivord"]): # Technically bad photos
                bad_cnt += 1
                no_desc_no_ort_no_motivord += 1
                file_table += "! " + str(bad_cnt) + "\n" 
                file_table += "| " + row["SMVK-EM-link"] + "\n"
                file_table += "| " + str(row["Beskrivning"]) + "\n"
                file_table += "| " + str(row["Ort, foto"]) + "\n"
                file_table += "| " + str(row["Motivord"]) + "\n"
                file_table += "| 'Description' and 'Place, photo' and 'Motive' are empty\n"
                file_table += "|\n"
                file_table += "|\n"
                file_table += "|-\n"
            
            elif pd.notnull(row["Motivord"]): 
                motivord = row["Motivord"]
                sep_motivord = [token.strip() for token in motivord.split(",")]
                for token in sep_motivord:
                    if token in bad_keywords:
                        generic_keyword += 1
                        #print("{} depicts a pyramid, a tempel or ciudadela!".format(row["Motivord"]))
                        diff = set(sep_motivord) - set(bad_keywords)
                        #print(diff)
                        if diff == set(): # Technically bad photos
                            bad_cnt += 1
                            no_desc_no_ort_generic_motivord += 1
                            file_table += "! " + str(bad_cnt) + "\n" 
                            file_table += "| " + row["SMVK-EM-link"] + "\n"
                            file_table += "| " + str(row["Beskrivning"]) + "\n"
                            file_table += "| " + str(row["Ort, foto"]) + "\n"
                            file_table += "| " + str(row["Motivord"]) + "\n"
                            file_table += "| Both 'Description' and 'Place, photo' are empty and 'Motive' is generic\n"
                            file_table += "|\n"
                            file_table += "|\n"
                            file_table += "|-\n"
        
        elif pd.isnull(row["Motivord"]): # problematic "Beskrivning might still be filled in"
            no_desc_no_motivord += 1
            problematic_cnt += 1
            
                
    # Technically bad photos    
    if pd.isnull(row["Ort, foto"]) and pd.isnull(row["Motivord"]):
        problematic_cnt += 1
        empty_ort_and_motivord += 1
        # file_table += "! " + str(bad_cnt) + "\n" 
        # file_table += "| " + row["SMVK-EM-link"] + "\n"
        # file_table += "| " + str(row["Region, foto"]) + "\n"
        # file_table += "| " + str(row["Ort, foto"]) + "\n"
        # file_table += "| " + str(row["Motivord"]) + "\n"
        # file_table += "| Both 'Motivord' and 'Ort, foto' are empty\n"
        # file_table += "|\n"
        # file_table += "|\n"
        # file_table += "|-\n"
        
    elif pd.isnull(row["Ort, foto"]) and pd.notnull(row["Motivord"]):
        
        if pd.isnull(row["Ort, foto"]) and pd.notnull(row["Motivord"]) in bad_keywords:
            motivord = row["Motivord"]
            sep_motivord = [token.strip() for token in motivord.split(",")]
            for token in sep_motivord:
                if token in bad_keywords:
                    generic_keyword += 1
                    #print("{} depicts a pyramid, a tempel or ciudadela!".format(row["Motivord"]))
                    diff = set(sep_motivord) - set(bad_keywords)
                    #print(diff)
                    if diff == set():
                        # bad_cnt += 1
                        problematic_cnt += 1
                        no_ort_and_generic_keyword += 1
                        # file_table += "! " + str(bad_cnt) + "\n" 
                        # file_table += "| " + row["SMVK-EM-link"] + "\n"
                        # file_table += "| " + str(row["Region, foto"]) + "\n"
                        # file_table += "| " + str(row["Ort, foto"]) + "\n"
                        # file_table += "| " + str(row["Motivord"]) + "\n"
                        # file_table += "| No 'Ort, foto' and 'Motivord' is generic\n"
                        # file_table += "|\n"
                        # file_table += "|\n"
                        # file_table += "|-\n"
        else:
            problematic_cnt += 1
            no_ort += 1
            # file_table += "! " + str(bad_cnt) + "\n" 
            # file_table += "| " + row["SMVK-EM-link"] + "\n"
            # file_table += "| " + str(row["Region, foto"]) + "\n"
            # file_table += "| " + str(row["Ort, foto"]) + "\n"
            # file_table += "| " + str(row["Motivord"]) + "\n"
            # file_table += "| No 'Ort, foto'\n"
            # file_table += "|\n"
            # file_table += "|\n"
            # file_table += "|-\n"
                        
    
    elif pd.isnull(row["Ort, foto"]) and pd.notnull(row["Motivord"]) in bad_keywords:
        # bad_cnt += 1
        problematic_cnt += 1
        no_ort_and_generic_keyword += 1
        # file_table += "! " + str(bad_cnt) + "\n" 
        # file_table += "| " + row["SMVK-EM-link"] + "\n"
        # file_table += "| " + str(row["Region, foto"]) + "\n"
        # file_table += "| " + str(row["Ort, foto"]) + "\n"
        # file_table += "| " + str(row["Motivord"]) + "\n"
        # file_table += "| No 'Ort, foto' and 'Motivord' is generic\n"
        # file_table += "|\n"
        # file_table += "|\n"
        # file_table += "|-\n" 
        
    else:
    
        if pd.isnull(row["Motivord"]) and pd.notnull(row["Ort, foto"]):
            # bad_cnt += 1 # Ort, foto + person, avbildad?
            no_keyword += 1
            problematic_cnt +=1
            # file_table += "! " + str(bad_cnt) + "\n" 
            # file_table += "| " + row["SMVK-EM-link"] + "\n"
            # file_table += "| " + str(row["Region, foto"]) + "\n"
            # file_table += "| " + str(row["Ort, foto"]) + "\n"
            # file_table += "| " + str(row["Motivord"]) + "\n"
            # file_table += "| No 'motivord'\n"
            # file_table += "|\n"
            # file_table += "|\n"
            # file_table += "|-\n"
    
        elif pd.notnull(row["Motivord"]):
            motivord = row["Motivord"]
            sep_motivord = [token.strip() for token in motivord.split(",")]
            for token in sep_motivord:
                if token in bad_keywords:
                    generic_keyword += 1
                    #print("{} depicts a pyramid, a tempel or ciudadela!".format(row["Motivord"]))
                    diff = set(sep_motivord) - set(bad_keywords)
                    #print(diff)
                    if diff == set():
                        # bad_cnt += 1
                        problematic_cnt += 1
                        # file_table += "! " + str(bad_cnt) + "\n" 
                        # file_table += "| " + row["SMVK-EM-link"] + "\n"
                        # file_table += "| " + str(row["Region, foto"]) + "\n"
                        # file_table += "| " + str(row["Ort, foto"]) + "\n"
                        # file_table += "| " + str(row["Motivord"]) + "\n"
                        # file_table += "| Motivord' is generic'\n"
                        # file_table += "|\n"
                        # file_table += "|\n"
                        # file_table += "|-\n"
                                                        
            

file_table += "|}"

table_header = """{| class="wikitable sortable\n"""
table_header += "|+ Fotos with bad metadata (" + str(bad_cnt) + "/" + str(tot_cnt) + ") needing manual tagging\n"
table_header += """|-
! number
! file_url
! region
! place
! why_bad? 
! Commons Cat(-s separated by comma)
! Wikidata item (-s separated by comma)
|-
"""
full_table = table_header + file_table

print("== Data Quality Statistics ==")
print()
print("Total number of photos in batch: '''{}'''".format(tot_cnt))
print()
print("=== Technically bad photos (below): '''{}''' ===".format(bad_cnt))
print("Description and Ort, foto are empty: '''{}'''".format(no_desc_and_no_ort))
print()
print("Description, Motivord and Ort, foto are empty: '''{}'''".format(no_desc_no_ort_no_motivord))
print()
print("Description and Ort, foto are empty and Motivord is generic: '''{}'''".format(no_desc_no_ort_generic_motivord))
print()
print("=== Problematic photos (in a separate wikitable): ===")
print("Description and motivord are empty: '''{}'''".format(no_desc_no_motivord))
print()
print()
print("No 'Description/Beskrivning': '''{}'''".format(no_desc))
print()
print("Both 'Motivord' and 'Ort, foto' are empty: '''{}'''".format(empty_ort_and_motivord))
print()
print("No 'motivord': '''{}'''".format(no_keyword))
print()
print("'Motivord' is generic: '''{}'''".format(generic_keyword))
print()
print("No 'Ort, foto': '''{}'''".format(pd.isnull(mexiko["Ort, foto"]).value_counts()[1]))
print()
print("No 'Ort, foto' and 'Motivord' is generic: '''{}'''".format(no_ort_and_generic_keyword))
print()



print("== Generic keywords: ==")
for token in bad_keywords:
    print("* " + token + ", " + str(motivord_count[token]), end="\n")
print()

print("'nan' means empty in the table")
print() 
print(full_table)


# Tips: Om det bara finns generiskt motivord och det finns Ort, foto OCH Motivord:
# Finns Commons-kategori som heter typ Pyramids in Techuacan?
# pröva Motivord

# In[19]:

mexiko.to_pickle("./mexiko_df_final.pickle")


# In[3]:

mexiko = pickle.load(open("./mexiko_df_final.pickle","rb"))
mexiko


# # Statistics: Not OK_to_upload

# In[6]:

bad_keywords = ["pyramid","tempel","Ciudadela","tempelpyramid", "tempelpyramider","ruiner","fornlämningar"]
no_ort = 0
no_ort_and_generic_motivord = 0
no_ort_no_motivord = 0

for index, row in mexiko.iterrows():
    if pd.isnull(row["Beskrivning"]) and pd.isnull(row["Ort, foto"]):
        no_ort += 1
        if pd.notnull(row["Motivord"]):
            sep_motivord = [token.strip() for token in row["Motivord"].split(",")]
            diff = set(sep_motivord) - set(bad_keywords)
            if diff == set(): # Technically bad photos
                no_ort_and_generic_motivord += 1
        elif pd.isnull(row["Motivord"]):
            no_ort_no_motivord += 1
                
print("no ort: {}\nno ort plus generic motivord: {}\nno ort, no motivord: {}".format(no_ort, no_ort_and_generic_motivord, no_ort_no_motivord))


# # Inspect that unique filenames gets created

# In[21]:

# Field "Motivord", "Beskrivning" and "Ort, foto"
non_id_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Motivord"]) and pd.notnull(row["Beskrivning"]) and pd.notnull(row["Ort, foto"]):
        motivord = row["Motivord"]
        beskrivning = row["Beskrivning"]
        ort = row["Ort, foto"]
        tri_combo = motivord + " " + beskrivning + " " + ort
        non_id_names.add(tri_combo)
        
print(len(non_id_names))
list(non_id_names)[:10]


# In[ ]:




# In[22]:

# Field "Beskrivning" and "Ort, foto"
non_id_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Beskrivning"]) and pd.notnull(row["Ort, foto"]):
        non_id_names.add(str(row["Beskrivning"]) + str(row["Ort, foto"]) )
print(len(non_id_names))


# In[23]:

# Field "Beskrivning" only
non_id_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Beskrivning"]):
        non_id_names.add(row["Beskrivning"])
print(len(non_id_names))


# # Collect keyword mappings and create dataframes
# 
# Keywords for the Mexiko dataset are published as mappingtables on [Commons](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Mexiko_keywords).

# In[ ]:




# # Create filenames and filenames-mapping file

# In[24]:

fname1 = "0307.a.0001.tif"
fname2 = "0307.a.0002.a.tif"
print("fname1: {}".format(fname1.split(".")))
print("fname2: {}".format(fname2.split(".")))
print(fname2[-1].isalpha())


# In[25]:

def append_new_filename_to_filenames_mapping_file(filenames_file, old_filename, new_filename):
    filnames_file.write("{}|{}\n".format(old_filename, new_filename))
    return 


# In[172]:

mexiko = pickle.load(open("./mexiko_df_final.pickle","rb"))
print("Loaded DataFrame from 'mexiko_df_final.pickle' OK")
    
def create_new_filename(row):
    import pickle
    
    # Remove the extension from filename_1_clean
    fname_parts = row["Fotonummer"].split(".")
    
    def create_id_str(fname_parts):
        id_str = None
        if len(fname_parts) == 3 and fname_parts[-1]:
            id_str = fname_parts[2]
        elif len(fname_parts) == 4 and fname_parts[-1].isalpha():
            id_str = fname_parts[2] + "." + fname_parts[3]
        else:
            print("Something wrong when creating ext and id_str!")
            print("fname_parts: {}".format(fname_parts))
            return
                  #return print("ext: {}\nid_str: {}".format(ext, id_str))
        return id_str # skip extension, assume all extensions are .tif
    
    def construct_new_name_from_dataframe(row, id_str):
        ext = ".tif"
        new_fname = ""
        if pd.notnull(row["Beskrivning"]):
            new_fname += row["Beskrivning"]
            new_fname += "_-_"
            new_fname += "SMVK-EM"
            new_fname += "_-_"
            new_fname += id_str
            
            new_fname += ext
            
        elif pd.isnull(row["Beskrivning"]) and pd.notnull(row["Ort, foto"]) and pd.notnull(row["Motivord"]):
            new_fname += row["Ort, foto"]
            new_fname += " "
            new_fname += row["Motivord"]
            new_fname += "_-_"
            new_fname += "SMVK-EM"
            new_fname += "_-_"
            new_fname += id_str
            new_fname += ext
            
        else:
            print("Fotonummer {} could not be created a new filename for".format(row["Fotonummer"]))
        return new_fname
    
    def append_new_filename_to_filenames_mapping_file(filenames_file, old_filename, new_filename):
        filnames_file.write("{}|{}\n".format(old_filename, new_filename))
        return 
    
    id_str = create_id_str(fname_parts)
    
    if id_str:
        fname = construct_new_name_from_dataframe(row, id_str)
        return fname
    else:
        print("ops!")


# In[189]:

def create_infofiles(row):
    bad_keywords = ["pyramid","tempel","Ciudadela","tempelpyramid", "tempelpyramider","ruiner","fornlämningar"]
    outpath = "./infofiles/"
    infotext = "{{photograph\n"
    
    new_filename = create_new_filename(row)
    
    lacking_description = False
    lacking_photographer = False
    personnamn_not_even = False
    OK_to_upload = True
    
    
    if pd.notnull(row["Personnamn / fotograf"]):
        if "Apenes" in row["Personnamn / fotograf"]:
            infotext +="|photographer       =  " + "[[q:Q5959424|Sigvald Linné]]/Ola Apenes\n"
        else:
            infotext += "|photographer       =  " + row["Personnamn / fotograf"].strip() + "\n"
    if pd.isnull(row["Personnamn / fotograf"]):
        infotext += "|photographer       =  \n"
        lacking_photographer = True
    
    infotext += "|title              = \n"
    
    if pd.notnull(row["Beskrivning"]):
        if pd.notnull(row["Ort, foto"]) and pd.notnull(row["Motivord"]):
            infotext += "|description       = {{sv|" + row["Beskrivning"] + " " + row["Ort, foto"] + " " + row["Motivord"] + "}}\n"
        elif pd.notnull(row["Ort, foto"]) and pd.isnull(row["Motivord"]):
            infotext += "|description       = {{sv|" + row["Beskrivning"] + " " + row["Ort, foto"] + "}}\n"
        elif pd.isnull(row["Ort, foto"]) and pd.notnull(row["Motivord"]):
            infotext += "|description       = {{sv|" + row["Beskrivning"] + " " + row["Motivord"] + "}}\n"
        elif pd.isnull(row["Ort, foto"]) and pd.isnull(row["Motivord"]):    
            infotext += "|description       = {{sv|" + row["Beskrivning"] + "}}\n"
    if pd.isnull(row["Beskrivning"]):
        lacking_description = True
        if pd.isnull(row["Ort, foto"]):
            OK_to_upload = False
        elif pd.notnull(row["Ort, foto"]) and pd.notnull(row["Motivord"]):
            infotext += "|description       = {{sv|" + row["Ort, foto"] + " " + row["Motivord"] + "}}\n"
        
        
    
    depicted_people = ""
    if pd.notnull(row["Personnamn / avbildad"]):
        lista = row["Personnamn / avbildad"].split(", ")
        for i, j in zip(lista[::2], lista[1::2]):
            if j + " " + i == "Sigvald Linne":
                depicted_people += "[[q:Q5959424|Sigvald Linné]] "
            else:
                depicted_people += j + i + " "
            
        infotext += "|depicted people    = " + depicted_people + "\n"
        
    if pd.notnull(row["Händelse / var närvarande vid"]):
        infotext += "|depicted place     = " + row["Händelse / var närvarande vid"] + "\n"
    
    if pd.notnull(row["Fotodatum"]):    
        infotext += "|date               = " + row["Fotodatum"] + "\n"

    infotext += "|medium             = \n"
    infotext += "|dimensions         = \n"    
    
    infotext += "|institution        = {{Institution:Statens museer för världskultur}}\n"
    
    infotext += "|department         = [[q:Q1371375|Etnografiska muséet]]\n"
    
    infotext += "|references         = \n"
    infotext += "|object history     = \n"
    infotext += "|exhibition history = \n"
    infotext += "|credit line        = \n"
    infotext += "|inscriptions       = \n"
    infotext += "|notes              = \n"
    infotext += "|accession number   = \n"
    
    if pd.notnull(row["Fotonummer"]):
        infotext += "|source             = Original file name, as recieved from SMVK:  <br /> '''" + row["Fotonummer"] +        ".tif'''\n[[SMVK cooperation project|COH]]\n"
        
    infotext += "|permission         = {{cc-zero}}\n"
    infotext += "|other_versions     =\n"
    infotext += "}}"
    
    
    infotext += "\n"
    infotext += "\n[[Category:Images_from_SMVK_2016-11]]"
    
    if personnamn_not_even:
        infotext += "\n[[Category:Images_from_SMVK_with_faulty_depicted_persons]]"
    if lacking_description:
        infotext += "\n[[Category:Images_from_SMVK_without_full_description]]"
    if lacking_photographer:
        infotext += "\n[[Category:Images_from_SMVK_without_photographer]]"
    
    if OK_to_upload:
        #print("new_filename: {} + .info".format(new_filename))
        outfile = open(outpath + new_filename + ".info","w")
        outfile.write(infotext)
        outfile.close()
        
    print(infotext)
    print()


# In[190]:

for index, row in mexiko.iterrows():
    create_infofiles(row)


# In[29]:

filenames_file = open("./mexiko_filenames_mappings.csv","w")
filenames_file.write("Original|Commons\n")


for index, row in mexiko.iterrows():
    new_filename = create_new_filename(row)
    append_new_filename_to_filenames_mapping_file(filenames_file, row["Fotonummer"] + ".tif", new_filename)
    create_infofiles(row)


# In[ ]:

total_images = 0
OK_images = 0
uncategorized_images = 0
faulty_images = 0

filenames_file = open("./filenames_mapping.csv","w")
filenames_file.write("Folder|Original|Commons\n")
    
for row_index, row in mexiko.iterrows():
    filename = create_filename(row["Folder"], row["Filename"])
    save_filename_to_filename_file(filenames_file, filename)
    create_infofile(row, filename)
    #print("Stats: \nTotal images {}\nOK images {}\nUncategorized images {}\nImages missing author {}".format(total_images, OK_images - faulty_images, uncategorized_images, faulty_images ))
#print("Total Stats: \nTotal images {}\nOK images {}\nUncategorized images {}\nImages missing author {}".format(total_images, OK_images - faulty_images, uncategorized_images, faulty_images ))
print("Uncategorized images: {} out of {}".format(uncategorized_images, total_images))


# # Create metadata dataframe to convert to wikitable

# In[ ]:

headers = mexiko.columns.tolist()
headers


# In[ ]:

en_headers = ["photo_no","post_no","content_words","desc","country","region","place",
              "ethnic_group_depict","date_of_photo","name_photographer","name_depicted",
             "search_words","event_or_attending_at","url","subcol_desc","wiki_url"]


# In[ ]:

table_string = ""
# Declare table
table_header = """{| class="wikitable"
|-
"""
table_string += table_header

# Column headers
for header in en_headers:
    table_string += "! " + header + "\n"
table_string += "|-\n"

iter_limit = 3 # for testing purpose
for index, row in mexiko.iterrows():
    if index < iter_limit:
        for col in headers:
            table_string += "| " + str(row[col]) + "\n"
        table_string += "|-\n"
    else:
        break
    
# Close table
table_string += "|}"
print(table_string)


# for row in mexiko.itertuples()[:3]:
#     print(row)
#     

# # 

# In[ ]:

mexiko.to_csv("enriched_mexiko_metadata_table.csv", index=False)


# # 1. Create category/wikidata mapping tables
# 
# [place mappings](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/places_mappings)
# 
# [Mexiko keywords](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Mexiko_keywords)
# 
stopwords_file = open("./stopwords.txt","w")
for token, count in token_count.most_common(1000):
    stopwords_file.write(token + "\n")
stopwords_file.close()
# In[ ]:

stopwords = [w.rstrip() for w in open("./stopwords.txt").readlines()]
stopwords


# ## Column "Motivord"

# The mapping tables are pasted onto [Commons](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Mexiko_keywords)

# In[ ]:

list_of_strings = mexiko.Motivord.values.astype("str")
chunk_of_strings = "" 

for string in list_of_strings:
    clean_string = regex.sub("[\"\'\.\!\?\:\(\),;]| - ","",string) # remove .'s
    chunk_of_strings += " " + clean_string

#chunk_of_strings # separated by ","

nyckelord_list = [phrase.strip() for phrase in chunk_of_strings.split(" ") if phrase not in stopwords]
#print(nyckelord_list[:10])

nyckelord_freq = Counter(nyckelord_list)
nyckelord_freq.most_common(20)


# In[ ]:

header = "== Keywords from column '''Motivord''' (as is, separated by comma) ==\n"
header_row = """{| class="wikitable sortable" style="width: 60%; height: 200px;"
! Motivord
! frequency
! category
! wikidata
|-\n"""

data_rows = []
for kw, count in  nyckelord_freq.most_common(50): # original 12 stops at 4 occurances of "bad"
    nyckelord = "| " + kw + "\n"
    
    freq = "| " + str(count) + "\n"
    the_rest = "| \n| \n|-"
        
    row = nyckelord + freq + the_rest
    
    data_rows.append(row)
        
table_ending = "\n|}"
#print(data_rows)
nyckelord_wikitable = header + header_row + "\n".join(data_rows) + table_ending
print(nyckelord_wikitable)


# ## Column "Beskrivning"

# In[ ]:

####### Unigrams ##############
clean_tokens_list = []
mega_string = ""
list_of_strings = []
for string in mexiko.Beskrivning.values.astype("str"):
    mega_string += " " +string
    clean_string = regex.sub("[\"\”\'\.\!\?\:\,\(\);]| - "," ",string) # remove .'s
    #print(clean_string)
    tokens = clean_string.split(" ")
    clean_tokens = [word for word in tokens] # if word not in stopwords
    #print(clean_tokens)
    for token in clean_tokens:
        clean_tokens_list.append(token)
    clean_string = " ".join(clean_tokens)
    clean_ended_string = clean_string + "." # add .'s again!

    list_of_strings.append(clean_ended_string)
    
#print("clean_tokens_list:\n{}".format(clean_tokens_list))
token_count = Counter(clean_tokens_list)

####### Bigrams ##############
chunk_of_strings = "" 
chunk_of_strings += list_of_strings[0]
for string in list_of_strings[1:]:
    if string not in stopwords:
        chunk_of_strings += " " + string

### Bigrams second approach (to avoid bigrams made of end-word + first word next sentence)
token = nltk.word_tokenize(chunk_of_strings)
bigrams = ngrams(token,2)
bigrams_counter = Counter(bigrams)

clean_bigram_dict = {}
for each_tuple, freq in bigrams_counter.items():
    #print(each_tuple)
    w1, w2 = each_tuple
    forbidden_chars = set([",","."])
    if w1 in forbidden_chars or w2 in forbidden_chars:
        continue
    elif freq > 3:
        clean_bigram_dict[w1 + " " + w2] = freq
    else:
        continue
#print(type(bigrams_counter))
#print(list(bigrams_counter)[:2])
sorted_clean_bigram_dict = sorted(clean_bigram_dict.items(), key=operator.itemgetter(1), reverse=True)
print("Token count:\n{}".format(token_count.most_common(1000)))
print()
print("Bigrams:\n{}".format(sorted_clean_bigram_dict))
#for bigram in sorted_clean_bigram_dict:
#    print(bigram)

# single words


# In[ ]:

header = "== Keywords from column '''Beskrivning''' (två-ordskombinationer) ==\n"
header_row = """{| class="wikitable sortable" style="width: 60%; height: 200px;"
! Två-ordskombination
! frequency
! category
! wikidata
|-\n"""

data_rows = []
for kw, count in sorted_clean_bigram_dict: 
    w1, w2 = kw.split()
    #print("w1: {} w2: {}".format(w1,w2))
    if w1 in stopwords or w2 in stopwords:
        print("Forbidden bigram: {}".format(kw))
    else:
        nyckelord = "| " + kw + "\n"
    
        freq = "| " + str(count) + "\n"
        the_rest = "| \n| \n|-"
        
        row = nyckelord + freq + the_rest
    
        data_rows.append(row)
        
table_ending = "\n|}"
#print(data_rows)
nyckelord_wikitable = header + header_row + "\n".join(data_rows) + table_ending
print()
print(nyckelord_wikitable)


# In[ ]:

header = "== Keywords from column '''Beskrivning''' (word-by-word) ==\n"
header_row = """{| class="wikitable sortable" style="width: 60%; height: 200px;"
! Ord
! frequency
! category
! wikidata
|-\n"""

data_rows = []
for kw, count in token_count.most_common(500): # original 50 stops at 3 occurances of "H"
    if kw in stopwords:
        print("Forbidden unigram: {}".format(kw))
    elif count >= 3:
        nyckelord = "| " + kw + "\n"
    
        freq = "| " + str(count) + "\n"
        the_rest = "| \n| \n|-"
        
        row = nyckelord + freq + the_rest
    
        data_rows.append(row)
    
table_ending = "\n|}"
#print(data_rows)
nyckelord_wikitable = header + header_row + "\n".join(data_rows) + table_ending
print()
print(nyckelord_wikitable)


# # Column "Sökord"

# In[ ]:

mexiko.Sökord.value_counts()


# In[ ]:

sokord_count = Counter()

for index, value in mexiko.Sökord.iteritems():
    tokens = str(value).split(",")
    clean_tokens = [token.strip() for token in tokens]
    for token in clean_tokens:
        sokord_count[token] += 1
sokord_count.most_common()


# In[ ]:

# unigram "Motivord"
nyckelord_freq.most_common(50)
# unigram "Beskrivning"
token_count.most_common(1000)
# bigram "Beskrivning"
sorted_clean_bigram_dict
# uni- and bigrams "Sökord"
sokord_count.most_common()


# # Create mapping list for places - columns "Ort, foto", "Region, foto"

# In[ ]:

res = "Estado de Oaxaca, Oaxaca".partition(",")
res


# In[ ]:

res = "Villahermosa".split(",")
res[-1]


# In[ ]:

res = "Chichén Itzá, Dzitas".split(",")
res[-1].strip()


# In[ ]:

place_counter = Counter()
for index, row in mexiko.iterrows():
    if not pd.isnull(row["Ort, foto"]):
        place = row["Ort, foto"].split(",")[-1].strip()
        #print("full: {}\n place: {}\n".format(row["Ort, foto"], place))
        place_counter[place] += 1
    elif pd.isnull(row["Ort, foto"]) and pd.notnull(row["Region, foto"]): # city/village/place not specified, but
        place = row["Region, foto"].split(",")[-1].strip()
        #print("full: {}\n place: {}\n".format(row["Region, foto"], place))
        place_counter[place] += 1
    else: # neither place nor region is specified
        place_counter["n/a"] += 1
        #print("No region or place! Fotonummer: {}".format(row["Fotonummer"]))
place_counter.most_common()


# In[ ]:

place_table = ""
place_table += """{| class="wikitable"
|-
! Place
! Frequency
! Commons cat
! Wikidata item
|-
"""

for place, freq in place_counter.most_common():
    #print(place, freq)
    place_table += "| " + str(place) + "\n| " + str(freq) + "\n|\n|\n|-\n" 

place_table += "|}"
print(place_table)


# # Create mapping list for depicted persons
# The mapping list is located on [Commons](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Mexiko_depicted_persons)

# In[53]:

all_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Personnamn / avbildad"]):
        lista = row["Personnamn / avbildad"].split(", ")
        for i,j in zip(lista[::2],lista[1::2]):
            print(i,j)
#for name in all_names:
#    print(all_names)
all_names


# # 2. Create new filenames for the images
$ cypern.columns

Index(['Fotonummer', 'Postnr.', 'Nyckelord', 'Beskrivning', 'Land, foto',
       'Region, foto', 'Ort, foto', 'Geograf namn, alternativ', 'Fotodatum',
       'Personnamn / fotograf', 'Personnamn / avbildad', 'Sökord',
       'Händelse / var närvarande vid', 'Länk'],
      dtype='object')
# In[ ]:

def save_filename_to_filename_file(filname_file, filename):
    """Create a file mapping original filenames and their folders with new
    Commons filenames according to <Task X on Phabricator>"""
    folder = row["Folder"]
    file = row["Filename"]
    # Filename: <Filename_1_clean>_-_DecArch_-_<Folder_#>-<Filename_0_clean>.<ext>
    
    #print("filename: {}".format(filename))
    filenames_file.write("{}|{}|{}\n".format(row["Folder"],row["Filename"],filename))


# In[ ]:

def get_foldernames_and_filenames(inpath):
    


# In[ ]:

def create_filenames(fold, foldobj):
    


# In[ ]:

filenames_file = open("./filenames_mapping.csv","w")
filenames_file.write("Folder|Original|Commons\n")

for row_index, row in cypern.iterrows():
    filename = create_filename(row["Folder"], row["Filename"])
    save_filename_to_filename_file(filenames_file, filename)


# Infobox mapping is available on [Phabricator](https://phabricator.wikimedia.org/T144485)

# In[ ]:

filenames_dict = {}
for index, row in cypern.iterrows():
    

