import shlex

import prompt

from primitive_db.core import INVALID_VALUE_MESSAGE, create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

META_FILE = "db_meta.json"
EXIT_COMMAND = "exit"
HELP_COMMAND = "help"
CREATE_TABLE_COMMAND = "create_table"
DROP_TABLE_COMMAND = "drop_table"
LIST_TABLES_COMMAND = "list_tables"
VALID_COMMANDS = (
    EXIT_COMMAND,
    HELP_COMMAND,
    CREATE_TABLE_COMMAND,
    DROP_TABLE_COMMAND,
    LIST_TABLES_COMMAND,
)


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Read commands, manage table schemas, and persist metadata."""
    print_help()

    while True:
        metadata = load_metadata(filepath=META_FILE)
        user_input = prompt.string("Введите команду: ").strip()

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(INVALID_VALUE_MESSAGE.format(value=user_input))
            continue

        if not args:
            continue

        command, *arguments = args

        if command not in VALID_COMMANDS:
            print(f"Функции {command} нет. Попробуйте снова.")
            continue

        if (
            (command in (EXIT_COMMAND, HELP_COMMAND, LIST_TABLES_COMMAND) and arguments)
            or (command == CREATE_TABLE_COMMAND and len(arguments) < 2)
            or (command == DROP_TABLE_COMMAND and len(arguments) != 1)
        ):
            print(INVALID_VALUE_MESSAGE.format(value=user_input))
            continue

        updated_metadata = None

        if command == EXIT_COMMAND:
            return
        elif command == HELP_COMMAND:
            print_help()
        elif command == LIST_TABLES_COMMAND:
            if not metadata:
                print("Таблиц пока нет.")
            for table_name in metadata:
                print(f"- {table_name}")
        elif command == CREATE_TABLE_COMMAND:
            table_name, *columns = arguments
            updated_metadata = create_table(
                metadata=metadata, table_name=table_name, columns=columns
            )
        elif command == DROP_TABLE_COMMAND:
            updated_metadata = drop_table(
                metadata=metadata, table_name=arguments[0]
            )

        if updated_metadata is not None:
            save_metadata(filepath=META_FILE, data=updated_metadata)
