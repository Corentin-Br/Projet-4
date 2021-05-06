"""Implement a class that will manage interactions with the user"""


class View:
    def __init__(self):
        pass

    def display(self, text):
        print(text)

    def ask(self, text):
        answer = input(text)
        return answer

    def ask_command(self, text):
        answer = input(text)
        answer = find_keywords(answer.split())
        return answer


def find_keywords(list_of_strings):
    working_list = list_of_strings.copy()
    command = working_list.pop(0)
    args = []
    kwargs = {}
    for i in range(working_list):
        string = working_list[i]
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
