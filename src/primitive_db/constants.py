"""Shared constants for commands, storage, types, and messages"""

META_FILE = "db_meta.json"
DATA_DIRECTORY = "data"
TABLE_FILENAME_TEMPLATE = "{table_name}.json"

VALID_TYPES = {"int": int, "str": str, "bool": bool}
ID_COLUMN_NAME = "ID"
ID_COLUMN_TYPE = "int"

STRING_ESCAPES = {
    "\\": "\\",
    '"': '"',
    "'": "'",
}

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

COMMAND_PROMPT = "Введите команду: "
NO_TABLES_MESSAGE = "Таблиц пока нет."
NO_RECORDS_MESSAGE = "Записи не найдены."
MISSING_COLUMNS_MESSAGE = "столбцы не указаны"

TABLE_CREATED_MESSAGE = (
    'Таблица "{table_name}" успешно создана со столбцами: {columns_description}'
)
TABLE_DROPPED_MESSAGE = 'Таблица "{table_name}" успешно удалена.'
RECORD_INSERTED_MESSAGE = (
    'Запись с ID={record_id} успешно добавлена в таблицу "{table_name}".'
)
RECORD_UPDATED_MESSAGE = (
    'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.'
)
RECORD_DELETED_MESSAGE = (
    'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".'
)
TABLE_INFO_MESSAGE = """Таблица: {table_name}
Столбцы: {columns_description}
Количество записей: {record_count}"""

INVALID_VALUE_MESSAGE = (
    "Некорректное значение: {value}. Попробуйте снова."
)

UNKNOWN_COMMAND_MESSAGE = "Функции {command} нет. Попробуйте снова."

TABLE_ALREADY_EXISTS_MESSAGE = 'Ошибка: Таблица "{table_name}" уже существует.'
TABLE_NOT_FOUND_MESSAGE = 'Ошибка: Таблица "{table_name}" не существует.'
DATA_FILE_NOT_FOUND_MESSAGE = (
    "Ошибка: Файл данных не найден. Возможно, база данных не инициализирована."
)
KEY_NOT_FOUND_MESSAGE = "Ошибка: Таблица или столбец {key} не найден."
UNEXPECTED_ERROR_MESSAGE = "Произошла непредвиденная ошибка: {error}"

DROP_TABLE_ACTION = "удаление таблицы"
DELETE_RECORDS_ACTION = "удаление записей"
CONFIRMATION_ANSWER = "y"
CONFIRM_ACTION_PROMPT = 'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '

LOG_TIME_MESSAGE = "Функция {function_name} выполнилась за {elapsed:.3f} секунд"

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
