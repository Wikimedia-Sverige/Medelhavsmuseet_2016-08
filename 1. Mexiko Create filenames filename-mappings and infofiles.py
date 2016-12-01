
# coding: utf-8

# In[2]:

get_ipython().system('pip install --process-dependency-links git+https://github.com/lokal-profil/BatchUploadTools.git@py3compat')


# In[1]:

from batchupload import helpers
import pandas as pd
from collections import Counter
import os
import regex
import pickle
#import batchupload.helpers as helpers # error when using Python 3.5.2 :: Anaconda custom (x86_64) on MacBook Air

mexiko = pickle.load(open("./mexiko_df_final.pickle","rb"))


# In[41]:

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

# In[3]:

mexiko_test = pd.read_excel("excel-export.xls", sheetname="Mexiko")
mexiko_test.columns


# In[4]:

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
# 
# * Add these to the final images in the infobox

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


# Tips: Om det bara finns generiskt motivord och det finns Ort, foto OCH Motivord:
# Finns Commons-kategori som heter typ Pyramids in Techuacan?
# pröva Motivord

# # Statistics: Not OK_to_upload

# In[19]:

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


# # Collect keyword mappings and create dataframes
# 
# Keywords for the Mexiko dataset are published as mappingtables on [Commons](https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Mexiko_keywords).

# In[4]:

kw_maps_url = "https://commons.wikimedia.org/wiki/Commons:Medelhavsmuseet/batchUploads/Mexiko_keywords"
kw_maps_list = pd.read_html(kw_maps_url, attrs = {"class":"wikitable"}, header=0)
motivord = kw_maps_list[0]
beskr_bi = kw_maps_list[1]
beskr_uni = kw_maps_list[2]
kw_maps = pd.concat([motivord,beskr_bi,beskr_uni])
#kw_maps = kw_maps.dropna()
print("tot: {} keywords".format(len(kw_maps)))
print("filled in: {}".format(len(kw_maps[:][(pd.notnull(kw_maps["wikidata"])) & (pd.notnull(kw_maps["category"]))])))
kw_maps = kw_maps[:][(pd.notnull(kw_maps["wikidata"])) & (pd.notnull(kw_maps["category"]))] # 33 at 2016-11-24
kw_maps.head()


# # Create filenames and filenames-mapping file

# In[22]:

def create_new_filename(row, filenames_file):
    import pickle
    
    old_filename = row["Fotonummer"] + ".tif"
    
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
            
        elif pd.isnull(row["Beskrivning"]) and pd.notnull(row["Händelse / var närvarande vid"]) and pd.notnull(row["Motivord"]):
            new_fname += row["Motivord"]
            new_fname += " "
            new_fname += row["Händelse / var närvarande vid"]
            new_fname += "_-_"
            new_fname += "SMVK-EM"
            new_fname += "_-_"
            new_fname += id_str
            new_fname += ext
            
        elif pd.isnull(row["Beskrivning"]) and pd.notnull(row["Händelse / var närvarande vid"]) and pd.isnull(row["Motivord"]):
            new_fname += row["Händelse / var närvarande vid"]
            new_fname += "_-_"
            new_fname += "SMVK-EM"
            new_fname += "_-_"
            new_fname += id_str
            new_fname += ext
            print("Fotonummer {}: only 'Händelse / var närvarande vid' added to new filename".format(row["Fotonummer"]))
        
        else:
            print("Fotonummer {} could not be created a new filename for".format(row["Fotonummer"]))
        #print("type(new_fname): {}".format(type(new_fname)))
        return new_fname
    
    def compose_description(row):
        description = ""
        if pd.notnull(row["Beskrivning"]):
            description += row["Beskrivning"]
        if pd.isnull(row["Beskrivning"]) and pd.notnull(row["Händelse / var närvarande vid"]):
            description += row["Händelse / var närvarande vid"]
        return description
    
    def append_new_filename_to_filenames_mapping_file(filenames_file, old_filename, new_filename):
        filenames_file.write("{}|{}\n".format(old_filename, new_filename))
        return 
    
    id_str = create_id_str(fname_parts)
    #print("id_str: {}".format(id_str))
    if id_str:
        ########## Not using BatchUploadTools ###############################
        #fname = construct_new_name_from_dataframe(row, id_str) # without using BatchUploadTools
        #append_new_filename_to_filenames_mapping_file(filenames_file, old_filename, fname)
        #print("fname: {}\nchecked_fname: {}\n".format(fname, checked_fname))
        #return fname
        
        ########## Using BatchUploadTools ####################################
        description = compose_description(row)
        checked_fname = helpers.format_filename(description, "SMVK", row["Fotonummer"]) # skip id_str, since not unique
        return checked_fname
        
    else:
        return print("Could not create a new filename for photo: {}".format(row["Fotonummer"]))


# Infobox mapping is available on [Phabricator](https://phabricator.wikimedia.org/T144485)

# In[23]:

