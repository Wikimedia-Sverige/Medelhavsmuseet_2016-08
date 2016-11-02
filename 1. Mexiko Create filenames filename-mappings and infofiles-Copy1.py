
# coding: utf-8

# In[41]:

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

# In[42]:

mexiko_test = pd.read_excel("excel-export.xls", sheetname="Mexiko")
mexiko_test.columns


# In[43]:

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


# ## Add sub-collection metadata field "description"

# In[44]:

a_str = "1234.j.345432"


# In[45]:

a_str.partition(".")


# In[46]:

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


# In[47]:

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

# In[48]:

for index, row in mexiko.iterrows():
    url = row["Länk"]
    first, slash, id_str = url.rpartition("/")
    new_url = "[" + url + " Fotonummer: " + id_str + "]"
    mexiko.loc[index, "wiki_url"] = new_url
mexiko


# In[49]:

mexiko.loc[0,"wiki_url"]


# # Create metadata dataframe to convert to wikitable

# In[50]:

headers = mexiko.columns.tolist()
headers


# In[51]:

en_headers = ["photo_no","post_no","content_words","desc","country","region","place",
              "ethnic_group_depict","date_of_photo","name_photographer","name_depicted",
             "search_words","event_or_attending_at","url","subcol_desc","wiki_url"]


# In[52]:

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
stopwords_file = open("./stopwords.txt","w")
for token, count in token_count.most_common(1000):
    stopwords_file.write(token + "\n")
stopwords_file.close()
# In[100]:

stopwords = [w.rstrip() for w in open("./stopwords.txt").readlines()]
stopwords


# ## Column "Motivord"

# The mapping tables are pasted onto [Commons](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Mexiko_keywords)

# In[101]:

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


# In[102]:

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

# In[103]:

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


# In[104]:

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


# In[105]:

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

# In[106]:

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
# 
# # Cypern-samlingen

# In[ ]:

filenames_dict = {}
for index, row in cypern.iterrows():
    

