import pandas as pd
import regex
from pandas import ExcelWriter

old_json = json.load(open("./mexiko_info_data.json"))

def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text

mexiko_converters = {
    "Fotonummer": strip,
    "Postnr": strip,
    "Motivord": strip,
    "Beskrivning": strip,
    "Land, foto": strip,
    "Region, foto": strip,
    "Ort, foto": strip,
    "Etnisk grupp, avb.": strip,
    "Fotodatum": strip,
    "Personnamn / fotograf": strip,
    "Personnamn / avbildad": strip,
    "Sökord": strip,
    "Händelse / var närvarande vid": strip,
    "Länk": strip}

mexiko_arkiv_converters = {
    "Arkiv"

}

mexiko_arkiv = pd.read_excel("excel-export.xls", sheetname="Mexiko-Arkiv") # All column names are strip:ed

has_archive_cards = []
has_archive_cards.extend(mexiko_arkiv["Fotonummer.1"].dropna().tolist())
has_archive_cards.extend(mexiko_arkiv["Fotonummer.2"].dropna().tolist())
has_archive_cards.extend(mexiko_arkiv["Fotonummer.3"].dropna().tolist())
has_archive_cards.extend(mexiko_arkiv["Fotonummer.4"].dropna().tolist())
has_archive_cards = [id_str.strip() for id_str in has_archive_cards] # Note: every id has a leading whitespace in metadat doc!

print(has_archive_cards)

def create_archive_card_smvk_em_link(fotonr, mexiko_arkiv):
    arkiv_id_row = mexiko_arkiv[mexiko_arkiv["Fotonummer"] == row["Fotonummer"]]
    arkiv_id = arkiv_id_row["Arkiv-id"]
    ac_url = arkiv_id_row["Länk"]
    left_side, slash, id_str = url.rpartition("/")
    ac_template = "{{SMVK-EM-link|1=?|2=" + id_str + "|3=" + arkiv_id
    return ac_template

for index, row in mexiko.iterrows():
    url = row["Länk"]
    fotonr = row["Fotonummer"]
    # first, slash, id_str = url.rpartition("/")
    # new_url = "[" + url + " Fotonummer: " + id_str + "]"
    # mexiko.loc[index, "wiki_url"] = new_url

    left_side, slash, id_str = url.rpartition("/")
    template = "{{SMVK-EM-link|1=foto|2=" + id_str + "|3=" + row["Fotonummer"] + "}}"
    mexiko.loc[index, "SMVK-EM-link"] = template

    ac_cols = ["Fotonummer","Fotonummer.1","Fotonummer.2","Fotonummer.3","Fotonummer.4","Fotonummer.5"]

    if fotonr in has_archive_cards:
        # print("fotonr is in has archive cards")

        ac_link = create_archive_card_smvk_em_link(fotonr, mexiko_arkiv)
        print("ac_link: {}".format(ac_link))
        
        mexiko_arkiv.loc[index, "archive_card"] = ac_template

        

#writer = ExcelWriter("mexiko-arkiv_with_appended_archive_card_link.xlsx")
#mexiko_arkiv.to_excel(writer, 'Mexiko-Arkiv')
#writer.save()