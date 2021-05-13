"""Implement a class that will manage interactions with the user"""


class View:
    def __init__(self):
        pass

    def display(self, text):
        """Write text in the console"""
        print(text)

    def ask(self, text):
        """Return the input of an user after a question"""
        answer = input(text)
        return answer

    def ask_command(self, text):
        """Return a tuple that contains a command and its arguments"""
        answer = input(text)
        answer = parse(answer.split())
        return answer


def parse(list_of_strings):
    """Parse a string to get a command and arguments from it"""
    working_list = list_of_strings.copy()
    command = working_list.pop(0)
    args = []
    kwargs = {}
    for i, string in enumerate(working_list):
        string = string.lower()
        if string == "ignore":
            continue
        if string.startswith("--") and i < len(working_list)-1:
            kwargs[string] = working_list[i+1]
            working_list[i+1] = "ignore"
        elif string.startswith("--") and i == len(working_list)-1:
            args.append(string.strip("-"))
        else:
            args.append(string)
    return command, args, kwargs
