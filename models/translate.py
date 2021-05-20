"""Implement functions to translate strings according to a pre-existing dictionary"""
from json import load
with open("fr.json", "r") as file:
    data = load(file)


def translate(text, translations):
    if text in translations:
        return translations[text]
    else:
        raise ValueError


def translate_commands(text):
    return translate(text, data["command_names"])


def translate_arguments(text):
    return translate(text, data["argument_names"])
