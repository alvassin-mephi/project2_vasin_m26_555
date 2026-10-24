import shlex

from primitive_db import constants


def _tokenize(user_input):
    """Split a command into tokens while preserving quoted strings

    Examples:
        '("Ivan Petrov",28)' -> ['(', '"Ivan Petrov"', ',', '28', ')']
        'age=28' -> ['age', '=', '28']
    """
    tokens = []
    position = 0

    while position < len(user_input):
        character = user_input[position]

        if character.isspace():
            position += 1
            continue

        if character in "(),=":
            tokens.append(character)
            position += 1
            continue

        start = position

        if character in "\"'":
            quote = character
            position += 1

            while position < len(user_input):
                character = user_input[position]

                if character == "\\":
                    position += 2
                elif character == quote:
                    position += 1
                    break
                else:
                    position += 1
            else:
                raise ValueError(
                    constants.INVALID_VALUE_MESSAGE.format(value=user_input)
                )
        else:
            while (
                position < len(user_input)
                and not user_input[position].isspace()
                and user_input[position] not in "(),=\"'"
            ):
                position += 1

        tokens.append(user_input[start:position])

    return tokens


def _parse_value(value):
    """Convert a token to a Python string, integer, or boolean

    Examples:
        '28' -> 28
        'true' -> True
        'FALSE' -> False
        '"Ivan"' -> 'Ivan'
        '"28"' -> '28'
    """
    if value.startswith(("'", '"')):
        text = value[1:-1]
        characters = []
        position = 0

        while position < len(text):
            character = text[position]

            if character == "\\":
                position += 1
                character = constants.STRING_ESCAPES.get(
                    text[position], "\\" + text[position]
                )

            characters.append(character)
            position += 1

        return "".join(characters)

    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    try:
        return int(value)
    except ValueError:
        raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=value)) from None


def parse_values(value_tokens):
    """Validate and convert value tokens for an insert command

    Tokens exclude the surrounding parentheses and contain values separated
    by commas. Return a list of Python strings, integers, or booleans.
    Raise ValueError if a separator or value is invalid.

    Examples:
        ['"Ivan"', ',', '28', ',', 'true'] -> ['Ivan', 28, True]
        ['"Ivan"', '28'] -> ValueError (missing comma)
    """
    if value_tokens and (
        len(value_tokens) % 2 == 0
        or any(token != "," for token in value_tokens[1::2])
    ):
        raise ValueError(
            constants.INVALID_VALUE_MESSAGE.format(
                value="(" + " ".join(value_tokens) + ")"
            )
        )

    return [_parse_value(value=value) for value in value_tokens[::2]]


def parse_clause(column_name, value):
    """Build a column-value condition from parsed tokens

    Examples:
        parse_clause('age', '28') -> {'age': 28}
        parse_clause('name', '"Ivan"') -> {'name': 'Ivan'}
    """
    return {column_name: _parse_value(value=value)}


def _parse_simple_command(user_input):
    """Parse and validate a general or table management command"""
    try:
        command, *arguments = shlex.split(user_input)
    except ValueError:
        raise ValueError(
            constants.INVALID_VALUE_MESSAGE.format(value=user_input)
        ) from None

    if command in (
        constants.EXIT_COMMAND,
        constants.HELP_COMMAND,
        constants.LIST_TABLES_COMMAND,
    ):
        if arguments:
            raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=user_input))

        return command, None, {}

    if command == constants.CREATE_TABLE_COMMAND:
        if len(arguments) < 2:
            raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=user_input))

        return command, arguments[0], {"columns": arguments[1:]}

    if command == constants.DROP_TABLE_COMMAND:
        if len(arguments) != 1:
            raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=user_input))

        return command, arguments[0], {}

    raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=user_input))


def parse_data_command(user_input):
    """Return a command name, table name, and parsed parameters"""
    tokens = _tokenize(user_input=user_input)

    # Check the command structure and extract the table name, columns, and values
    # *value_tokens collects the tokens inside parentheses into a list
    match tokens:
        case [
            constants.INSERT_COMMAND,
            "into", table_name,
            "values", "(", *value_tokens, ")",
        ]:
            parameters = {"values": parse_values(value_tokens=value_tokens)}

        case [
            constants.SELECT_COMMAND,
            "from", table_name
        ]:
            parameters = {}

        case [
            constants.INFO_COMMAND,
            table_name
        ]:
            parameters = {}

        case [
            constants.SELECT_COMMAND,
            "from", table_name,
            "where", column, "=", value,
        ]:
            parameters = {
                "where_clause": parse_clause(column_name=column, value=value)
            }

        case [
            constants.DELETE_COMMAND,
            "from", table_name,
            "where", column, "=", value,
        ]:
            parameters = {
                "where_clause": parse_clause(
                    column_name=column, value=value
                )
            }

        case [
            constants.UPDATE_COMMAND,
            table_name,
            "set", set_column, "=", set_value,
            "where", where_column, "=", where_value,
        ]:
            parameters = {
                "set_clause": parse_clause(
                    column_name=set_column, value=set_value
                ),
                "where_clause": parse_clause(
                    column_name=where_column, value=where_value
                ),
            }

        case _:
            raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=user_input))

    if table_name.startswith(("'", '"')):
        table_name = _parse_value(value=table_name)

    return tokens[0], table_name, parameters


def parse_command(user_input):
    """Return the command name, optional table name, and parsed parameters"""
    parts = user_input.split(maxsplit=1)
    if not parts:
        raise ValueError(constants.INVALID_VALUE_MESSAGE.format(value=user_input))

    command = parts[0]
    if command in constants.SIMPLE_COMMANDS:
        return _parse_simple_command(user_input=user_input)

    if command in constants.DATA_COMMANDS:
        return parse_data_command(user_input=user_input)

    raise ValueError(constants.UNKNOWN_COMMAND_MESSAGE.format(command=command))
