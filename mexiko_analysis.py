
# coding: utf-8

# In[3]:

import pandas as pd
from collections import Counter
import os
import regex
import pickle
#import batchupload.helpers as helpers # error when using Python 3.5.2 :: Anaconda custom (x86_64) on MacBook Air

mexiko = pickle.load(open("./mexiko_df_final.pickle","rb"))


# In[ ]:

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


# In[4]:

mexiko["Personnamn / avbildad"].value_counts()


# In[ ]:

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


# # Inspect keywords in column "Motivord"

# In[ ]:

mexiko.Motivord.value_counts()[:10]


# In[1]:

motivord_count = Counter()

for index, string in mexiko.Motivord.iteritems():
    if pd.notnull(string):
        tokens = string.split(", ")
        tokens = [token.strip() for token in tokens]
        for token in tokens:
            motivord_count[token] += 1
motivord_count.most_common(10)


# # Inspect that unique filenames gets created

# In[1]:

fname1 = "0307.a.0001.tif"
fname2 = "0307.a.0002.a.tif"
print("fname1: {}".format(fname1.split(".")))
print("fname2: {}".format(fname2.split(".")))
print(fname2[-1].isalpha())


# In[1]:

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


# In[2]:

# Field "Beskrivning" and "Ort, foto"
non_id_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Beskrivning"]) and pd.notnull(row["Ort, foto"]):
        non_id_names.add(str(row["Beskrivning"]) + str(row["Ort, foto"]) )
print(len(non_id_names))


# In[3]:

# Field "Beskrivning" only
non_id_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Beskrivning"]):
        non_id_names.add(row["Beskrivning"])
print(len(non_id_names))


# # Inspect keywords in column "Motivord"

# In[1]:

mexiko.Motivord.value_counts()[:10]


# In[2]:

motivord_count = Counter()

for index, string in mexiko.Motivord.iteritems():
    if pd.notnull(string):
        tokens = string.split(", ")
        tokens = [token.strip() for token in tokens]
        for token in tokens:
            motivord_count[token] += 1
motivord_count.most_common(10)


# # Statistics: Not OK_to_upload

# In[3]:

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

# In[4]:

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


# In[5]:

# Field "Beskrivning" and "Ort, foto"
non_id_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Beskrivning"]) and pd.notnull(row["Ort, foto"]):
        non_id_names.add(str(row["Beskrivning"]) + str(row["Ort, foto"]) )
print(len(non_id_names))


# In[6]:

# Field "Beskrivning" only
non_id_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Beskrivning"]):
        non_id_names.add(row["Beskrivning"])
print(len(non_id_names))


# In[7]:

fname1 = "0307.a.0001.tif"
fname2 = "0307.a.0002.a.tif"
print("fname1: {}".format(fname1.split(".")))
print("fname2: {}".format(fname2.split(".")))
print(fname2[-1].isalpha())


# # Create list of badly filled out meatdata for WMMX

# In[ ]:

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


# # Statistics: Not OK_to_upload

# In[ ]:

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

