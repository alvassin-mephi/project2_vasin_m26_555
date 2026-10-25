import json

import prompt
from prettytable import PrettyTable

from primitive_db import constants
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    filter_records,
    insert,
    select,
    update,
    validate_table_name,
    validate_value,
)
from primitive_db.decorators import create_cacher, handle_db_errors
from primitive_db.parser import parse_command
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Print the available table and data commands"""
    print(constants.HELP_MESSAGE)


def _run_table_command(metadata, command, table_name, parameters, cache_result):
    """Run a table command and clear the cache after saving changes"""
    updated_metadata = None

    if command == constants.LIST_TABLES_COMMAND:
        if not metadata:
            print(constants.NO_TABLES_MESSAGE)
        for table_name in metadata:
            print(f"- {table_name}")
    elif command == constants.CREATE_TABLE_COMMAND:
        updated_metadata = create_table(
            metadata=metadata,
            table_name=table_name,
            columns=parameters["columns"],
        )
    elif command == constants.DROP_TABLE_COMMAND:
        validate_table_name(table_name=table_name)
        if table_name not in metadata:
            raise ValueError(
                constants.TABLE_NOT_FOUND_MESSAGE.format(table_name=table_name)
            )

        updated_metadata = drop_table(
            metadata=metadata, table_name=table_name
        )

    if updated_metadata is not None:
        if command == constants.DROP_TABLE_COMMAND:
            delete_table_data(table_name=table_name)

        save_metadata(filepath=constants.META_FILE, data=updated_metadata)
        cache_result.clear()

        if command == constants.CREATE_TABLE_COMMAND:
            columns_description = ", ".join(
                f"{name}:{column_type}"
                for name, column_type in updated_metadata[table_name].items()
            )
            print(constants.TABLE_CREATED_MESSAGE.format(
                table_name=table_name, columns_description=columns_description,
            ))
        else:
            print(constants.TABLE_DROPPED_MESSAGE.format(table_name=table_name))


def _select_records(table_name, where_clause, cache_result):
    """Return cached records or load and select them on a cache miss"""
    cache_key = (table_name, json.dumps(where_clause, sort_keys=True))

    return cache_result(
        key=cache_key,
        # Read and filter the file only when the result is not cached.
        value_func=lambda: select(
            table_data=load_table_data(table_name=table_name),
            where_clause=where_clause,
        ),
    )


def _validate_data_command(metadata, table_name, parameters):
    """Validate the table and clause values and return its columns"""
    validate_table_name(table_name=table_name)

    if table_name not in metadata:
        raise ValueError(
            constants.TABLE_NOT_FOUND_MESSAGE.format(table_name=table_name)
        )

    columns = metadata[table_name]

    if constants.ID_COLUMN_NAME in parameters.get("set_clause", {}):
        raise ValueError(
            constants.INVALID_VALUE_MESSAGE.format(value=constants.ID_COLUMN_NAME)
        )

    for clause_name in ("where_clause", "set_clause"):
        for column_name, value in parameters.get(clause_name, {}).items():
            if column_name not in columns:
                raise ValueError(
                    constants.INVALID_VALUE_MESSAGE.format(value=column_name)
                )

            validate_value(value=value, column_type=columns[column_name])

    return columns


def _save_table_changes(table_name, table_data, cache_result):
    """Save table records and clear the cache after a successful write"""
    save_table_data(table_name=table_name, data=table_data)
    cache_result.clear()


def _find_matching_records(table_data, where_clause):
    """Find records for an update or deletion and report an empty result"""
    matching_records = filter_records(
        table_data=table_data, where_clause=where_clause,
    )

    if not matching_records:
        print(constants.NO_RECORDS_MESSAGE)

    return matching_records


def _handle_insert(metadata, table_name, values, cache_result):
    """Insert a record, save changes, and print its ID"""
    table_data = load_table_data(table_name=table_name)
    table_data = insert(
        metadata=metadata,
        table_name=table_name,
        table_data=table_data,
        values=values,
    )
    if table_data is None:
        return

    _save_table_changes(
        table_name=table_name, table_data=table_data, cache_result=cache_result,
    )
    record_id = table_data[-1][constants.ID_COLUMN_NAME]
    print(constants.RECORD_INSERTED_MESSAGE.format(
        record_id=record_id, table_name=table_name,
    ))


def _handle_select(columns, table_name, where_clause, cache_result):
    """Select records through the cache and print them as a table"""
    matching_records = _select_records(
        table_name=table_name,
        where_clause=where_clause,
        cache_result=cache_result,
    )
    if matching_records is None:
        return

    result = PrettyTable()
    result.field_names = list(columns)
    for record in matching_records:
        result.add_row([record[column_name] for column_name in columns])
    print(result)


def _handle_update(table_name, set_clause, where_clause, cache_result):
    """Update matching records, save changes, and print their IDs"""
    table_data = load_table_data(table_name=table_name)
    matching_records = _find_matching_records(
        table_data=table_data, where_clause=where_clause,
    )
    if not matching_records:
        return

    table_data = update(
        table_data=table_data, set_clause=set_clause, where_clause=where_clause,
    )
    if table_data is None:
        return

    _save_table_changes(
        table_name=table_name, table_data=table_data, cache_result=cache_result,
    )
    for record in matching_records:
        print(constants.RECORD_UPDATED_MESSAGE.format(
            record_id=record[constants.ID_COLUMN_NAME], table_name=table_name,
        ))


def _handle_delete(table_name, where_clause, cache_result):
    """Delete matching records after confirmation and save the result"""
    table_data = load_table_data(table_name=table_name)
    matching_records = _find_matching_records(
        table_data=table_data, where_clause=where_clause,
    )
    if not matching_records:
        return

    table_data = delete(table_data=table_data, where_clause=where_clause)
    if table_data is None:
        return

    _save_table_changes(
        table_name=table_name, table_data=table_data, cache_result=cache_result,
    )
    for record in matching_records:
        print(constants.RECORD_DELETED_MESSAGE.format(
            record_id=record[constants.ID_COLUMN_NAME], table_name=table_name,
        ))


def _handle_info(table_name, columns):
    """Print the table schema and record count"""
    table_data = load_table_data(table_name=table_name)
    columns_description = ", ".join(
        f"{name}:{column_type}" for name, column_type in columns.items()
    )
    print(constants.TABLE_INFO_MESSAGE.format(
        table_name=table_name,
        columns_description=columns_description,
        record_count=len(table_data),
    ))


def _run_data_command(metadata, command, table_name, parameters, cache_result):
    """Validate a data command and call its handler"""
    columns = _validate_data_command(
        metadata=metadata, table_name=table_name, parameters=parameters,
    )

    match command:
        case constants.INSERT_COMMAND:
            _handle_insert(
                metadata=metadata,
                table_name=table_name,
                values=parameters["values"],
                cache_result=cache_result,
            )
        case constants.SELECT_COMMAND:
            _handle_select(
                columns=columns,
                table_name=table_name,
                where_clause=parameters.get("where_clause"),
                cache_result=cache_result,
            )
        case constants.UPDATE_COMMAND:
            _handle_update(
                table_name=table_name,
                set_clause=parameters["set_clause"],
                where_clause=parameters["where_clause"],
                cache_result=cache_result,
            )
        case constants.DELETE_COMMAND:
            _handle_delete(
                table_name=table_name,
                where_clause=parameters["where_clause"],
                cache_result=cache_result,
            )
        case constants.INFO_COMMAND:
            _handle_info(table_name=table_name, columns=columns)


@handle_db_errors
def _execute_command(command, table_name, parameters, cache_result):
    """Load metadata and execute a table or data command"""
    metadata = load_metadata(filepath=constants.META_FILE)

    if command in constants.DATA_COMMANDS:
        _run_data_command(
            metadata=metadata,
            command=command,
            table_name=table_name,
            parameters=parameters,
            cache_result=cache_result,
        )
    else:
        _run_table_command(
            metadata=metadata,
            command=command,
            table_name=table_name,
            parameters=parameters,
            cache_result=cache_result,
        )


def run():
    """Read commands, manage tables, and persist metadata and records"""
    print_help()
    cache_result = create_cacher()

    while True:
        user_input = prompt.string(constants.COMMAND_PROMPT).strip()
        if not user_input:
            continue

        try:
            command, table_name, parameters = parse_command(user_input=user_input)
        except ValueError as error:
            print(error)
            continue

        if command == constants.EXIT_COMMAND:
            return

        if command == constants.HELP_COMMAND:
            print_help()
            continue

        _execute_command(
            command=command,
            table_name=table_name,
            parameters=parameters,
            cache_result=cache_result,
        )
