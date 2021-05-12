"""Implement a class that will manage interactions with the user"""
import controller

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
        answer = parse(answer.split())
        return answer


def parse(list_of_strings):
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
