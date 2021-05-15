"""Implement a class that will manage interactions with the user"""
import re


class View:
    def __init__(self):
        pass

    @staticmethod
    def display(text):
        """Write text in the console"""
        print(text)

    @staticmethod
    def ask(text):
        """Return the input of an user after a question"""
        answer = input(text)
        return answer

    @staticmethod
    def ask_command(text):
        """Return a tuple that contains a command and its arguments"""
        answer = input(text)
        answer = parse(answer)
        return answer

    @staticmethod
    def ask_argument(argument):
        """Return an input from the user for a specific argument"""
        text_to_send = {"name": "Quel est le prénom du nouveau membre?",
                        "tournament_name": "Quel est le nom du tournoi?",
                        "place": "Où se déroule le tournoi?",
                        "tournament_date": "A quelle(s) date(s) se déroule le tournoi? (format jj/mm/aaaa, a"
                                           "vec un espace entre chaque date s'il y en a plusieurs).",
                        "max_round": "Combien de rondes comportera le tournoi?",
                        "participant_amount": "Combien de joueurs participeront au tournoi?",
                        "tournament_type": "Quel contrôle de temps sera utilisé pour le tournoi?",
                        "surname": "Quel est le nom de famille du nouveau membre?",
                        "birthdate": "Quel est la date de naissance du nouveau membre?",
                        "gender": "Quel est le genre du nouveau membre?",
                        "ranking": "Quel est le classement du nouveau membre?",
                        "name_ranking": "Quel est le prénom du membre dont vous voulez changer le classement?",
                        "surname_ranking": "Quel est le nom de famille du membre dont vous voulez changer "
                                           "le classement?",
                        "new_ranking": "Quel est le nouveau classement du membre dont vous voulez changer "
                                       "le classement.",
                        "tournament_name_to_load": "Quel est le nom du tournoi que vous voulez charger?",
                        "participant_name": "Quel est le prénom du joueur que vous voulez ajouter au tournoi?",
                        "participant_surname": "Quel est le nom de famille du joueur que vous voulez "
                                               "ajouter au tournoi?",
                        "name_to_remove": "Quel est le prénom du joueur que vous voulez retirer du tournoi?",
                        "surname_to_remove": "Quel est le nom de famille du joueur que vous voulez retirer du tournoi?",
                        "name_info": "Quel est le prénom du joueur dont vous voulez les détails?",
                        "surname_info": "Quel est le nom de famille du joueur dont vous voulez les détails?",
                        "discriminator": "Quel est le discriminant du joueur dont vous voulez les détails?",
                        "match_number": "Quel est le numéro du match dont vous voulez donner le résultat?",
                        "result": "Quel est le résultat du match?",





         }
        answer = input(text_to_send[argument])
        return answer

    @staticmethod
    def ask_correct_argument(argument):
        """Return an input from the user for a specific argument to fix an invalid argument."""
        text_to_send = {"tournament_date": "La date du tournoi n'est pas valide, entrez une date correcte (au format "
                                           "jj/mm/aaaa avec des espaces entre chaque date s'il y en a plusieurs.",
                        "max_round": "Le nombre de rondes doit être un nombre. Entrez un entier positif.",
                        "participant_amount": "Le nombre de participants doit être un nombre. "
                                              "Entrez un entier positif.",
                        "birthdate": "La date de naissance n'est pas valide, entrez une date correcte "
                                     "(au format jj/mm/aaaa).",
                        "ranking": "Le classement d'un joueur doit être un nombre. Entrez un entier positif.",
                        "new_ranking": "Le nouveau classement du joueur doit être un nombre. Entrez un entier positif.",
                        "discriminator": "Le discriminant du joueur doit être un nombre positif. "
                                         "Entrez un entier positif.",
                        "result": "Le résultat du match n'est pas valide. Entrez un résultat valide "
                                  "(1-0, 0-1 ou 1/2-1/2).",
                        "match_number": "Le numéro du match doit être un nombre. Entrez un entier positif."}
        answer = input(text_to_send[argument])
        return answer

def parse(param_string):
    """Parse a string to get a command and arguments from it"""
    #Todo: Remplacer les fonctions qui utilisent des arguments par des arguments mot-clés
    #Todo : Remplacer les **kwargs en entrée des init de class par des mots-clés directement
    #Todo (plus tard): Ajouter commande pour traduire les commandes/arguments (ils sont donnés en X, ils doivent être traduits en anglais pour être utilisés par le code
    #Todo: Remplacer les "commandes_possibles" par la traduction et un getattr()
    #Todo: Prévenir quand un nombre de joueurs est impair
    command_regex = re.compile(r"^[^ ]+")
    args_regex = re.compile(r"--(?P<name>[^ ]+)\s(?P<value>[^--]+)")
    command_name = command_regex.search(param_string).group()
    kwargs = {match["name"]: match["value"].strip() for match in args_regex.finditer(param_string)}
    # value must be stripped of its space because the regex keeps the last space.
    # It's easier to strip the last space than rewrite the regex
    # TODO: add a translate function on "name"
    return command_name, kwargs


