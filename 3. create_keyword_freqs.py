
# coding: utf-8

# In[2]:

import os
import pandas as pd
from collections import Counter,OrderedDict


# In[3]:

metadata = pd.read_excel("./excel-export.xls", sheetname="Sheet0")


# In[3]:

metadata.columns


# In[19]:

original = ["Fotonummer", "Motivord", "Land, foto", "Region, foto",  "Ort, foto",  "Världsdel, foto", "Land, ursprung, Land, tillverkning, Land, brukare", "Region, ursprung/bruk/tillv", "Etn. avb.", "Tumnagel", "Postnr.", "Fotodatum", "Ort, ursprung/bruk/tillv", "Världsdel", "<Dataelement> / OBJTXT / Beskrivning", "<Dataelement> / OBJNAM / Sökord"]
fixed = ["Fotonr", "Motivord", "Land_foto", "Region_foto", "Ort_foto", "Världsdel_foto", "Land_urspr_tillver_brukare", "Region_urspr_tillv_brukare", "Etn_avb", "Tumnagel", "Postnr", "Fotodatum", "Ort_urspr_tillv_brukare", "Världsdel", "Beskrivning", "Sokord"]
col_map = OrderedDict(zip(original,fixed))
col_map


# In[20]:

metadata.columns = col_map.values()


# In[21]:

metadata.head(3)


# In[24]:

sum(pd.isnull(metadata.Land_foto))


# # Luogo keywords

# In[6]:

cnt = Counter(metadata.Luogo.tolist())
cnt.most_common(30)


# In[81]:

header = "== '''Luogo''' (place) ==\n"
header_row = """{| class="wikitable sortable" style="width: 60%; height: 200px;"
! Luogo
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


# # Special place (Nome monumento + Luogo)

# In[31]:

all_comb = zip(list(metadata["Nome monumento"]), list(metadata["Luogo"]))
all_comb = list(all_comb)
all_comb[5:10]


# In[34]:

special = Counter(all_comb)
special.most_common(5)


# In[67]:

header = "== Specific places (combination of '''Nome Monumento''' and '''Luogo''') ==\n"
header_row = """{| class="wikitable sortable" style="width: 60%; height: 200px;"
! Nome_monumento
! Luogo
! frequency
! category
! wikidata
|-\n"""


# make sure the values are sorted when printed, since wikitable syntax doesn't allow pre-sorted field
# http://stackoverflow.com/questions/16140758/default-sort-column-in-wikipedia-table
df = pd.DataFrame()
for *tup, cnt in special.items():
    for n, l in tup:
        row_data = pd.DataFrame([{"nome":n, "luogo":l, "freq":cnt}])
    df = df.append(row_data,ignore_index=True)

df.sort_values(by="freq", ascending=False, inplace=True)  
#print(df.head())

# Now create strings to form wikitable rows in sorted order
data_rows = []
for index, row in df.iterrows():
    nome = "| " + str(row["nome"]) + "\n"
    luogo = "| " + str(row["luogo"]) + "\n"
    freq = "| " + str(row["freq"]) + "\n"
    the_rest = "| \n| \n|-"
        
    new_row = nome + luogo + freq + the_rest
    
    if pd.notnull(row["nome"]) and pd.notnull(row["luogo"]) and row["nome"] != row["luogo"]:
        data_rows.append(new_row)
    else:
        continue
        
table_ending = "\n|}"
#print(data_rows)
special_wikitable = header + header_row + "\n".join(data_rows) + table_ending
print(special_wikitable)


# In[ ]:



