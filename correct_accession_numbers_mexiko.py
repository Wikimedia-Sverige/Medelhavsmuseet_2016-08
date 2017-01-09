import pandas as pd
import regex
import json
import pywikibot
import time

alteration_log = open("correct_accession_numbers.log", "w")

site = pywikibot.Site(fam="commons")

fname_map = {}
for line in open("./mexiko_filenames_mappings.csv").readlines():
    original, commons = line.split("|")
    # print("original: {} commons: {}".format(original, commons))
    if not original == "original":
        fname_map[original] = commons.strip()

old_json = json.load(open("./mexiko_info_data.json"))
new_json = old_json.copy()


def strip(text):
    '''Removes leading and trailing whitespace
    '''
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
# All column names are strip:ed
mexiko_arkiv = pd.read_excel("excel-export.xls", sheetname="Mexiko-Arkiv")

has_archive_cards = []
has_archive_cards.extend(mexiko_arkiv["Fotonummer.1"].dropna().tolist())
has_archive_cards.extend(mexiko_arkiv["Fotonummer.2"].dropna().tolist())
has_archive_cards.extend(mexiko_arkiv["Fotonummer.3"].dropna().tolist())
has_archive_cards.extend(mexiko_arkiv["Fotonummer.4"].dropna().tolist())
has_archive_cards = [id_str.strip() for id_str in has_archive_cards]  # Note: every id has a leading whitespace in metadat doc!

# print(has_archive_cards)

def create_archive_card_smvk_em_link(fotonr, mexiko_arkiv):
    arkiv_id_row = mexiko_arkiv[mexiko_arkiv["Fotonummer"] == row["Fotonummer"]]
    arkiv_id = arkiv_id_row["Arkiv-id"]
    ac_url = arkiv_id_row["Länk"]
    left_side, slash, id_str = url.rpartition("/")
    ac_template = "{{SMVK-EM-link|1=?|2=" + id_str + "|3=" + arkiv_id
    return ac_template

ac_cols = ["Fotonummer","Fotonummer.1","Fotonummer.2","Fotonummer.3","Fotonummer.4","Fotonummer.5"]

for index, fotonr in enumerate(old_json.keys()):
    print("File no {} of {}".format(index, len(old_json.keys())))
    if fotonr in has_archive_cards:
        #print("{} has archive card".format(fotonr))
        
        for col in ac_cols:
            #print(mexiko_arkiv[col])
            if fotonr in mexiko_arkiv[col].str.strip().dropna().tolist():
                ugly_fotonr = " " + fotonr # due to leading whitespace in original metadata
                result = mexiko_arkiv[mexiko_arkiv[col] == ugly_fotonr]["Länk"]
                link_string = result.values[0]
                #print("{} in in mexiko_arkiv col {}".format(fotonr, col))
                left, dummy, id_str = link_string.rpartition("/")
                #print("id_str: {} ".format(id_str))
                template = "{{SMVK-EM-link|1=arkiv|2=" + id_str + "|3=" + fotonr + "}}"
                #print("fotonr: {} {}".format(fotonr,template))
        
                old_infotext = old_json[fotonr]["info"]
                source_patt = regex.compile(r"\|source\W+=([ \w,\:<>\/\'\.\n{}|\=]+)permission") # note: catches the initial | of permission fild
                match = source_patt.search(old_infotext)
                new_source = "" 
                new_source += match.group(1).split("\n")[0] + "\n"
                new_source += match.group(1).split("\n")[1] + "\nRelated archive card: " + template
                new_source += match.group(1).split("\n")[2] + "\n"
                #print("old_source:\n{}\nnew_source:\n{}\n ".format(match.group(1), new_source))
                fotonr_plus_ext = fotonr + ".tif"
                if fotonr_plus_ext in fname_map:
                    time.sleep(3)
                    try:
                        current_page = pywikibot.Page(site, u"File:" + fname_map[fotonr_plus_ext])
                        current_infotext = current_page.latest_revision.text # ensure latest revision
                        current_match = source_patt.search(current_infotext)
                    except Exception as e:
                        print("It seems that <fotonummer> {} is not uploaded?\nError message: {}\n".format(fotonr, e))
                    try:
                        current_source = current_match.group(1)
                        altered_infotext = current_infotext.replace(current_source, new_source)
                        current_page.text = altered_infotext
                        current_page.save(u"Add link to archive card")
                        alteration_log.write("Appended archive card link {} to File:{}\n".format(template, fname_map[fotonr_plus_ext]))

                        #print("old_infotext:\n{}\n\n-------- {} ---------\naltered_page:\n{}\n\n".format(current_infotext, fname_map[fotonr_plus_ext], altered_infotext))
                    except AttributeError as e:
                        print("Error on commons file {} source field retrieval:\n{}".format(current_page, e))
                    #print("current_source:\n{}".format(current_source))
                else:
                    print("{} not in fname_map, thus wasn't good enough to be uploaded".format(fotonr))
alteration_log.close()


re.match("hej","jag är hej som")