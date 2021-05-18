"""Implement a class that will manage interactions with the user"""


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
        answer = parse(answer)
        return answer

    @staticmethod
    def ask_argument(argument):
        """Return an input from the user for a specific argument."""
        text_to_send = {"birthdate": "Quel est la date de naissance du nouveau membre?",
                        "discriminator": "Quel est le discriminant du joueur dont vous voulez les détails?",
                        "gender": "Quel est le genre du nouveau membre?",
                        "match_number": "Quel est le numéro du match dont vous voulez donner le résultat?",
                        "max_round": "Combien de rondes comportera le tournoi?",
                        "name": "Quel est le prénom du nouveau membre?",
                        "name_info": "Quel est le prénom du joueur dont vous voulez les détails?",
                        "name_ranking": "Quel est le prénom du membre dont vous voulez changer le classement?",
                        "name_to_remove": "Quel est le prénom du joueur que vous voulez retirer du tournoi?",
                        "new_ranking": "Quel est le nouveau classement du membre dont vous voulez changer "
                                       "le classement.",
                        "participant_amount": "Combien de joueurs participeront au tournoi?",
                        "participant_name": "Quel est le prénom du joueur que vous voulez ajouter au tournoi?",
                        "participant_surname": "Quel est le nom de famille du joueur que vous voulez ajouter "
                                               "au tournoi?",
                        "place": "Où se déroule le tournoi?",
                        "ranking": "Quel est le classement du nouveau membre?",
                        "result": "Quel est le résultat du match?",
                        "surname": "Quel est le nom de famille du nouveau membre?",
                        "surname_info": "Quel est le nom de famille du joueur dont vous voulez les détails?",
                        "surname_ranking": "Quel est le nom de famille du membre dont vous voulez changer "
                                           "le classement?",
                        "surname_to_remove": "Quel est le nom de famille du joueur que vous voulez retirer du tournoi?",
                        "tournament_date": "A quelle(s) date(s) se déroule le tournoi? (format jj/mm/aaaa, avec un "
                                           "espace entre chaque date s'il y en a plusieurs).",
                        "tournament_name": "Quel est le nom du tournoi?",
                        "tournament_name_to_load": "Quel est le nom du tournoi que vous voulez charger?",
                        "tournament_type": "Quel contrôle de temps sera utilisé pour le tournoi?"}
        answer = input(text_to_send[argument]).strip()
        return answer

    @staticmethod
    def ask_correct_argument(argument):
        """Return an input from the user for a specific argument that was invalid."""
        text_to_send = {"birthdate": "La date de naissance n'est pas valide, entrez une date correcte "
                                     "(au format jj/mm/aaaa).",
                        "discriminator": "Le discriminant du joueur doit être un nombre positif. "
                                         "Entrez un entier positif.",
                        "match_number": "Le numéro du match doit être un nombre. Entrez un entier positif.",
                        "max_round": "Le nombre de rondes doit être un nombre. Entrez un entier positif.",
                        "new_ranking": "Le nouveau classement du joueur doit être un nombre. Entrez un entier positif.",
                        "participant_amount": "Le nombre de participants doit être un nombre. "
                                              "Entrez un entier positif.",
                        "ranking": "Le classement d'un joueur doit être un nombre. Entrez un entier positif.",
                        "result": "Le résultat du match n'est pas valide. Entrez un résultat valide "
                                  "(1-0, 0-1 ou 1/2-1/2).",
                        "tournament_date": "La date du tournoi n'est pas valide, entrez une date correcte (au format "
                                           "jj/mm/aaaa avec des espaces entre chaque date s'il y en a plusieurs.",
                        "tournament_type": "Le contrôle de temps du tournoi ne fait pas partie des noms autorisés. "
                                           "Indiquez un nom valide."}
        answer = input(text_to_send[argument]).strip()
        return answer


def parse(param_string):
    """Parse a string to get a command and arguments from it."""
    # TODO (plus tard): Ajouter commande pour traduire les commandes/arguments (ils sont donnés en X,
    #  ils doivent être traduits en anglais pour être utilisés par le code
    param = param_string.split("--")
    command_name = param[0].strip().lower()
    param = [parameter.split() for parameter in param]
    kwargs = {param[i][0].lower(): " ".join(param[i][1:]) for i in range(1, len(param))}
    # TODO: add a translate function on "name"
    return command_name, kwargs
