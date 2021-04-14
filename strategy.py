"""
    Strategy module to provide different ways of export and import data.
"""

import logging
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import List
from typing import Dict
from grid_objects import (Record, Cell)
import utils

logger = logging.getLogger(__name__)

#####
# Base class for export xml file
#####
class XmlExportStrategy(ABC):
    """
        Base class for XmlExportStrategy
    """

    @abstractmethod
    def build(self, root_node: Dict, records: List):
        pass

#####
# Mapping the grid content to xml objects
#####
class DefaultXmlExportStrategy(XmlExportStrategy):
    """
            DefaultXmlExportStrategy. This is served a specific case
    """
    def build(self, root: Dict, records: List):
        for record in records:
            group = root
            levels = record['id'].split('/')

            for level in levels[:-1]:
                if level:
                    found_group = group.find(f"./group[@name='{level}']")
                    if not found_group:
                        group = ET.SubElement(group, 'group')
                        group.attrib = {'name': level}
                    else:
                        group = found_group
            if record['cells']:
                if len(record['cells']) >= 1:
                    phrase = ET.SubElement(group, 'phrase')
                    phrase.attrib = {'name': levels[-1], 'text': record['cells'][0].get('value', '')}

        return root
#####
# Base class for export json file
#####
class JsonExportStrategy(ABC):
    """
        Base class for JsonExportStrategy
    """

    @abstractmethod
    def build(self, root_node: Dict, records: List):
        pass

#####
# Mapping the grid content to json objects
#####
class DefaultJsonExportStrategy(JsonExportStrategy):
    """
            DefaultJsonExportStrategy. This is served a specific case
    """
    def build(self, root_node: Dict, records: List):
        for record in records:
            node = root_node
            levels = record['id'].split('/')
            for level in levels[:-1]:
                if level:
                    node = node.setdefault(level, dict())
            if record['cells']:
                if len(record['cells']) == 1:
                    node.setdefault(levels[-1], record['cells'][0].get('value', ''))
                else:
                    node = node.setdefault(levels[-1], dict())
                    for cell in record['cells']:
                        node.setdefault(cell['columnId'], cell.get('value', ''))

            else:
                node.setdefault(levels[-1], '')

        return root_node

#####
# Base class for import xml file
#####
class XmlImportStrategy(ABC):
    """
        Base class for XmlImportStrategy
    """

    def read(self, column_id, tree: Dict, previous_path=''):
        records = []
        keys = {}
        self.extract(keys, records, column_id, tree, previous_path)
        return records

    @abstractmethod
    def extract(self, keys, records, column_id, tree: Dict, previous_path=''):
        pass

#####
# Mapping xml objects to records
#####
class DefaultXmlImportStrategy(XmlImportStrategy):
    """
                DefaultImportStrategy. This is served Xml case
    """
    def extract(self, keys: Dict, records: List, column_id, tree: Dict, previous_path=''):
        if len(tree) == 0:
            if 'text' in tree.attrib and tree.tag == 'phrase':
                key = utils.get_next_key(keys, utils.get_string_after(previous_path, '/'))
                records.append(Record(key, '', [Cell(column_id, tree.attrib['text'])]))
            else:
                logger.warning(f"Tag {tree.tag} in path {previous_path} is not 'phrase' tag.")
            logger.info(tree)
        else:
            for child in tree:
                if 'name' in child.attrib:
                    self.extract(keys, records, column_id, child, previous_path + "/" + child.attrib['name'])
                else:
                    logger.warning(f"Tag {child.tag} in path {previous_path} does not have 'name' attribute.")
                logger.info(tree)

#####
# Base class for import po file
#####
class PoImportStrategy(ABC):
    """
        Base class for PoImportStrategy
    """

    def read(self, column_id, obj: Dict, previous_path=''):
        records = []
        self.extract(records, column_id, obj, previous_path)
        return records
        
    @abstractmethod
    def extract(self, records, column_id, obj: Dict, previous_path=''):
        pass

#####
# Mapping po objects to records
#####
class DefaultPoImportStrategy(PoImportStrategy):
    """
                DefaultImportStrategy. This is served Po case
    """
    def extract(self, records: List, column_id, obj: Dict, previous_path=''):
        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{key}"
                self.extract(records, column_id, value, path)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                path = f"{i}"
                self.extract(records, column_id, value, path)
        else:
            records.append(
                Record(previous_path, previous_path[0:previous_path.rfind("/")], [Cell(column_id, obj)]))     

#####
# Base class for import json file
#####
class JsonImportStrategy(ABC):
    """
        Base class for JsonImportStrategy
    """

    def read(self, column_id, json_obj: Dict, previous_path=''):
        records = []
        self.extract(records, column_id, json_obj, previous_path)
        return records
        
    @abstractmethod
    def extract(self, records, column_id, json_obj: Dict, previous_path=''):
        pass

#####
# Mapping json objects to records
#####
class DefaultJsonImportStrategy(JsonImportStrategy):
    """
                DefaultImportStrategy. This is served Json case
    """
    def extract(self, records: List, column_id, obj: Dict, previous_path=''):
        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{previous_path}/{key}"
                self.extract(records, column_id, value, path)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                path = f"{previous_path}/{i}"
                self.extract(records, column_id, value, path)
        else:
            records.append(
                Record(previous_path, previous_path[0:previous_path.rfind("/")], [Cell(column_id, obj)]))
