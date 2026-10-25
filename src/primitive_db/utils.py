import json
import os

from primitive_db import constants


def load_metadata(filepath):
    """Load metadata or return an empty dictionary if the file is missing"""
    try:
        with open(filepath, mode="r") as fd:
            return json.load(fd)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Save table metadata to a JSON file"""
    with open(filepath, mode="w") as fd:
        json.dump(data, fd)


def load_table_data(table_name):
    """Load table records or return an empty list if the file is missing"""
    filepath = os.path.join(
        constants.DATA_DIRECTORY,
        constants.TABLE_FILENAME_TEMPLATE.format(table_name=table_name),
    )

    try:
        with open(filepath, mode="r") as fd:
            return json.load(fd)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Save table records to a JSON file"""
    os.makedirs(constants.DATA_DIRECTORY, exist_ok=True)
    filepath = os.path.join(
        constants.DATA_DIRECTORY,
        constants.TABLE_FILENAME_TEMPLATE.format(table_name=table_name),
    )

    with open(filepath, mode="w") as fd:
        json.dump(data, fd)


def delete_table_data(table_name):
    """Delete a table data file if it exists"""
    filepath = os.path.join(
        constants.DATA_DIRECTORY,
        constants.TABLE_FILENAME_TEMPLATE.format(table_name=table_name),
    )

    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
