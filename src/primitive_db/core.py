from primitive_db import constants
from primitive_db.decorators import confirm_action, handle_db_errors, log_time


def _parse_columns(columns):
    """Parse column definitions and prepend the integer ID column

    Examples:
        ['name:str', 'age:int'] -> {'ID': 'int', 'name': 'str', 'age': 'int'}
        ['name:str', 'ID:int'] -> {'ID': 'int', 'name': 'str'}
        ['age:float'] -> ValueError (unsupported type)
    """
    if not columns:
        raise ValueError(
            constants.INVALID_VALUE_MESSAGE.format(
                value=constants.MISSING_COLUMNS_MESSAGE
            )
        )

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
            raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=column))

        parsed_columns[column_name] = column_type

    return {constants.ID_COLUMN_NAME: constants.ID_COLUMN_TYPE, **parsed_columns}


def validate_table_name(table_name):
    """Require a nonempty table name containing ASCII letters, digits, or underscores"""
    if not table_name or not table_name.isascii() or not all(
        character.isalnum() or character == "_" for character in table_name
    ):
        raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=table_name))


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Create a table and return updated metadata"""
    validate_table_name(table_name=table_name)

    if table_name in metadata:
        raise ValueError(
            constants.TABLE_ALREADY_EXISTS_MESSAGE.format(table_name=table_name)
        )

    metadata[table_name] = _parse_columns(columns=columns)
    return metadata


@handle_db_errors
@confirm_action(action_name=constants.DROP_TABLE_ACTION)
def drop_table(metadata, table_name):
    """Drop a table and return updated metadata"""
    validate_table_name(table_name=table_name)

    if table_name not in metadata:
        raise ValueError(
            constants.TABLE_NOT_FOUND_MESSAGE.format(table_name=table_name)
        )

    del metadata[table_name]
    return metadata


def validate_value(value, column_type):
    """Raise ValueError if a value does not match its declared type"""
    # bool is a subclass of int, so isinstance(True, int) would not work here
    if type(value) is not constants.VALID_TYPES[column_type]:
        raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=value))


@handle_db_errors
@log_time
def insert(metadata, table_name, table_data, values):
    """Insert typed values and return updated table data"""
    if table_name not in metadata:
        raise ValueError(
            constants.TABLE_NOT_FOUND_MESSAGE.format(table_name=table_name)
        )

    columns = {
        name: column_type
        for name, column_type in metadata[table_name].items()
        if name != constants.ID_COLUMN_NAME
    }

    if len(values) != len(columns):
        raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=values))

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


def filter_records(table_data, where_clause=None):
    """Return matching records without logging or changing the data"""
    if where_clause is None:
        return table_data

    return [
        record for record in table_data
        if _matches_where(record=record, where_clause=where_clause)
    ]


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Return all records or only those matching the conditions"""
    return filter_records(table_data=table_data, where_clause=where_clause)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Return updated records without changing the original table data"""
    updated_data = []

    for record in table_data:
        updated_record = record.copy()

        if _matches_where(record=record, where_clause=where_clause):
            updated_record.update(set_clause)

        updated_data.append(updated_record)

    return updated_data


@handle_db_errors
@confirm_action(action_name=constants.DELETE_RECORDS_ACTION)
def delete(table_data, where_clause):
    """Return table data without records matching the conditions"""
    return [
        record for record in table_data
        if not _matches_where(record=record, where_clause=where_clause)
    ]
