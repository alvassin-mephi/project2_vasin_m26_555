"""Decorators and a cache closure for database operations"""

import json
import time

import prompt

from primitive_db import constants


def handle_db_errors(func):
    """Print database errors and return None when an operation fails"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(constants.DATA_FILE_NOT_FOUND_MESSAGE)
        except KeyError as error:
            print(constants.KEY_NOT_FOUND_MESSAGE.format(key=error))
        except json.JSONDecodeError as error:
            print(constants.INVALID_VALUE_MESSAGE.format(value=error))
        except ValueError as error:
            print(error)
        except Exception as error:
            print(constants.UNEXPECTED_ERROR_MESSAGE.format(error=error))

    return wrapper


def confirm_action(action_name):
    """Require a y response before executing the decorated operation"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                prompt=constants.CONFIRM_ACTION_PROMPT.format(action_name=action_name),
                empty=True,
            )
            if answer != constants.CONFIRMATION_ANSWER:
                return

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Print the execution time of a successful function call in seconds"""
    def wrapper(*args, **kwargs):
        started_at = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - started_at

        print(constants.LOG_TIME_MESSAGE.format(
            function_name=func.__name__, elapsed=elapsed
        ))
        return result

    return wrapper


def create_cacher():
    """Create a cache function with a clear method and a dictionary in a closure"""
    cache = {}

    def cache_result(key, value_func):
        """Return a cached result or compute it without caching None"""
        if key not in cache:
            result = value_func()
            # None signals a failed query; [] is valid and must be cached
            if result is None:
                return

            cache[key] = result

        return cache[key]

    def clear():
        """Clear all cached query results"""
        cache.clear()

    # Functions can have attributes; this exposes the clear closure
    # Both closures use the same cache dictionary
    cache_result.clear = clear
    return cache_result
