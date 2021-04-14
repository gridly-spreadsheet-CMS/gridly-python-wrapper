import logging
import utils


script_configs = None


def __log_level():
    config_level = script_configs['log']['level']
    if config_level == 'DEBUG':
        return logging.DEBUG
    elif config_level == 'WARNING':
        return logging.WARNING
    else:
        return logging.INFO


def init():
    global script_configs
    script_configs = utils.load_yml_file('config/script.yml')
    log_mode = script_configs['log']['mode']
    if log_mode == 'FILE':
        logging.basicConfig(filename='log/app.log', filemode='w', format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                        level=__log_level())
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S',
                            level=__log_level())


def max_fetch_retry():
    return int(script_configs['max-fetch-retry'])


def import_chunk_size():
    return 1500


def fetch_limit():
    return 1500


def gridly_url():
    return script_configs['gridly-url']

