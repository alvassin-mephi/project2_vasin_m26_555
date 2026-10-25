import prompt
from prettytable import PrettyTable

from primitive_db import constants
from primitive_db.core import (
    TableAlreadyExistsError,
    TableNotFoundError,
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
    validate_table_name,
    validate_value,
)
from primitive_db.parser import UnknownCommandError, parse_command
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


def _run_table_command(metadata, command, table_name, parameters):
    """Execute a table command and save metadata after changes"""
    updated_metadata = None

    if command == constants.LIST_TABLES_COMMAND:
        if not metadata:
            print("Таблиц пока нет.")
        for table_name in metadata:
            print(f"- {table_name}")
    elif command == constants.CREATE_TABLE_COMMAND:
        updated_metadata = create_table(
            metadata=metadata,
            table_name=table_name,
            columns=parameters["columns"],
        )
    elif command == constants.DROP_TABLE_COMMAND:
        updated_metadata = drop_table(
            metadata=metadata, table_name=table_name
        )
        delete_table_data(table_name=table_name)

    if updated_metadata is not None:
        save_metadata(filepath=constants.META_FILE, data=updated_metadata)

        if command == constants.CREATE_TABLE_COMMAND:
            columns_description = ", ".join(
                f"{name}:{column_type}"
                for name, column_type in updated_metadata[table_name].items()
            )
            print(
                f'Таблица "{table_name}" успешно создана со столбцами: '
                f"{columns_description}"
            )
        else:
            print(f'Таблица "{table_name}" успешно удалена.')


def _run_data_command(metadata, command, table_name, parameters):
    """Validate and execute a parsed data command"""
    validate_table_name(table_name=table_name)

    if table_name not in metadata:
        raise TableNotFoundError(table_name)

    columns = metadata[table_name]

    if constants.ID_COLUMN_NAME in parameters.get("set_clause", {}):
        raise ValueError(constants.ID_COLUMN_NAME)

    for clause_name in ("where_clause", "set_clause"):
        for column_name, value in parameters.get(clause_name, {}).items():
            if column_name not in columns:
                raise ValueError(column_name)

            validate_value(value=value, column_type=columns[column_name])

    table_data = load_table_data(table_name=table_name)

    if command == constants.INSERT_COMMAND:
        table_data = insert(
            metadata=metadata,
            table_name=table_name,
            table_data=table_data,
            values=parameters["values"],
        )
        save_table_data(table_name=table_name, data=table_data)
        record_id = table_data[-1][constants.ID_COLUMN_NAME]
        print(f'Запись с ID={record_id} успешно добавлена в таблицу "{table_name}".')
        return

    if command == constants.INFO_COMMAND:
        columns_description = ", ".join(
            f"{name}:{column_type}" for name, column_type in columns.items()
        )
        print(f"Таблица: {table_name}")
        print(f"Столбцы: {columns_description}")
        print(f"Количество записей: {len(table_data)}")
        return

    where_clause = parameters.get("where_clause")
    matching_records = select(table_data=table_data, where_clause=where_clause)

    if command == constants.SELECT_COMMAND:
        result = PrettyTable()
        result.field_names = list(columns)
        for record in matching_records:
            result.add_row([record[column_name] for column_name in columns])
        print(result)
        return

    if not matching_records:
        print("Записи не найдены.")
        return

    if command == constants.UPDATE_COMMAND:
        table_data = update(
            table_data=table_data,
            set_clause=parameters["set_clause"],
            where_clause=where_clause,
        )
    elif command == constants.DELETE_COMMAND:
        table_data = delete(table_data=table_data, where_clause=where_clause)

    save_table_data(table_name=table_name, data=table_data)

    for record in matching_records:
        record_id = record[constants.ID_COLUMN_NAME]
        if command == constants.UPDATE_COMMAND:
            print(
                f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.'
            )
        else:
            print(
                f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".'
            )


def run():
    """Read commands, manage tables, and persist metadata and records"""
    print_help()

    while True:
        user_input = prompt.string("Введите команду: ").strip()
        if not user_input:
            continue

        try:
            command, table_name, parameters = parse_command(user_input=user_input)

            if command == constants.EXIT_COMMAND:
                return

            if command == constants.HELP_COMMAND:
                print_help()
                continue

            metadata = load_metadata(filepath=constants.META_FILE)

            if command in constants.DATA_COMMANDS:
                _run_data_command(
                    metadata=metadata,
                    command=command,
                    table_name=table_name,
                    parameters=parameters,
                )
            else:
                _run_table_command(
                    metadata=metadata,
                    command=command,
                    table_name=table_name,
                    parameters=parameters,
                )

        except UnknownCommandError as error:
            print(f"Функции {error} нет. Попробуйте снова.")

        except TableAlreadyExistsError as error:
            print(f'Ошибка: Таблица "{error}" уже существует.')

        except TableNotFoundError as error:
            print(f'Ошибка: Таблица "{error}" не существует.')

        except ValueError as error:
            print(constants.INVALID_VALUE_MESSAGE.format(value=error))
