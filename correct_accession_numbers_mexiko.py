import pandas as pd
import json
import pywikibot
import time

log = open("./correct_accession_numbers.log","w")
no_alterations = 0

site = pywikibot.Site(fam="commons")

json_images = {}
for line in open("./mexiko_filenames_mappings.csv").readlines():
    original, commons = line.split("|")
    # print("original: {} commons: {}".format(original, commons))
    if not original == "original":
        json_images[original] = commons.strip()

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

for index, fotonr in enumerate(old_json.keys()):
    fotonr_plus_ext = fotonr + ".tif"
    json_infotext = old_json[fotonr]["info"]

    try:
        current_page = pywikibot.Page(
            site, u"File:" + json_images[fotonr_plus_ext])
        # ensure latest revision
        commons_infotext = current_page.latest_revision.text

        current_page.text = json_infotext

    except Exception as e:
            print(
                "It seems <fotonummer> {} is not uploaded? \
                \nError: {}\n".format(
                    fotonr, e))

    except AttributeError as e:
        print("Error on commons file {} source field retrieval:\n{}".format(
            current_page, e))
        # print("current_source:\n{}".format(current_source))

    if commons_infotext != json_infotext:
        time.sleep(1)
        no_alterations += 1
         # Dry-run to check quality ########
        #log.write("old_infotext:\n{}\n\n-------- {} ---------\
        #    \naltered_page:\n{}\n\n".format(
        #    commons_infotext,
        #    json_images[fotonr_plus_ext],
        #    json_infotext)
        #)

        # In production ###################
        current_page.save(u"Updated infotext from ./mexiko_info_data.json")
    else:
        pass

    print("File no {} of {}. Altered: {}".format(index, len(old_json.keys()), no_alterations))
log.close()
