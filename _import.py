"""
    Import module.
"""

import sys
from pathlib import Path
import utils
import api
import urls
import strategy
import logging
import configs
from api import HTTP_STATUS

DEFAULT_XML_IMPORT_STRATEGY = strategy.DefaultXmlImportStrategy()
DEFAULT_JSON_IMPORT_STRATEGY = strategy.DefaultJsonImportStrategy()
DEFAULT_PO_IMPORT_STRATEGY = strategy.DefaultPoImportStrategy()
logger = logging.getLogger(__name__)

#####
# Validate properties in setup.yml
#####
def __validate_config(config_properties):
    if 'api-key' not in config_properties:
        logger.error("api-key is missing. Please add 'api-key' property in setup.yml.")
        sys.exit()

    if 'import' not in config_properties:
        logger.error("import configurations are missing. Please add 'import' property in setup.yml.")
        sys.exit()

    if 'data-directory' not in config_properties['import']:
        logger.error("import data-directory is missing. Please add 'import.data-directory' property in setup.yml.")
        sys.exit()

    if 'grids' not in config_properties['import']:
        logger.error("import grid(s) is missing. Please add 'import.grids' property in setup.yml.")
        sys.exit()

    grids = config_properties['import']['grids']
    has_default_grid = False
    for grid in grids:
        if 'name' not in grid:
            logger.error("grid name is missing. Please add 'import.grids.name' in setup.yml")
            sys.exit()
        if 'view-id' not in grid:
            logger.error("grid view-id is missing. Please add 'import.grids.view-id' in setup.yml")
            sys.exit()
        if 'default' in grid:
            has_default_grid = grid['default']

    if not has_default_grid:
        logger.error("Default grid is missing. Please set one grid with 'import.grids.default=true' in setup.yml")
        sys.exit()

    if 'files' not in config_properties['import']:
        logger.error("file(s) is missing. Please add 'import.files' in setup.yml")
        sys.exit()

    if 'mappings' not in config_properties['import']['files']:
        logger.error("file mapping(s) is missing. Please add 'import.files.mappings' in setup.yml")
        sys.exit()

    file_mappings = config_properties['import']['files']['mappings']
    file_path = (".xml", ".json", ".po")
    for file_mapping in file_mappings:
        if 'file-name' not in file_mapping:
            logger.error("file-name is missing. Please add 'import.files.mappings.file-name' in setup.yml")
            sys.exit()

        if 'file-name' in file_mapping and not file_mapping['file-name'].endswith(file_path):
            logger.error("file must be json file. Please add 'import.files.mappings.file-name' in setup.yml")
            sys.exit()

        if 'column-id' not in file_mapping:
            logger.error("column-id is missing. Please add 'import.files.mappings.column-id' in setup.yml")
            sys.exit()

#####
# Get file(s) to import
#####
def __get_files_to_import(base_dir, file_mappings):
    base_path = Path(base_dir)
    files_in_base_path = base_path.iterdir()

    files_return = []
    for item in files_in_base_path:
        if item.is_file() and item.suffix in ('.xml', '.json', '.po') and not __get_file_mapping(item.name, file_mappings) is None:
            files_return.append(item)

    return files_return

#####
# Get file(s) mapping
#####
def __get_file_mapping(file_name, file_mappings):
    for file_mapping in file_mappings:
        if file_mapping['file-name'] == file_name:
            return file_mapping
    return None

#####
# Get grid in Gridly
#####
def __get_grid_to_import(record_id, grids):
    default_grid = None
    for grid in grids:
        if not grid.get('default', False):
            if 'path' in grid and grid['path'] in record_id:
                return grid
        else:
            default_grid = grid

    return default_grid

#####
# Do post request
#####
def __do_post(api_key, grid, records):
    url = urls.set_record_url(grid['view-id'])
    response = api.post_json(api_key, url, records)
    if response.status_code == HTTP_STATUS['CREATED']:
        logger.info(f'Successfully create {len(response.json())} record(s)')

    elif response.status_code == HTTP_STATUS['NOT_FOUND']:
        logger.error(
            f'Failed create records for grid {grid["name"]}, return-code: {response.status_code}, details: {response.text}')
        exit()
    else:
        logger.error(
            f'Failed create records for grid {grid["name"]}, return-code: {response.status_code}, details: {response.text}')
    records.clear()

#####
# Import xml/json file(s) to a grid in Gridly
#####
def import_data():
    config_properties = utils.load_yml_file('config/setup.yml')
    __validate_config(config_properties)

    api_key = config_properties['api-key']
    import_properties = config_properties['import']
    file_properties = import_properties['files']
    grids = import_properties['grids']
    import_directory = import_properties['data-directory']
    file_mappings = file_properties['mappings']

    # Start import file
    files_to_import = __get_files_to_import(import_directory, file_mappings)
    for file in files_to_import:
        logger.info(f'Importing file {file.name}...')

        file_name = file.name
        
        # Check the file format before import the data to the grid
        if '.xml' in file.name:
            data = utils.load_xml_file(f"{import_directory}/{file_name}")

            file_mapping = __get_file_mapping(file_name, file_mappings)
            if file_mapping is None:
                return

            extracted_records = DEFAULT_XML_IMPORT_STRATEGY.read(file_mapping['column-id'], data, '')
        elif '.json' in file.name:
            data = utils.load_json_file(f"{import_directory}/{file_name}")
            
            file_mapping = __get_file_mapping(file_name, file_mappings)
            if file_mapping is None:
                return

            extracted_records = DEFAULT_JSON_IMPORT_STRATEGY.read(file_mapping['column-id'], data, '')
        elif '.po' in file.name:
            data = utils.load_po_file(f"{import_directory}/{file_name}")
            dict = {}
            for entry in data:
                key = entry.msgid 
                value = entry.msgstr
                dict[key] = value

            file_mapping = __get_file_mapping(file_name, file_mappings)
            if file_mapping is None:
                return

            extracted_records = DEFAULT_PO_IMPORT_STRATEGY.read(file_mapping['column-id'], dict, '')
        else: 
            logger.warning("Something went wrong!")

        length = len(extracted_records)
        if length == 0:
            return

        record = extracted_records[0]
        current_grid = __get_grid_to_import(record.id, grids)
        working_records = [record]

        loop = 1
        while loop < length:
            record = extracted_records[loop]
            grid = __get_grid_to_import(record.id, grids)

            if grid != current_grid:
                __do_post(api_key, current_grid, working_records)
                current_grid = grid

            if len(working_records) >= configs.import_chunk_size():
                __do_post(api_key, current_grid, working_records)

            working_records.append(extracted_records[loop])

            loop += 1

        if working_records:
            __do_post(api_key, current_grid, working_records)
