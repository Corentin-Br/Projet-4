"""Implement a class that will manage all interactions with the model"""

import classes
from exceptions import *

validation_words = ["oui", "o"]
refusal_words = ["non", "n"]


class GlobalController:
    def __init__(self, view):
        self.view = view

    def create_tournament(self, **kwargs):
        """Create a new tournament and return the controller that manages it"""
        new_tournament = classes.Tournament(**kwargs)
        self.view.display("Tournoi créé!")
        return self.create_tournament_controller(new_tournament)

    def create_tournament_controller(self, tournament):
        """Create a new controller for a tournament"""
        new_controller = TournamentController(tournament, self.view)
        return new_controller

    def add_member(self, **kwargs):
        """Add a new member with all required fields and make sure they are unique"""
        kwargs = self.fix_member_creation(kwargs)
        new_member = classes.Member(**kwargs)
        self.add_discriminator(new_member)
        new_member.save()
        return

    def fix_member_creation(self, data_given):
        """""Ask for all missing arguments required to create a member"""
        arguments_required = {"surname": "Quel est le nom",
                              "name": "Quel est le prénom",
                              "birthdate": "Quelle est la date de naissance",
                              "gender": "Quel est le genre",
                              "ranking": "Quel est le classement"}
        for argument in arguments_required:
            if argument not in data_given:
                data_given[argument] = self.view.ask(f"{arguments_required[argument]} du nouvel utilisateur?")
        return data_given

    def add_discriminator(self, member):
        """Ensure the member has a number to make them different from other members with same informations."""
        if member.already_exist > 0:
            add = self.view.ask("Cette personne semble déjà exister dans la base de données. Êtes-vous sûr de vouloir "
                                "la rajouter malgré tout? (o/n)")
            if add.lower() in validation_words:
                member.discriminator = member.already_exist
                self.view.display(f"Cette personne a bien été ajoutée. Pour la distinguer des personnes similaires, un"
                                  f"discriminant ({member.discriminator}) a été ajouté. Assurez-vous de vous en"
                                  f"souvenir pour distinguer les personnes!")
            elif add.lower not in refusal_words:
                self.view.display("Votre réponse n'est pas valide. La personne n'a pas été ajoutée à la base de données"
                                  "")
                return
            else:
                self.view.display("La personne n'a pas été ajoutée à la base de données.")
        return

    def change_ranking(self, name, surname, new_ranking):
        """Change the ranking of a single player"""
        member = self.choose_a_member(classes.Member.get_member(name, surname))
        if not member:
            return
        member["ranking"] = new_ranking
        classes.Member(**member).save()

    def choose_a_member(self, possible_members):
        if len(possible_members) == 0:
            self.view.display("Il n'y a personne avec ce nom dans la base de données!")
            return
        else:
            key_presentation = "   ".join(key for key in possible_members[0].keys())
            values = ["   ".join([value for value in member.values()]) for member in possible_members]
            value_presentation = ""
            for i, value in enumerate(values):
                value_presentation += f"{i+1}) {value} \n"
            self.view.display(f"Il y a {len(possible_members)} personne(s) avec ce nom dans la base de données: \n"
                              f"{key_presentation} \n {value_presentation}")
            if len(possible_members) > 1:
                number = self.view.ask("Indiquez le numéro du joueur dont vous voulez modifier le classement")
                if not number.isnumeric():
                    self.view.display("Vous n'avez pas indiqué un nombre. L'opération est annulée.")
                    return
                elif int(number) not in range(len(possible_members)):
                    self.view.display("Vous avez indiqué un nombre non-valide. L'opération est annulée.")
                    return
                else:
                    number = int(number)-1
            else:
                number = 0
            return possible_members[number]

    def load_tournament(self, name):
        """Load an existing tournament"""
        tournament = self.choose_a_tournament(classes.Tournament.get_tournament(name))
        if not tournament:
            return
        tournament_instance = classes.Tournament(**tournament)
        return self.create_tournament_controller(tournament_instance)

    def choose_a_tournament(self, possible_tournaments):
        if len(possible_tournaments) == 0:
            self.view.display("Il n'y a pas de tournoi avec ce nom dans la base de données!")
            return
        else:
            key_presentation = "   ".join(["name", "place", "date"])
            values = ["   ".join([tournament["name"], tournament["place"], tournament["date"]])
                      for tournament in possible_tournaments]
            value_presentation = ""
            for i, value in enumerate(values):
                value_presentation += f"{i+1}) {value} \n"
            self.view.display(f"Il y a {len(possible_tournaments)} tournoi(s) avec ce nom dans la base de données: \n"
                              f"{key_presentation} \n {value_presentation}")
            if len(possible_tournaments) > 1:
                number = self.view.ask("Indiquez le numéro du tournoi dont vous voulez modifier le classement")
                if not number.isnumeric():
                    self.view.display("Vous n'avez pas indiqué un nombre. L'opération est annulée.")
                    return
                elif int(number) not in range(len(possible_tournaments)):
                    self.view.display("Vous avez indiqué un nombre non-valide. L'opération est annulée.")
                    return
                else:
                    number = int(number)-1
            else:
                number = 0
            return possible_tournaments[number]

    def display_members(self, sort_key=None):
        """Display all the members"""
        members = classes.Member.all_members
        if sort_key is not None:
            members = sorted(members, key=lambda x: getattr(x, "ranking" if sort_key == "classement" else "name"))
        string_return = ""
        for i in range(len(members)):
            member = members[i]
            string_return += "   ".join([f"{i})",
                                         member.surname,
                                         member.name,
                                         member.birthdate,
                                         member.gender,
                                         member.ranking])
            string_return += "\n"
        return string_return

    def display_tournaments(self):
        """Display all the tournaments"""
        tournaments = classes.Tournament.all_tournaments
        string_return = ""
        for i in range(len(tournaments)):
            tournament = tournaments[i]
            string_return += "   ".join([f"{i})",
                                         tournament.name,
                                         tournament.place,
                                         "et ".join(tournament.date),
                                         tournament.type,
                                         tournament.description])
        return string_return

    def display_help(self):
        pass
        # Send various possible commands

    def does(self, command, args, kwargs):
        pass
        # Find the method the user wants to use and run it.


