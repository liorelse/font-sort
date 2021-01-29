#!/usr/bin/python3
import sys
import os
from fontTools import ttLib
from shutil import (copyfile, move)
from contextlib import redirect_stderr


def index_in_list(index: int, check_list: list) -> bool:
    length = len(check_list)
    return -length <= index < length


def font_details(file_path: str):
    """Get ttf and otf details from font file"""
    try:
        font = ttLib.TTFont(file_path, ignoreDecompileErrors=True)
    except ttLib.TTLibError:
        return
    with redirect_stderr(None):
        names = font["name"].names
    details = {}
    for name in names:
        if name.langID == 0 or name.langID == 1033:
            try:
                details[name.nameID] = name.toUnicode()
            except UnicodeDecodeError:
                details[name.nameID] = name.string.decode(errors="ignore")
    name, family, style = ("",) * 3
    if 4 in details.keys():
        name = details[4]
    if 16 in details.keys():
        family = details[16]
    elif 1 in details.keys():
        family = details[1]
    if 2 in details.keys():
        style = details[2]
    return name, family, style


def path_create(path: str):
    if path:
        if not os.path.exists(path):
            path_list = path.replace("\\", "/").split("/")
            if path_list[-1] == "":
                del path_list[-1]
            current = ""
            for directory in path_list:
                if len(directory) == 2 and directory[-1] == ":":
                    directory = f"{directory}\\"
                current = os.path.join("", current, directory)
                if not os.path.exists(current):
                    try:
                        os.mkdir(current)
                    except OSError as error:
                        print(error)


def move_files(source_folder: str, library: str):
    source_folder = source_folder.replace("\\", "/")
    library = library.replace("\\", "/")
    name, family, style = (None,) * 3
    for root, sub_folders, files in os.walk(source_folder):
        for file in files:
            source_file = os.path.join(root, file)
            try:
                name, family, style = font_details(source_file)
            except TypeError:
                continue
            index_folder = family[0].upper()
            if index_folder.isnumeric():
                index_folder = '0..9'
            dest_folder = os.path.join(library, index_folder, family)
            ext = file.split(".")[-1].lower()
            font_name = f"{name}.{ext}"
            dest_file = os.path.join(dest_folder, font_name)
            num = 1
            while os.path.exists(dest_file):
                dest_folder = dest_folder + f" {num}"
                dest_file = os.path.join(dest_folder, font_name)
                num = +num
            path_create(dest_folder)
            copyfile(source_file, dest_file)


def main():
    source_folder = sys.argv[1]
    library = sys.argv[2]
    print(f"Source folder: {source_folder}\nDestination folder: {library}")
    move_files(source_folder, library)


if __name__ == "__main__":
    main()
