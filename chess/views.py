"""Implement a class that will manage interactions with the user"""
from models.translate import TRANSLATION

ASK_ARGUMENT = TRANSLATION["ask_argument"]
FIX_ARGUMENT = TRANSLATION["fix_argument"]


class View:
    def __init__(self):
        pass

    @staticmethod
    def display(text):
        """Write text in the console."""
        print(text)

    @staticmethod
    def ask(text):
        """Return the input of an user after a question."""
        answer = input(text).strip()
        return answer

    @staticmethod
    def ask_command(text):
        """Return a tuple that contains a command and its arguments."""
        answer = input(text)
        return parse(answer)

    @staticmethod
    def ask_argument(argument):
        """Return an input from the user for a specific argument."""
        answer = input(ASK_ARGUMENT[argument]).strip()
        return answer

    @staticmethod
    def ask_correct_argument(argument):
        """Return an input from the user for a specific argument that was invalid."""
        answer = input(FIX_ARGUMENT[argument]).strip()
        return answer


def parse(param_string):
    """Parse a string to get a command and arguments from it."""
    param = param_string.split("--")
    command_name = TRANSLATION["command_names"][param[0].strip().lower()]
    param = [parameter.split() for parameter in param]
    kwargs = {TRANSLATION["argument_names"][param[i][0].lower()]: " ".join(param[i][1:]) for i in range(1, len(param))}
    return command_name, kwargs
