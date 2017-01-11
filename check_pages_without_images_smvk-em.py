#!/usr/bin/env python

import re

import pywikibot
from pywikibot import pagegenerators as pg

site = pywikibot.Site(fam="commons")
cat = pywikibot.Category(site, 'Category:Media_from_the_National_Museums_of_World_Culture')
gen = pg.CategorizedPageGenerator(cat)

example_error = """
loadimageinfo: Query on [[commons:File:Från utgrävningarna vid Xolalpan - SMVK - 0307.a.0164.b.tif]] returned no imageinfo"""
fname_patt = re.compile(r'\[\[commons\:(File:[\w \_\-\.\,\(\)]+)\]\]')

# test regular expression
# test_match = fname_patt.search(example_error)
# print(test_match.group(1))
tot_images = 0
bad_images = 0

def add_deletion_template(page):
    """
    Fetch text from pywikibot filePage (since it's on Commons) object
    and add a template for speedy deletion to top,

    :rtype: string
    """
    current_infotext = page.latest_revision.text
    new_infotext = "{{speedydelete|broken file upload}}\n" + current_infotext
    print("--- Added deletion template to file {}\n{}\n".format(page,new_infotext))
    return new_infotext

for page in gen:
    tot_images += 1
    filePage = pywikibot.FilePage(page)
    print("Total number of files checked: {}".format(tot_images), end="\r")
    try:
        filePage.fileIsShared()
    except pywikibot.exceptions.PageRelatedError as e:
        bad_images += 1
        print("Bad image no {} error: {}".format(bad_images, filePage))
        match = fname_patt.search(str(e))
        # print(match.group(1))
        new_infotext = add_deletion_template(page)
        filePage.text = new_infotext
        # filePage.save("Add template for speedy deletion due to no image uploaded, only text")

print("Total number of bad images: {}".format(len(bad_images)))
