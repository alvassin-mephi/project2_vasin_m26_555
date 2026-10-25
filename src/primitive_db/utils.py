import json


def load_metadata(filepath):
    """Load metadata or return an empty dictionary if the file is missing."""
    try:
        with open(filepath, mode="r") as metadata_file:
            return json.load(metadata_file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Save table metadata to a JSON file."""
    with open(filepath, mode="w") as metadata_file:
        json.dump(data, metadata_file)
