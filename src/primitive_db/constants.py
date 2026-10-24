"""Shared constants for commands, storage, types, and messages"""

META_FILE = "db_meta.json"
DATA_DIRECTORY = "data"

VALID_TYPES = {"int": int, "str": str, "bool": bool}
ID_COLUMN_NAME = "ID"
ID_COLUMN_TYPE = "int"

EXIT_COMMAND = "exit"
HELP_COMMAND = "help"
CREATE_TABLE_COMMAND = "create_table"
DROP_TABLE_COMMAND = "drop_table"
LIST_TABLES_COMMAND = "list_tables"
INSERT_COMMAND = "insert"
SELECT_COMMAND = "select"
UPDATE_COMMAND = "update"
DELETE_COMMAND = "delete"
INFO_COMMAND = "info"

DATA_COMMANDS = (
    INSERT_COMMAND,
    SELECT_COMMAND,
    UPDATE_COMMAND,
    DELETE_COMMAND,
    INFO_COMMAND,
)

SIMPLE_COMMANDS = (
    EXIT_COMMAND,
    HELP_COMMAND,
    LIST_TABLES_COMMAND,
    CREATE_TABLE_COMMAND,
    DROP_TABLE_COMMAND,
)

INVALID_VALUE_MESSAGE = (
    "Некорректное значение: {value}. Попробуйте снова."
)

HELP_MESSAGE = """
***Процесс работы с таблицей***
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу

***Операции с данными***
Функции:
<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) \
- создать запись.
<command> select from <имя_таблицы> where <столбец> = <значение> \
- прочитать записи по условию.
<command> select from <имя_таблицы> - прочитать все записи.
<command> update <имя_таблицы> set <столбец1> = <новое_значение1> \
where <столбец_условия> = <значение_условия> - обновить запись.
<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.
<command> info <имя_таблицы> - вывести информацию о таблице.

Общие команды:
<command> exit - выход из программы
<command> help - справочная информация
"""
