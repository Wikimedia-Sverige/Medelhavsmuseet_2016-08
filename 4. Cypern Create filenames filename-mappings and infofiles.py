
# coding: utf-8

# In[58]:

import pandas as pd
from collections import Counter
import os
from textblob import TextBlob
import regex


# The metadata file on [Google Docs](https://docs.google.com/spreadsheets/d/1YXusiepersJ6_XGoUVEE0jfGh5NJs-5Rds2_l5ZbGik/edit?usp=sharing)
#     

# # 0. Read in the metadata

# In[2]:

def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text
    
cypern_converters = {"Fotonummer":strip,"Postnr":strip,"Nyckelord":strip,"Beskrivning":strip,"Land":strip,"foto":strip,
                     "Region, foto":strip,"Ort, foto":strip,"Geograf namn, alternativ":strip,"Fotodatum":strip,
                    "Personnamn / fotograf":strip, "Personnamn / avbildad":strip, "Sökord":strip,
                    "Händelse / var närvarande vid":strip, "Länk":strip}

cypern = pd.read_excel("excel-export.xls", sheetname="Cypern", converters=cypern_converters)


# # 1. Create category/wikidata mapping tables

# ## Column "Nyckelord"

# In[66]:

stopwords_file = open("./stopwords.txt","w")
for token, count in token_count.most_common(1000):
    stopwords_file.write(token + "\n")
#stopwords_file.close()


# In[68]:

stopwords = [w.rstrip() for w in open("./stopwords.txt").readlines()]
stopwords


# In[39]:

list_of_strings = cypern.Nyckelord.values.astype("str")
chunk_of_strings = "" 
chunk_of_strings += list_of_strings[0]
for string in list_of_strings[1:]:
    chunk_of_strings += ", " + string
chunk_of_strings # separated by ","

nyckelord_list = [phrase.strip() for phrase in chunk_of_strings.split(",")]
nyckelord_list[:10]

nyckelord_freq = Counter(nyckelord_list)
nyckelord_freq.most_common(10)


# ## Column "Beskrivning"

# In[87]:

b = TextBlob("abc")
b = b.join([" def "," ghi "])
b.pos_tags


# In[92]:

list_of_strings = []
for string in cypern.Beskrivning.values.astype("str"):
    clean_string = regex.sub("[\.\!\?\:\,;]| - ","",string) # remove .'s
    #print(clean_string)
    ended_string = string + "." # add .'s again!
    list_of_strings.append(ended_string)

chunk_of_strings = "" 
chunk_of_strings += list_of_strings[0]
for string in list_of_strings[1:]:
    chunk_of_strings += " " + string
#print(chunk_of_strings)


# bigrams
counter = 0
blobs = []
for line in list_of_strings:
    blobname = blob + str(counter)
    blobname = TextBlob(line)
    blobs.append(blobname)

blobs
    
blob = TextBlob("") # initiate empty blob
#blob.join(blobs)

bigrams = blob.ngrams(2)
bigrams_list = []
for wl in bigrams:
    bigrams_list.append(" ".join(wl))

bigrams_count = Counter(bigrams_list)
print("Bigrams:\n{}".format(bigrams_count.most_common(10)))

# single words
clean_tokens_list = [word for word in regex.split("\W",chunk_of_strings) if word != "" and word not in stopwords]
#print("clean_tokens_list:\n{}".format(clean_tokens_list))
token_count = Counter(clean_tokens_list)
#print("Token count:\n{}".format(token_count.most_common(10)))

tot_dict = {}
for bigram, count in bigrams_count.most_common(50):
    tot_dict[bigram] = count
for unigram, count in token_count.most_common(50):
    tot_dict[unigram] = count
#tot_dict


# In[ ]:




# In[71]:

beskrivning_df = pd.DataFrame(token_count, ignore_index=True)


# In[ ]:

header = "== '''Nyckelord''' (kolumnen) ==\n"
header_row = """{| class="wikitable sortable" style="width: 60%; height: 200px;"
! Nyckelord
! frequency
! category
! wikidata
|-\n"""

data_rows = []
for l, count in cnt.most_common(1000):
    luogo = "| " + l + "\n"
    
    freq = "| " + str(count) + "\n"
    the_rest = "| \n| \n|-"
        
    row = luogo + freq + the_rest
    
    data_rows.append(row)
        
table_ending = "\n|}"
#print(data_rows)
luogo_wikitable = header + header_row + "\n".join(data_rows) + table_ending
print(luogo_wikitable)


# # 2. Create new filenames for the images
$ cypern.columns

Index(['Fotonummer', 'Postnr.', 'Nyckelord', 'Beskrivning', 'Land, foto',
       'Region, foto', 'Ort, foto', 'Geograf namn, alternativ', 'Fotodatum',
       'Personnamn / fotograf', 'Personnamn / avbildad', 'Sökord',
       'Händelse / var närvarande vid', 'Länk'],
      dtype='object')
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
    

