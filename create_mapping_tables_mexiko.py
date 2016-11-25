
# coding: utf-8

# In[43]:

import pickle
from collections import Counter
import regex
import nltk
import pandas as pd
# For bigrams creation
import nltk
from nltk import word_tokenize
from nltk.util import ngrams
import operator


# # 1. Create category/wikidata mapping tables
# 
# [place mappings](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/places_mappings)
# 
# [Mexiko keywords](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Mexiko_keywords)

# In[35]:

mexiko = pickle.load(open("./mexiko_df_final.pickle","rb"))


# In[36]:

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


# In[37]:

stopwords_file = open("./stopwords.txt","w")
for token, count in token_count.most_common(1000):
    stopwords_file.write(token + "\n")
stopwords_file.close()


# In[38]:

stopwords = [w.rstrip() for w in open("./stopwords.txt").readlines()]
stopwords


# ## Column "Motivord"

# The mapping tables are pasted onto [Commons](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Mexiko_keywords)

# In[39]:

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


# In[40]:

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


# In[41]:

## Column "Beskrivning"


# In[42]:

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


# In[20]:

# Column "Sökord"


# In[22]:

mexiko.Sökord.value_counts().head()


# In[23]:

sokord_count = Counter()

for index, value in mexiko.Sökord.iteritems():
    tokens = str(value).split(",")
    clean_tokens = [token.strip() for token in tokens]
    for token in clean_tokens:
        sokord_count[token] += 1
sokord_count.most_common()


# In[24]:

# unigram "Motivord"
nyckelord_freq.most_common(50)
# unigram "Beskrivning"
token_count.most_common(1000)
# bigram "Beskrivning"
sorted_clean_bigram_dict
# uni- and bigrams "Sökord"
sokord_count.most_common()


# In[25]:

# Create mapping list for places - columns "Ort, foto", "Region, foto"


# In[26]:

res = "Estado de Oaxaca, Oaxaca".partition(",")
res


# In[27]:

res = "Villahermosa".split(",")
res[-1]


# In[28]:

res = "Chichén Itzá, Dzitas".split(",")
res[-1].strip()


# In[31]:

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


# In[32]:

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

# In[33]:

all_names = set()
for index, row in mexiko.iterrows():
    if pd.notnull(row["Personnamn / avbildad"]):
        lista = row["Personnamn / avbildad"].split(", ")
        for i,j in zip(lista[::2],lista[1::2]):
            print(i,j)
#for name in all_names:
#    print(all_names)
all_names


# In[ ]:



