VALID_TYPES = ("int", "str", "bool")
ID_COLUMN_NAME = "ID"
ID_COLUMN_TYPE = "int"
INVALID_VALUE_MESSAGE = (
    "Некорректное значение: {value}. Попробуйте снова."
)


def _parse_columns(columns):
    """Parse column definitions and prepend the integer ID column."""
    if not columns:
        raise ValueError("столбцы не указаны")

    parsed_columns = {}

    for column in columns:
        column_name, separator, column_type = column.partition(":")

        if (
            not separator
            or not column_name.strip()
            or column_type not in VALID_TYPES
            or column_name in parsed_columns
            or (column_name == ID_COLUMN_NAME and column_type != ID_COLUMN_TYPE)
        ):
            raise ValueError(column)

        parsed_columns[column_name] = column_type

    return {ID_COLUMN_NAME: ID_COLUMN_TYPE, **parsed_columns}


def create_table(metadata, table_name, columns):
    """Create a table and return updated metadata, or None on invalid input."""
    if not table_name.strip():
        print(INVALID_VALUE_MESSAGE.format(value=table_name))
        return

    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return

    try:
        table_columns = _parse_columns(columns=columns)
    except ValueError as error:
        print(INVALID_VALUE_MESSAGE.format(value=error))
        return

    metadata[table_name] = table_columns
    columns_description = ", ".join(
        f"{column_name}:{column_type}"
        for column_name, column_type in table_columns.items()
    )
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        f"{columns_description}"
    )
    return metadata


def drop_table(metadata, table_name):
    """Drop a table and return updated metadata, or None if it does not exist."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata
