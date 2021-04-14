"""
    Export module.
"""

import sys
import logging
from pathlib import Path
import utils
import grid_objects
import api
import urls
import time
import strategy
import configs
import xml.etree.ElementTree as ET

from api import HTTP_STATUS
from typing import Dict
from requests import Response

DEFAULT_XML_EXPORT_STRATEGY = strategy.DefaultXmlExportStrategy()
DEFAULT_JSON_EXPORT_STRATEGY = strategy.DefaultJsonExportStrategy()

logger = logging.getLogger(__name__)

#####
# Validate properties in setup.yml
#####
def __validate_config(config_properties):
    if 'api-key' not in config_properties:
        logger.error("api-key is missing. Please add 'api-key' property in setup.yml.")
        sys.exit()

    if 'export' not in config_properties:
        logger.error("export configurations are missing. Please add 'export' property in setup.yml.")
        sys.exit()

    if 'directory' not in config_properties['export']:
        logger.error("export directory is missing. Please add 'export.directory' property in setup.yml.")
        sys.exit()

    if 'grids' not in config_properties['export']:
        logger.error("export grid(s) is missing. Please add 'export.grids' property in setup.yml.")
        sys.exit()

    grids = config_properties['export']['grids']
    for grid in grids:
        if 'name' not in grid:
            logger.error("grid name is missing. Please add 'export.grids.name' in setup.yml")
            sys.exit()
        if 'view-id' not in grid:
            logger.error("grid view-id is missing. Please add 'export.grids.view-id' in setup.yml")
            sys.exit()

    if 'files' not in config_properties['export']:
        logger.error("file(s) is missing. Please add 'export.files' in setup.yml")
        sys.exit()

    if 'mappings' not in config_properties['export']['files']:
        logger.error("file mapping(s) is missing. Please add 'export.files.mappings' in setup.yml")
        sys.exit()

    file_mappings = config_properties['export']['files']['mappings']
    file_path = (".xml", ".json")
    for file_mapping in file_mappings:
        if 'file-name' not in file_mapping:
            logger.error("file-name is missing. Please add 'export.files.mappings.file-name' in setup.yml")
            sys.exit()

        if 'file-name' in file_mapping and not file_mapping['file-name'].endswith(file_path):
            logger.error("file must be json file. Please add 'export.files.mappings.file-name' in setup.yml")
            sys.exit()

        if 'column-id' not in file_mapping:
            logger.error("column-id is missing. Please add 'export.files.mappings.column-id' in setup.yml")
            sys.exit()

#####
# Paste the response
#####
def __parse_response(response: Response, root: Dict, api_key, url, retry_times):
    """
            Paste response
    """
    config_properties = utils.load_yml_file('config/setup.yml')
    __validate_config(config_properties)

    file_mappings = config_properties['export']['files']['mappings']

    if retry_times >= configs.max_fetch_retry():
        logger.error(f'Request to {urls.unquote(url)} has reached maximum of retries')
        return

    if response.status_code == HTTP_STATUS['OK']:
        records = response.json()
        for file_mapping in file_mappings:
            if 'file-name' in file_mapping and file_mapping['file-name'].endswith('.xml'):
                DEFAULT_XML_EXPORT_STRATEGY.build(root, records)
            elif 'file-name' in file_mapping and file_mapping['file-name'].endswith('.json'):
                DEFAULT_JSON_EXPORT_STRATEGY.build(root, records)
            else: 
                logger.warning("Stupid man ...")

        if 'Link' in response.headers and 'next' in response.links:
            url = response.links['next']['url']
            response = api.get(api_key, url)
            __parse_response(response, root, api_key, url, 0)

    elif response.status_code == HTTP_STATUS['TOO_MANY_REQUESTS']:
        time.sleep(1)
        response = api.get(api_key, url)
        __parse_response(response, root, api_key, url, retry_times + 1)

    else:
        logger.error(
            f'Request to {urls.unquote(url)} has returned code {response.status_code}, details: {response.text}')

#####
# Export the grid content to xml/json file(s)
#####
def export():
    """
        Export data from grids in setup.yml to xml/json file(s)
    """
    config_properties = utils.load_yml_file('config/setup.yml')
    __validate_config(config_properties)

    api_key = config_properties['api-key']
    export_properties = config_properties['export']
    grids = export_properties['grids']
    file_mappings = export_properties['files']['mappings']
    export_directory = export_properties['directory']

    utils.create_dir_if_not_exists(export_directory)

    combine = True
    if 'combine' in export_properties:
        combine = export_properties['combine']

    # Start export file
    for file_mapping in file_mappings:
        column_id = file_mapping['column-id']
        file_name = file_mapping['file-name']
        
        # Check the file format before export the data to the file
        if 'file-name' in file_mapping and file_mapping['file-name'].endswith('.xml'):
            root = ET.Element("texts")
            for grid in grids:
                url = urls.get_record_url(grid['view-id'], [column_id], grid_objects.Page(configs.fetch_limit()))
                response = api.get(api_key, url)
                __parse_response(response, root, api_key, url, 0)

                export_path = f"{export_directory}/{grid['name']}_{file_name}"
                utils.dump_to_xml_file(export_path, root)
                root = ET.Element("texts")

                logger.info(f'Exported data to {export_path}')
        elif 'file-name' in file_mapping and file_mapping['file-name'].endswith('.json'):
            root = {}
            for grid in grids:
                url = urls.get_record_url(grid['view-id'], [column_id], grid_objects.Page())
                response = api.get(api_key, url)
                __parse_response(response, root, api_key, url, 0)

                if not combine:
                    if 'lang' in file_mapping:
                        root.setdefault('name', file_mapping['lang'])

                    export_path = f"{export_directory}/{grid['name']}_{file_name}"
                    utils.dump_to_json_file(export_path, root)
                    root = {}

                    logger.info(f'Exported data to {export_path}')

            if combine:
                if 'lang' in file_mapping:
                    root.setdefault('name', file_mapping['lang'])

                export_path = f"{export_directory}/{file_name}"
                utils.dump_to_json_file(export_path, root)

                logger.info(f'Exported data to {export_path}')
        else:
            logger.warning("Please stop it!!!!")

