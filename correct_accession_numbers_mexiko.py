import pandas as pd
import json
import pywikibot
import time

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

    print("File no {} of {}".format(index, len(old_json.keys())))
    json_infotext = old_json[fotonr]["info"]

    time.sleep(3)
    try:
        current_page = pywikibot.Page(
            site, u"File:" + json_images[fotonr_plus_ext])
        # ensure latest revision
        commons_infotext = current_page.latest_revision.text
    except Exception as e:
            print(
                "It seems <fotonummer> {} is not uploaded? \
                \nError: {}\n".format(
                    fotonr, e))

    print(
        "old_source:\n{}\nnew_source:\n{}\n ".format(
            json_infotext, commons_infotext))

    try:
        current_page.text = json_infotext
        # current_page.save(u"Updated infotext from ./mexiko_info_data.json")

        print("old_infotext:\n{}\n\n-------- {} ---------\
            \naltered_page:\n{}\n\n".format(
            commons_infotext,
            json_images[fotonr_plus_ext],
            json_infotext)
        )
    except AttributeError as e:
        print("Error on commons file {} source field retrieval:\n{}".format(
            current_page, e))
        # print("current_source:\n{}".format(current_source))
