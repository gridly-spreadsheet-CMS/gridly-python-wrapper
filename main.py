"""
    Main module.
"""
import argparse
import configs
import _export
import _import

IMPORT_DATA_OPT = 'import'
EXPORT_OPT = 'export'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to work with Gridly via XML/JSON file')

    parser.add_argument('-o', '--option', choices=['import', 'export'], action='store', required=True,
                        help="Please select either 'import' or 'export'")

    args = parser.parse_args()
    action = args.option

    # Load config before running scripts
    configs.init()

    if action == IMPORT_DATA_OPT:
        _import.import_data()
    elif action == EXPORT_OPT:
        _export.export()
    else:
        print('Should not go here ^.^')
