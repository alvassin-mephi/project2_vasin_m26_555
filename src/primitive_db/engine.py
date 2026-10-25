import prompt

WELCOME_TEXT = "Первая попытка запустить проект!\n\n***"
HELP_TEXT = (
    "<command> exit - выйти из программы\n"
    "<command> help - справочная информация"
)
COMMAND_PROMPT = "Введите команду: "
EXIT_COMMAND = "exit"
HELP_COMMAND = "help"


def welcome():
    """Display the welcome message and handle user commands."""
    print(WELCOME_TEXT)
    print(HELP_TEXT)

    while True:
        command = prompt.string(COMMAND_PROMPT).strip()

        if command == EXIT_COMMAND:
            return
        elif command == HELP_COMMAND:
            print(f"\n{HELP_TEXT}")
