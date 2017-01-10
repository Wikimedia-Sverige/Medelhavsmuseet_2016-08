#!/usr/bin/env python
import regex

image_patt = regex.compile(r'\[\[(File\:[\w \-\.\(\)]+)\]\]')
acc_num = open("./output_python_correct_accession_numbers_mexiko.py")
acc_num_lines = acc_num.readlines()
acc_num_saved = set()

for line in acc_num_lines:
    match = image_patt.search(line)
    try:
        acc_num_saved.add(match.group(1))
        #print(line, match.group(1))

    except AttributeError as e:
        pass # no match
        #print(line, e)

for index, file in enumerate(acc_num_saved):
    print("{} {}".format(index, file))

arch_cards = open("./output_python_correct_accession_numbers_mexiko.py")
arch_cards.readlines()
