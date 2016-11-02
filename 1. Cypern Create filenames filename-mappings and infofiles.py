
# coding: utf-8

# In[8]:

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


# The metadata file on [Google Docs](https://docs.google.com/spreadsheets/d/1YXusiepersJ6_XGoUVEE0jfGh5NJs-5Rds2_l5ZbGik/edit?usp=sharing)
#     
# [Here](http://cypernochkreta.dinstudio.se/text1_100.html) is a informative reference web site about the archeological excavation sites

# # 0. Read in the metadata

# In[3]:

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
stopwords_file = open("./stopwords.txt","w")
for token, count in token_count.most_common(1000):
    stopwords_file.write(token + "\n")
stopwords_file.close()
# In[4]:

stopwords = [w.rstrip() for w in open("./stopwords.txt").readlines()]
stopwords


# ## Column "Nyckelord"

# In[5]:

list_of_strings = cypern.Nyckelord.values.astype("str")
chunk_of_strings = "" 

for string in list_of_strings:
    clean_string = regex.sub("[\"\'\.\!\?\:,;]| - ","",string) # remove .'s
    chunk_of_strings += " " + clean_string

chunk_of_strings # separated by ","

nyckelord_list = [phrase.strip() for phrase in chunk_of_strings.split(" ")]
#print(nyckelord_list[:10])

nyckelord_freq = Counter(nyckelord_list)
nyckelord_freq.most_common(20)


# The mapping tables are pasted onto [Commons](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Cypern_keywords)

# In[6]:

header = "== Keywords from column '''Nyckelord''' (as is, separated by comma) ==\n"
header_row = """{| class="wikitable sortable" style="width: 60%; height: 200px;"
! Nyckelord
! frequency
! category
! wikidata
|-\n"""

data_rows = []
for kw, count in  nyckelord_freq.most_common(12): # stops at 3 occurances
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

# In[53]:

#clean_tokens_list = []
mega_string = ""
list_of_strings = []
for string in cypern.Beskrivning.values.astype("str"):
    mega_string += " " +string
    clean_string = regex.sub("[\"\'\.\!\?\:\,;]| - ","",string) # remove .'s
    #print(clean_string)
    tokens = clean_string.split(" ")
    clean_tokens = [word for word in tokens if word not in stopwords]
    #print(clean_tokens)
    #for token in clean_tokens:
    #    clean_tokens_list.append(token)
    clean_string = " ".join(clean_tokens)
    clean_ended_string = clean_string + "." # add .'s again!

    list_of_strings.append(clean_ended_string)

chunk_of_strings = "" 
chunk_of_strings += list_of_strings[0]
for string in list_of_strings[1:]:
    chunk_of_strings += " " + string
#print(chunk_of_strings)


### bigrams initial approach
#blob = TextBlob(chunk_of_strings) # initiate empty blob

#bigrams = blob.ngrams(2)
#bigrams_list = []
#for wl in bigrams:
#    bigrams_list.append(" ".join(wl))

#bigrams_count = Counter(bigrams_list)
#print("Bigrams:\n{}".format(bigrams_count.most_common(50)))
#print()

### Bigrams second approach (to avoid bigrams made of end-word + first word next sentence)
token = nltk.word_tokenize(mega_string)
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
#sorted_clean_bigram_dict = sorted(clean_bigram_dict.items(), key=operator.itemgetter(1), reverse=True)
print("Bigrams:\n{}".format(sorted_clean_bigram_dict))
#for bigram in sorted_clean_bigram_dict:
#    print(bigram)

# single words

#print("clean_tokens_list:\n{}".format(clean_tokens_list))
token_count = Counter(clean_tokens_list)
print("Token count:\n{}".format(token_count.most_common(50)))


# In[55]:

header = "== Keywords from column '''Beskrivning''' (två-ordskombinationer) ==\n"
header_row = """{| class="wikitable sortable" style="width: 60%; height: 200px;"
! Två-ordskombination
! frequency
! category
! wikidata
|-\n"""

data_rows = []
for kw, count in sorted_clean_bigram_dict: # stops at 3 occurances
    nyckelord = "| " + kw + "\n"
    
    freq = "| " + str(count) + "\n"
    the_rest = "| \n| \n|-"
        
    row = nyckelord + freq + the_rest
    
    data_rows.append(row)
        
table_ending = "\n|}"
#print(data_rows)
nyckelord_wikitable = header + header_row + "\n".join(data_rows) + table_ending
print(nyckelord_wikitable)


# In[8]:

header = "== Keywords from column '''Beskrivning''' (word-by-word) ==\n"
header_row = """{| class="wikitable sortable" style="width: 60%; height: 200px;"
! Ord
! frequency
! category
! wikidata
|-\n"""

data_rows = []
for kw, count in token_count.most_common(50): # stops at 3 occurances
    nyckelord = "| " + kw + "\n"
    
    freq = "| " + str(count) + "\n"
    the_rest = "| \n| \n|-"
        
    row = nyckelord + freq + the_rest
    
    data_rows.append(row)
        
table_ending = "\n|}"
#print(data_rows)
nyckelord_wikitable = header + header_row + "\n".join(data_rows) + table_ending
print(nyckelord_wikitable)


# ## Merge keywords from columns Nyckelord and Beskrivning

# In[9]:

tot_dict = {}
for bigram, count in bigrams_count.most_common(100):
    tot_dict[bigram] = count
for unigram, count in token_count.most_common(100):
    tot_dict[unigram] = count
sorted_tot_dict = sorted(tot_dict.items(), key=operator.itemgetter(1), reverse=True)
sorted_tot_dict


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
    

