# Модуль "База данных"

Домашнее задание №2. Консольное приложение для управления таблицами.

## Установка и запуск

Требуются Python >= 3.12 и uv.

```bash
git clone https://github.com/alvassin-mephi/project2_vasin_m26_555.git
cd project2_vasin_m26_555
uv sync
uv run database
```

## Управление таблицами

| Команда | Описание |
| --- | --- |
| `create_table <имя_таблицы> <столбец:тип> ...` | Создать таблицу с указанными столбцами |
| `list_tables` | Показать список таблиц |
| `drop_table <имя_таблицы>` | Удалить таблицу |
| `help` | Показать справку |
| `exit` | Завершить работу |

Поддерживаемые типы столбцов: `int`, `str`, `bool`.
Столбец `ID:int` добавляется автоматически и всегда располагается первым.

Пример команд после запуска приложения:

```text
create_table users name:str age:int is_active:bool
list_tables
drop_table users
exit
```

Схемы таблиц сохраняются в `db_meta.json` в текущем рабочем каталоге.

## Демонстрация
asciinema: https://asciinema.org/a/7GrmNiKHzNCNw3BI
