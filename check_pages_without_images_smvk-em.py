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

bad_images = []


def add_deletion_template(page):
    """
    Fetch text from pywikibot filePage (since it's on Commons) object
    and add a template for speedy deletation to top, save it and
    return success message or error message.

    :rtype: string
    """
    current_infotext = page.latest_revision.text
    new_infotext = "{{speedydelete|broken file upload}}\n" + current_infotext
    print("--- {}\n{}\n".format(page,new_infotext))

for page in gen:
    filePage = pywikibot.FilePage(page)
    try:
        print(filePage.fileIsShared())
    except pywikibot.exceptions.PageRelatedError as e:
        match = fname_patt.search(str(e))
        # print(match.group(1))
        add_deletion_template(page)

        bad_images.append(match.group(1))

print(len(bad_images))