class TournamentController:
    def __init__(self, tournament, view):
        self.tournament = tournament
        self.view = view

    def display_players(self, sort_key=None):
        """Display all the players in the tournament"""
        players = self.tournament.players
        if sort_key is not None:
            players = sorted(players, key=lambda x: getattr(x, "points" if sort_key == "classement" else "name"))
            # TODO : points donne ça à l'envers
        for i in range(len(players)):
            player = players[i]
            self.view.display("   ".join([f"{i})",
                                          player.surname,
                                          player.name,
                                          player.points]))

    def display_rounds(self):
        """Display all the rounds in the tournament"""
        rounds = self.tournament.rounds
        for i in range(len(rounds)):
            game_round = rounds[i]
            self.view.display("   ".join([game_round.name,
                                          f"a commencé à {game_round.starting_time}",
                                          f"a fini à {game_round.starting_time}",
                                          "\n".join(game.name for game in game_round.games)]))

    def display_games(self):
        """Display all the games in the tournament"""
        games = [game for tournament_round in self.tournament.rounds for game in tournament_round.games]
        for i in range(len(games)):
            game = games[i]
            self.view.display("   ".join([game.name,
                                          game.score]))

    def add_participant(self, full_name):
        try:
            self.tournament.add_participant(classes.Member.all_members[full_name])
        except TournamentStartedError:
            self.view.display("Le tournoi a déjà commencé!")
        except TooManyParticipantsError:
            self.view.display("Il y a déjà assez de participants!")
        except AlreadyInTournamentError as inst:
            self.view.display(f"{inst.problem_member.name} {inst.problem_member.surname} est déjà dans le tournoi.")
        else:
            self.view.display(f"{full_name} a bien été ajouté au tournoi en cours.")

    def remove_participant(self, full_name):
        try:
            self.tournament.remove_participant(classes.Member.all_members[full_name])
        except NotInTournamentError as inst:
            self.view.display(f"{inst.problem_member.name} {inst.problem_member.surname} n'est pas dans le tournoi.")
        else:
            self.view.display(f"{full_name} a bien été enlevé du tournoi en cours")

    def start(self):
        try:
            self.tournament.start()
        except NotEnoughPlayersError:
            self.view.display("Il n'y a pas assez de joueurs.")
        except AlreadyStartedError:
            self.view.display("Le tournoi est déjà lancé!")
        else:
            self.view.display("Le tournoi est lancé")

    def next_round(self):
        try:
            self.tournament.create_round()
        except PreviousRoundNotFinishedError:
            self.view.display("La ronde précédente n'a pas été terminée.")
        except TooManyRoundsError:
            self.view.display("Toutes les rondes prévues ont déjà été jouées!")
        else:
            self.view.display("La prochaine ronde a été créée!")
            game_round = self.tournament.rounds[-1]
            for game in game_round.games:
                self.view.display(game.name)

    def finish_round(self):
        try:
            self.tournament.rounds[-1].finish()
        except GameNotOverError as inst:
            self.view.display(f"Le match {inst.game_not_finished.name} n'est pas fini.")
        else:
            self.view.display("La ronde actuelle a bien été finie.")

    def give_results(self, match_number, result):
        if not is_valid_result(result):
            self.view.display("Le résultat n'est pas valide.")
        else:
            if match_number >= len(self.tournament.rounds[-1].matchs):
                self.view.display("Ce match n'existe pas.")
            else:
                current_match = self.tournament.rounds[-1].matchs[match_number]
                if current_match.score != "0-0":
                    self.view.display("Le résultat du match a déjà été entré.")
                else:
                    answer = self.view.ask(f"Le résultat de {current_match.name} va être {result}. Il ne pourra plus"
                                           f"être changé après. Êtes-vous sûr de vouloir valider? (o/n)")
                    if answer.lower() in validation_words:
                        current_match.score = result
                        self.view.display("Le résultat a été validé!")
                    elif answer.lower() not in refusal_words:
                        self.view.display("Votre réponse n'était pas valide. Le résultat n'a pas été validé.")
                    else:
                        self.view.display("Le résultat n'a pas été validé.")

    def finish(self):
        if len(self.tournament.rounds) == self.tournament.max_round and self.tournament.rounds[-1].finished:
            result = self.tournament.result
            for player in result:
                self.view.display("   ".join([player.name,
                                              player.surname,
                                              player.points]))
            self.exit()
        else:
            self.view.display("Le tournoi n'est pas fini! Il reste une ou plusieurs rondes à jouer ou à terminer.")

    def exit(self):
        pass
        # How to make it go back to the global controller in the main loop?

    def does(self, command, args, kwargs):
        pass
        # Find the method the user wants to run.


def is_valid_result(result):
    valid_results = {"0-1", "1-0", "1/2-1/2"}
    return result in valid_results


# Que doit faire mon contrôleur?
# ->Afficher message de bienvenue avec commandes de base (help, créer tournoi, ajouter un membre, charger un tournoi,
# changer classement d'un joueur, afficher tous les membres, afficher tous les joueurs d'un tournois,
# afficher tous les tournois, afficher toutes les rondes d'un tournoi, afficher tous les matchs d'un tournois.)
#
# -> Si on crée un tournoi ou qu'on en charge un:
#     -> générer ronde suivante
#     -> Choisir un match et entrer résultat
