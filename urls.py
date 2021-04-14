"""
This module is for getting request urls.
"""

import jsonpickle
from requests.utils import requote_uri
from typing import List
from typing import Dict
import urllib.parse
import configs


def quote(url):
    return requote_uri(url)


def unquote(url):
    return urllib.parse.unquote(url)


def set_record_url(view_id):
    """
        Url to set records
    """
    return f"{configs.gridly_url()}/v1/views/{view_id}/records"


def get_record_url(view_id, column_ids: List, page: Dict):
    """
        Url to gets record
    """
    url = f"{configs.gridly_url()}/v1/views/{view_id}/records"

    queries = []
    if column_ids:
        queries.append('columnIds=' + ','.join(column_ids))

    if page:
        queries.append('page=' + jsonpickle.encode(page, unpicklable=False))

    if queries:
        url = url + '?' + '&'.join(queries)

    return quote(url)


def add_binary_file_url(view_id, record_id, column_id):
    """
        Url to add binary file for specified record and column
    """
    url = f"{configs.gridly_url()}/v1/views/{view_id}/files?recordId={record_id}&columnId={column_id}"
    return quote(url)
