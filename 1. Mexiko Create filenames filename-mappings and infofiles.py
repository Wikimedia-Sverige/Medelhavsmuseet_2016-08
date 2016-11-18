
# coding: utf-8

# In[1]:

import pandas as pd
from collections import Counter
import os
from textblob import TextBlob
import regex
import operator

# For bigrams creation
import nltk
from nltk import word_tokenize
from nltk.util import ngrams

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

# In[2]:

mexiko_test = pd.read_excel("excel-export.xls", sheetname="Mexiko")
mexiko_test.columns


# In[3]:

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

# In[4]:

mexiko.Motivord.value_counts()[:10]


# In[5]:

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

# In[4]:

a_str = "1234.j.345432"


# In[5]:

a_str.partition(".")


# In[6]:

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


# In[7]:

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

# In[8]:

for index, row in mexiko.iterrows():
    print(row["Länk"])
    break


# In[9]:

first, slash, id_str = "http://kulturarvsdata.se/SMVK-EM/fotografi/html/2786726".rpartition("/")
id_str


# In[10]:

for index, row in mexiko.iterrows():
    url = row["Länk"]
    #first, slash, id_str = url.rpartition("/")
    #new_url = "[" + url + " Fotonummer: " + id_str + "]"
    #mexiko.loc[index, "wiki_url"] = new_url
    
    left_side, slash, id_str = url.rpartition("/")
    template = "{{SMVK-EM-link|1=foto|2=" + id_str + "|3=" + row["Fotonummer"] + "}}"
    mexiko.loc[index, "SMVK-EM-link"] = template
    
mexiko


# In[11]:

mexiko.loc[0,"SMVK-EM-link"]


# # Create list of badly filled out meatdata for WMMX

# In[12]:

mexiko["Personnamn / avbildad"].value_counts()


# In[13]:

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


# In[38]:

bad_keywords = ["pyramid","tempel","Ciudadela","tempelpyramid", "tempelpyramider","ruiner","fornlämningar"]

file_table = ""
tot_cnt = 0
bad_cnt = 0
problematic_cnt = 0
no_keyword = 0
no_ort = 0
generic_keyword = 0
empty_ort_and_motivord = 0
no_ort_and_generic_keyword = 0

for index, row in mexiko.iterrows():
    tot_cnt += 1
    if pd.isnull(row["Ort, foto"]) and pd.isnull(row["Motivord"]):
        bad_cnt += 1
        empty_ort_and_motivord += 1
        file_table += "! " + str(bad_cnt) + "\n" 
        file_table += "| " + row["SMVK-EM-link"] + "\n"
        file_table += "| " + str(row["Region, foto"]) + "\n"
        file_table += "| " + str(row["Ort, foto"]) + "\n"
        file_table += "| Both 'Motivord' and 'Ort, foto' are empty\n"
        file_table += "|\n"
        file_table += "|\n"
        file_table += "|-\n"
        
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
                        file_table += "! " + str(bad_cnt) + "\n" 
                        file_table += "| " + row["SMVK-EM-link"] + "\n"
                        file_table += "| " + str(row["Region, foto"]) + "\n"
                        file_table += "| " + str(row["Ort, foto"]) + "\n"
                        file_table += "| No 'Ort, foto' and 'Motivord' is generic\n"
                        file_table += "|\n"
                        file_table += "|\n"
                        file_table += "|-\n"
        else:
            problematic_cnt += 1
            no_ort += 1
            file_table += "! " + str(bad_cnt) + "\n" 
            file_table += "| " + row["SMVK-EM-link"] + "\n"
            file_table += "| " + str(row["Region, foto"]) + "\n"
            file_table += "| " + str(row["Ort, foto"]) + "\n"
            file_table += "| No 'Ort, foto'\n"
            file_table += "|\n"
            file_table += "|\n"
            file_table += "|-\n"
                        
    
    elif pd.isnull(row["Ort, foto"]) and pd.notnull(row["Motivord"]) in bad_keywords:
        # bad_cnt += 1
        problematic_cnt += 1
        no_ort_and_generic_keyword += 1
        file_table += "! " + str(bad_cnt) + "\n" 
        file_table += "| " + row["SMVK-EM-link"] + "\n"
        file_table += "| " + str(row["Region, foto"]) + "\n"
        file_table += "| " + str(row["Ort, foto"]) + "\n"
        file_table += "| No 'Ort, foto' and 'Motivord' is generic\n"
        file_table += "|\n"
        file_table += "|\n"
        file_table += "|-\n" 
        
    else:
    
        if pd.isnull(row["Motivord"]) and pd.notnull(row["Ort, foto"]):
            # bad_cnt += 1 # Ort, foto + person, avbildad?
            no_keyword += 1
            problematic_cnt +=1
            file_table += "! " + str(bad_cnt) + "\n" 
            file_table += "| " + row["SMVK-EM-link"] + "\n"
            file_table += "| " + str(row["Region, foto"]) + "\n"
            file_table += "| " + str(row["Ort, foto"]) + "\n"
            file_table += "| No 'motivord'\n"
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
                    if diff == set():
                        # bad_cnt += 1
                        problematic_cnt += 1
                        file_table += "! " + str(bad_cnt) + "\n" 
                        file_table += "| " + row["SMVK-EM-link"] + "\n"
                        file_table += "| " + str(row["Region, foto"]) + "\n"
                        file_table += "| " + str(row["Ort, foto"]) + "\n"
                        file_table += "| Motivord' is generic'\n"
                        file_table += "|\n"
                        file_table += "|\n"
                        file_table += "|-\n"
                                                        
            

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
print()
print("Both 'Motivord' and 'Ort, foto' are empty: '''{}'''".format(empty_ort_and_motivord))
print()
print("=== Problematic photos (below): '''{}''' ===".format(problematic_cnt))
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

