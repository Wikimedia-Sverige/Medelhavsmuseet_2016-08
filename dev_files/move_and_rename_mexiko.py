#!/usr/bin/python
# -*- coding: utf-8  -*-
# Ugly fix of relative path imports difference in Python 2 and 3
from sys import path
from os.path import dirname as dir
path.append(dir(path[0]))

import os
from shutil import copyfile
import batchupload.csv_methods as csv_methods
import batchupload.helpers as helpers
import batchupload.common as common
import batchupload.prepUpload as prep
"""Load filenames_mapping then identify the matching files and rename them.
Basic usage: python DecArch_2016-08/moveAndRename.py
"""


def load_data(in_file):
    """Load csv file.
    @param in_data: the path to the metadata file
    @return: dict, list
    """
    header = u'Original|Commons'
    key_col = (u'Original')
    data = csv_methods.csv_file_to_dict(in_file, key_col, header)
    return (data)


def find_all_files(base_dir, sub_dir):
    """Find potential files (in corresponding folder).
    @param base_dir: the path to the directory where the folders are expected
    @param sub_dir: list of sub-dirs we are expecting
    @param out_dir: name of the directory where output files should be placed
    @param data: the data loaded from the csv
    @return: dict
    """
    file_exts = (u'.tif', u'.jpg', u'.tiff', u'.jpeg')

    files = {}
    for folder in sub_dir:
        folder_path = common.modify_path(base_dir, folder)
        if not os.path.isdir(folder_path):
            continue  # e.g. if already deleted
        for filename in os.listdir(folder_path):
            name, ext = os.path.splitext(filename)
            if ext.lower() in file_exts:
                label = u'{}:{}'.format(folder, name)
                files[label] = os.path.join(folder_path, filename)
    return files


def move_matching_files(files, data, out_dir):
    """Rename and move matching files.
    @param files: output from find_all_files
    @param data: the data loaded from the csv
    @param out_dir: path of the directory where output files should be placed
    """
    common.create_dir(out_dir)
    for key, in_path in files.iteritems():
        if key in data.keys():
            path_name, ext = os.path.splitext(in_path)
            file_name_out = u'{}{}'.format(data[key][u'Commons'], ext)
            out_path = common.modify_path(out_dir, file_name_out)
            # Switched to os.renames from Andŕes os.rename since it causes error:
            # Not removing non-empty directory: ... 
            os.renames(in_path, out_path) 


def copy_info_files(info_dir, data, out_dir):
    """Checks all info files are present and copies them to the file directory.
    @param info_dir: path to the directory where the info files are expected
    @param data: the data loaded from the csv
    @param out_dir: path of the directory where output files should be placed
    """
    for val in data.values():
        file_name = u'{}.info'.format(val['Commons'])
        in_file = common.modify_path(info_dir, file_name)
        if os.path.isfile(in_file):
            out_file = common.modify_path(out_dir, file_name)
            copyfile(in_file, out_file)
        else:
            print(u'{} is missing'.format(file_name))


def main(*args):
    """Command line entry point"""
    in_file = u'/home/mos/Dropbox/wmse/batchuploads/BatchUploadTools/batches/Medelhavsmuseet_2016-08/mexiko_filenames_mappings.csv'
    info_dir = u'/home/mos/Dropbox/wmse/batchuploads/BatchUploadTools/batches/Medelhavsmuseet_2016-08/infofiles/'
    base_dir = u'/media/mos/My Passport/Wikimedia/Mexiko'
    out_dir = u'renamed'

    for arg in args:
        option, sep, value = arg.partition(':')
        if option == '-in_file':
            in_file = helpers.convertFromCommandline(value)
        elif option == '-base_dir':
            base_dir = helpers.convertFromCommandline(value)
        elif option == '-out_dir':
            out_dir = helpers.convertFromCommandline(value)
        elif option == '-info_dir':
            info_dir = helpers.convertFromCommandline(value)

    out_dir = common.modify_path(base_dir, out_dir)
    data = load_data(in_file)
    files = find_all_files(base_dir)
    move_matching_files(files, data, out_dir)
    prep.removeEmptyDirectories(base_dir)
    copy_info_files(info_dir, data, out_dir)
    print('Done')

if __name__ == "__main__":
    main()