import os
import sys
import stat
from datetime import datetime
import math
import csv
import argparse

fieldnames = [
    # CUSTOM
    "File_Name", "Full_Path", "Date_Modified", "Size", "Type",
    # ATTRIBUTES
    "st_mode", "st_ino", "st_dev", "st_nlink", "st_uid", "st_gid", "st_size",
    # TIMESTAMPS
    "st_atime", "st_mtime", "st_ctime", "st_atime_ns", "st_mtime_ns", "st_ctime_ns",
    # ATTRIBUTES ON MISC SYSTEMS
    "st_blocks", "st_blksize", "st_rdev", "st_flags", "st_gen", "st_birthtime",
    "st_fstype", "st_ftype", "st_attrs", "st_obtype", "st_rsize", "st_creator",
    "st_type", "st_file_attributes"
]


def walktree(top, callback):
    # From Python documentation
    '''recursively descend the directory tree rooted at top,
       calling the callback function for each regular file'''

    for f in os.listdir(top):
        pathname = os.path.join(top, f)
        current_stat = os.stat(pathname)
        mode = current_stat.st_mode
        if stat.S_ISDIR(mode):
            # It's a directory, recurse into it
            walktree(pathname, callback)
        elif stat.S_ISREG(mode):
            # It's a file, call the callback function
            callback(pathname, current_stat)
        else:
            # Unknown file type, print a message
            print('Skipping %s' % pathname)


def stat_object_to_dictionary(stat_obj):
    result = dict((field, getattr(stat_obj, field, None))
                  for field in fieldnames)
    return result


def convert_time(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S %f')


def get_human_mtime(stat_obj):
    return convert_time(stat_obj.st_mtime)


def get_human_size(stat_obj):
    size_bytes = stat_obj.st_size
    # From https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    result = "{size}{unit}".format(size=s, unit=size_name[i])
    return result


def get_type(stat_obj):
    mode = stat_obj.st_mode
    if stat.S_ISREG(mode):
        return "file"
    if stat.S_ISDIR(mode):
        return "directory"
    else:
        return "unknown"


def get_stat_dict(file_path, stat_obj):
    stat_dict = stat_object_to_dictionary(stat_obj)
    stat_dict["File_Name"] = os.path.basename(file_path)
    stat_dict["Full_Path"] = os.path.abspath(file_path)
    stat_dict["Date_Modified"] = get_human_mtime(stat_obj)
    stat_dict["Size"] = get_human_size(stat_obj)
    stat_dict["Type"] = get_type(stat_obj)
    return stat_dict


def add_csv_row(callback):
    def with_action(file_path, stat_obj):
        stat_dict = get_stat_dict(file_path, stat_obj)
        callback(stat_dict)
        print("Read {}".format(file_path))
    return with_action


def scan_folder(args):

    if args.append is False:
        if os.path.exists(args.output):
            os.remove(args.output)

    csvFile = open(args.output, 'a', newline='')
    writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
    if not args.append:
        writer.writeheader()
    walktree(args.folder, add_csv_row(writer.writerow))
    csvFile.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Creates csv record of files in given folder.')
    parser.add_argument("folder", help='Base folder to parse')
    parser.add_argument("--append", action='store_true',
                        help='Append to output file', default=False)
    parser.add_argument(
        "-o", "--output", help="output filename", default="Files.csv")

    args = parser.parse_args()

    scan_folder(args)
