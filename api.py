"""
This module implements the Requests API.
"""

import requests
import logging
import utils
from urls import unquote

HTTP_STATUS = {
    'OK': 200,
    'CREATED': 201,
    'TOO_MANY_REQUESTS': 429,
    'NOT_FOUND': 404
}
logger = logging.getLogger(__name__)


def post_json(api_key, url, json_data):
    """ POST json request the specified url.

        :param api_key: (required)

        Usage::

        :return: requests.Response
    """
    json_string = utils.encode_to_json(json_data)

    logger.info(f'Post data to {unquote(url)}')
    logger.debug(f'payload = {json_string}')

    headers = {'Authorization': f'ApiKey {api_key}', 'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json_string)
    return response


def patch_json(api_key, url, json_data):
    """ POST json request the specified url.

        :param api_key: (required)

        Usage::

        :return: requests.Response
    """
    json_string = utils.encode_to_json(json_data)

    logger.info(f'Patch data to {unquote(url)}')
    logger.debug(f'payload = {json_string}')

    headers = {'Authorization': f'ApiKey {api_key}', 'Content-Type': 'application/json'}
    response = requests.patch(url, headers=headers, data=json_string)
    return response


def get(api_key, url):
    """ GET data from the specified url.

        :param api_key: (required)

        Usage::

        :return: requests.Response
    """
    logger.info(f'Get data from {unquote(url)}')

    headers = {'Authorization': f'ApiKey {api_key}', 'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    return response


def post_binary_file(api_key, url, file_path):
    """ GET data from the specified url.

        :param api_key: (required)

        Usage::

        :return: requests.Response
    """
    logger.info(f'Post binary file to {unquote(url)}')

    headers = {'Authorization': f'ApiKey {api_key}'}

    files = [
        ('file', (utils.get_file_name(file_path), open(file_path, 'rb'), utils.get_content_type(file_path)))
    ]
    response = requests.post(url, headers=headers, files=files)
    return response