def create_infofiles(row, filenames_file, not_ok_file):
    bad_keywords = ["pyramid","tempel","Ciudadela","tempelpyramid", "tempelpyramider","ruiner","fornlämningar"]
    outpath = "./infofiles/"
    infotext = "{{photograph\n"
    
    new_filename = create_new_filename(row, filenames_file)
    
    lacking_description = False
    lacking_photographer = False
    personnamn_not_even = False
    linne_category = False
    content_categories = False
    OK_to_upload = True
    no_content_categories = 0
    
    if pd.notnull(row["Personnamn / fotograf"]):
        if "Apenes" in row["Personnamn / fotograf"]:
            infotext +="|photographer       =  " + "{{creator|Sigvald_Linné}} / Ola Apenes\n"
        elif "Sigvald" in row["Personnamn / fotograf"]:
            linne_category == True
        else:
            infotext += "|photographer       =  " + row["Personnamn / fotograf"].strip() + "\n"
    if pd.isnull(row["Personnamn / fotograf"]):
        if row["Personnamn / fotograf"] == "Linné, Sigvald": # not all cases
            infotext += "|photographer       =  "+ "{{creator:Sigvald_Linné}}\n" 
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
                linne_category = True
                depicted_people += "[[q:Q5959424|Sigvald Linné]] "
            else:
                depicted_people += j + " " + i + "/"
    depicted_people = depicted_people.rstrip("/") 
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
        infotext += "|source             = Original file name, as recieved from SMVK:  <br /> '''" + row["Fotonummer"] +        ".tif'''\n{{SMVK_cooperation_project|COH}}\n"
        
    infotext += "|permission         = {{cc-zero}}\n"
    infotext += "|other_versions     =\n"
    infotext += "}}"
    
    # categories
    categories = "[[Category:Linné_expedition_at_Teotihuacan_Mexico_1932]]"
    content_categories_set = set()
    for index, kw in kw_maps.iterrows():
        #print(kw["keyword"])
        patt = regex.compile(r"\b" + kw["keyword"] + r"\b", regex.I)
        #print(patt)
        
        
        if pd.notnull(row["Beskrivning"]):
            if patt.search(row["Beskrivning"]):
                #print("Beskrivnig: {}\nkw found {}\n".format(row["Beskrivning"], kw["keyword"]))
                if pd.notnull(kw["category"]) and kw["category"] != "-":
                    content_categories = True
                    content_categories_set.add("[[" + kw["category"] + "]]") 
        
        if pd.notnull(row["Motivord"]):
            list_of_motivord = row["Motivord"].split(", ")
            for motivord in list_of_motivord:
                if patt.search(motivord):
                    if pd.notnull(kw["category"]) and kw["category"] != "-":
                        content_categories = True
                        content_categories_set.add("[[" + kw["category"] + "]]") 
                    
        if pd.notnull(row["Sökord"]):
            list_of_sokord = row["Sökord"].split(", ")
            for sokord in list_of_sokord:
                if patt.search(sokord):
                    if pd.notnull(kw["category"]) and kw["category"] != "-":
                        content_categories = True
                        content_categories_set.add("[[" + kw["category"] + "]]") 
    #print("content_categories_set: \n{}".format(content_categories_set))
    
    content_categories_string = ""    
    if content_categories:
        for content_category in content_categories_set:
            content_categories_string += "\n" + content_category
        categories += "\n" + content_categories_string
        
    else:
        no_content_categories += 1
        categories += "\n[[Images_from_SMVK-EM_without_content_categories]]"
        OK_to_upload = False
    
    if personnamn_not_even:
        categories += "\n[[Category:Images_from_SMVK_with_faulty_depicted_persons]]"
    if lacking_description:
        categories += "\n[[Category:Images_from_SMVK_without_full_description]]"
    if lacking_photographer:
        categories += "\n[[Category:Images_from_SMVK_without_photographer]]"
    if linne_category:
        categories += "\n[[Category:Sigvald_Linné]]"
    
    categories.lstrip()
    
    if OK_to_upload:
        #print(OK_to_upload)
        #print("new_filename: {} + .info".format(new_filename))
        outfile = open(outpath + new_filename + ".info","w")
        outfile.write(infotext + "\n" + categories)
        outfile.close()
    else:
        not_ok_row = ""
        link = "| " + str(row["SMVK-EM-link"]) + "\n"
        desc = "| " + str(row["Beskrivning"]) + "\n"
        place = "| " + str(row["Ort, foto"]) + "\n"
        motif = "| " + str(row["Motivord"]) + "\n"
        person = "| " + str(row["Personnamn / avbildad"]) + "\n"
        searchw = "| " + str(row["Sökord"])
        not_ok_row += link
        not_ok_row += desc
        not_ok_row += place
        not_ok_row += motif
        not_ok_row += person
        not_ok_row += "|-\n"
        not_ok_file.write(not_ok_row)
        
    
    print("New filename: {}".format(new_filename))
    print()
    print(infotext)
    print()
    print("<nowiki>\n")
    print(categories)
    print("</nowiki>")
    
    return no_content_categories


# In[24]:

mexiko = pickle.load(open("./mexiko_df_final.pickle","rb"))
#print("Loaded DataFrame from 'mexiko_df_final.pickle' OK")
filenames_file = open("./mexiko_filenames_mappings.csv","w")
filenames_file.write("Original|Commons\n")
no_content_categories = 0

not_ok_file = open("./no_ok_to_upload.info","a")
not_ok_table = ""
header_row = """{| class="wikitable sortable" style="width: 60%; height: 200px;"
        ! Image
        ! Description
        ! Place
        ! Keywords
        ! Depicted person
        ! Search terms
        |-\n"""
footer_row = "\n|}"   
not_ok_file.write(header_row)

for row_index, row in mexiko.iterrows():
    no_content_category = create_infofiles(row, filenames_file, not_ok_file)
    no_content_categories += no_content_category
    #print("Stats: \nTotal images {}\nOK images {}\nUncategorized images {}\nImages missing author {}".format(total_images, OK_images - faulty_images, uncategorized_images, faulty_images ))
#print("Total Stats: \nTotal images {}\nOK images {}\nUncategorized images {}\nImages missing author {}".format(total_images, OK_images - faulty_images, uncategorized_images, faulty_images ))
not_ok_file.write(footer_row)
not_ok_file.close()
print("Uncategorized images: {}".format(no_content_categories))


# In[ ]:



