"""
   Utilities
"""
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import filetype 
import json
import jsonpickle
import yaml
import polib
from typing import Dict

logger = logging.getLogger(__name__)

#####
# Read the json file
#####
def load_json_file(file_path):
    """
        load json file
    """
    with open(file_path, "r", encoding="utf8") as json_file:
        return json.load(json_file)

#####
# Read the yaml file
#####
def load_yml_file(file_path):
    """
        load yaml file
    """
    with open(file_path, "r") as yml_file:
        return yaml.full_load(yml_file)

#####
# Read the xml file 
#####
def load_xml_file(file_path):
    """
        load xml file
    """
    tree = ET.parse(file_path)
    return tree.getroot()

#####
# Read the po file 
#####
def load_po_file(file_path): 
    """
        load po file
    """
    pofile = polib.pofile(file_path)
    return pofile

#####
# Write the dictionary to a json file
#####
def dump_to_json_file(file_path, obj: Dict):
    """
        write object as json to file
    """
    with open(file_path, "w", encoding="utf8") as write_file:
        json.dump(obj, write_file, indent=4, sort_keys=True, ensure_ascii=False)

#####
# Write the xml content to a xml file
#####
def dump_to_xml_file(file_path, root: Dict):
    """
        write object as xml to file
    """
    reparsed = minidom.parseString(ET.tostring(root, 'utf-8'))
    with open(file_path, "w", encoding="utf8") as text_file:
        text_file.write(reparsed.toprettyxml(indent="  "))


def get_deep(_dict, keys, default=None):
    for key in keys:
        if isinstance(_dict, dict):
            _dict = _dict.get(key, default)
        else:
            return default
    return _dict


def get_base_file_name(file_name):
    index = file_name.rindex('.')
    if index <= 0:
        return file_name

    return file_name[:index]


def get_file_name(file_path):
    return os.path.basename(file_path)


def get_content_type(file_path):
    kind = filetype.guess(file_path)
    if kind is not None:
        return kind.mime
    return None


def encode_to_json(obj):
    return jsonpickle.encode(obj, unpicklable=False)


def decode_from_json(json):
    return jsonpickle.decode(json)


def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_string_after(str, after):
    index = str.index(after)
    if index >= 0:
        return str[index + 1:]
    return None


def does_file_exist(file_path):
    return Path(file_path).is_file()


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_next_key(map: Dict, key):
    if key not in map:
        map[key] = 1
        return key

    index = map[key]
    map[key] = index + 1

    new_key = f"{key}({index})"
    logger.warning(f"Key {key} already exists. Replace with this new key {new_key}")
    return new_key

