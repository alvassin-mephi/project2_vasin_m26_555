from primitive_db import constants


class TableAlreadyExistsError(Exception):
    """Indicate that a table with the given name already exists"""


class TableNotFoundError(Exception):
    """Indicate that a table with the given name does not exist"""


def _parse_columns(columns):
    """Parse column definitions and prepend the integer ID column"""
    if not columns:
        raise ValueError("столбцы не указаны")

    parsed_columns = {}

    for column in columns:
        column_name, separator, column_type = column.partition(":")

        if (
            not separator
            or not column_name.strip()
            or column_type not in constants.VALID_TYPES
            or column_name in parsed_columns
            or (
                column_name == constants.ID_COLUMN_NAME
                and column_type != constants.ID_COLUMN_TYPE
            )
        ):
            raise ValueError(column)

        parsed_columns[column_name] = column_type

    return {constants.ID_COLUMN_NAME: constants.ID_COLUMN_TYPE, **parsed_columns}


def validate_table_name(table_name):
    """Require a nonempty table name containing ASCII letters, digits, or underscores"""
    if not table_name or not table_name.isascii() or not all(
        character.isalnum() or character == "_" for character in table_name
    ):
        raise ValueError(table_name)


def create_table(metadata, table_name, columns):
    """Create a table and return updated metadata"""
    validate_table_name(table_name=table_name)

    if table_name in metadata:
        raise TableAlreadyExistsError(table_name)

    metadata[table_name] = _parse_columns(columns=columns)
    return metadata


def drop_table(metadata, table_name):
    """Drop a table and return updated metadata"""
    validate_table_name(table_name=table_name)

    if table_name not in metadata:
        raise TableNotFoundError(table_name)

    del metadata[table_name]
    return metadata


def validate_value(value, column_type):
    """Raise ValueError if a value does not match its declared type"""
    if type(value) is not constants.VALID_TYPES[column_type]:
        raise ValueError(value)


def insert(metadata, table_name, table_data, values):
    """Insert typed values and return updated table data"""
    if table_name not in metadata:
        raise TableNotFoundError(table_name)

    columns = {
        name: column_type
        for name, column_type in metadata[table_name].items()
        if name != constants.ID_COLUMN_NAME
    }

    if len(values) != len(columns):
        raise ValueError(values)

    for column_type, value in zip(columns.values(), values):
        validate_value(value=value, column_type=column_type)

    ids = [record[constants.ID_COLUMN_NAME] for record in table_data]
    record_id = max(ids, default=0) + 1
    record = {constants.ID_COLUMN_NAME: record_id, **dict(zip(columns, values))}
    table_data.append(record)

    return table_data


def _matches_where(record, where_clause):
    """Check whether a record matches all conditions"""
    return all(
        record[column_name] == value
        for column_name, value in where_clause.items()
    )


def select(table_data, where_clause=None):
    """Return all records or only those matching the conditions"""
    if where_clause is None:
        return table_data

    return [
        record for record in table_data
        if _matches_where(record=record, where_clause=where_clause)
    ]


def update(table_data, set_clause, where_clause):
    """Return updated records without changing the original table data"""
    updated_data = []

    for record in table_data:
        updated_record = record.copy()

        if _matches_where(record=record, where_clause=where_clause):
            updated_record.update(set_clause)

        updated_data.append(updated_record)

    return updated_data


def delete(table_data, where_clause):
    """Return table data without records matching the conditions"""
    return [
        record for record in table_data
        if not _matches_where(record=record, where_clause=where_clause)
    ]