print(full_table)


# Tips: Om det bara finns generiskt motivord och det finns Ort, foto OCH Motivord:
# Finns Commons-kategori som heter typ Pyramids in Techuacan?
# pröva Motivord

# In[49]:

mexiko.to_pickle("./mexiko_df_final.pickle")


# # Inspect that unique filenames gets created

# In[35]:

# Field "Motivord", "Beskrivning" and "Ort, foto"
non_id_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Motivord"] and pd.notnull(row["Beskrivning"]) and pd.notnull(row["Ort, foto"])):
        motivord = row["Motivord"]
        beskrivning = row["Beskrivning"]
        ort = row["Ort, foto"]
        non_id_names.add(motivord + beskrivning + ort)
print(len(non_id_names))


# In[34]:

for fname in non_id_names:
    print(fname)


# In[23]:

# Field "Beskrivning" and "Ort, foto"
non_id_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Beskrivning"]) and pd.notnull(row["Ort, foto"]):
        non_id_names.add(str(row["Beskrivning"]) + str(row["Ort, foto"]) )
print(len(non_id_names))


# In[24]:

# Field "Beskrivning" only
non_id_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Beskrivning"]):
        non_id_names.add(row["Beskrivning"])
print(len(non_id_names))


# # Create filenames and filenames-mapping file

# In[42]:

fname1 = "0307.a.0001.tif"
fname2 = "0307.a.0002.a.tif"
print("fname1: {}".format(fname1.split(".")))
print("fname2: {}".format(fname2.split(".")))
print(fname2[-1].isalpha())


# In[60]:

for index, row in mexiko.iterrows():
    if pd.notnull(row["Beskrivning"]) and pd.notnull(row["Ort, foto"]) and pd.notnull(row["Motivord"]):
        print("beskr: {}\nOrt: {}\n:Motivord: {}".format(row["Beskrivning"], row["Ort, foto"], row["Motivord"]))


# In[50]:

def create_filename(filename):
    import os
    import pickle
    # Remove the extension from filename_1_clean
    fname_parts = filename.split(".")
    
    def create_ext_and_id_str(fname_parts):
        if len(fname_parts) == 4 and fname_parts[-1].isalpha() :
            ext = fname_parts[-1]
            id_str = fname_parts[2]
        elif len(fname_parts) == 5 and fname_parts[-1].isalpha():
            ext = fname_parts[-1]
            id_str = fname_parts[2] + "." + fname_parts[3]
        #return print("ext: {}\nid_str: {}".format(ext, id_str))
        return ext, id_str
    ext, id_str = create_ext_and_id_str(fname_parts)
    
    mexiko = pickle.load(open("./mexiko_df_final.pickle","rb"))
    
    def construct_new_name_from_dataframe(dataframe):
        for index, row in dataframe.iterrows():
            


# In[48]:

create_filename(fname2)


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

# In[10]:

headers = mexiko.columns.tolist()
headers


# In[11]:

en_headers = ["photo_no","post_no","content_words","desc","country","region","place",
              "ethnic_group_depict","date_of_photo","name_photographer","name_depicted",
             "search_words","event_or_attending_at","url","subcol_desc","wiki_url"]


# In[12]:

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

# In[82]:

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
# In[13]:

stopwords = [w.rstrip() for w in open("./stopwords.txt").readlines()]
stopwords


# ## Column "Motivord"

# The mapping tables are pasted onto [Commons](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Mexiko_keywords)

# In[14]:

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


# In[15]:

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

# In[16]:

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


# In[17]:

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


# In[18]:

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

# In[19]:

mexiko.Sökord.value_counts()


# In[120]:

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

# In[29]:

res = "Estado de Oaxaca, Oaxaca".partition(",")
res


# In[38]:

res = "Villahermosa".split(",")
res[-1]


# In[40]:

res = "Chichén Itzá, Dzitas".split(",")
res[-1].strip()


# In[55]:

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


# In[61]:

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


# # 2. Create new filenames for the images
$ cypern.columns

Index(['Fotonummer', 'Postnr.', 'Nyckelord', 'Beskrivning', 'Land, foto',
       'Region, foto', 'Ort, foto', 'Geograf namn, alternativ', 'Fotodatum',
       'Personnamn / fotograf', 'Personnamn / avbildad', 'Sökord',
       'Händelse / var närvarande vid', 'Länk'],
      dtype='object')
# In[10]:

def save_filename_to_filename_file(filname_file, filename):
    """Create a file mapping original filenames and their folders with new
    Commons filenames according to <Task X on Phabricator>"""
    folder = row["Folder"]
    file = row["Filename"]
    # Filename: <Filename_1_clean>_-_DecArch_-_<Folder_#>-<Filename_0_clean>.<ext>
    
    #print("filename: {}".format(filename))
    filenames_file.write("{}|{}|{}\n".format(row["Folder"],row["Filename"],filename))


# In[11]:

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
    

