"""Implement a class that will manage all interactions with the model"""

import classes
from exceptions import *


class GlobalController:
    def __init__(self, view_used):
        self.view = view_used
        self.data = {"members": [],
                     "tournaments": []}

    def get_members(self):
        if not classes.Member.all_members:
            classes.Member.initialize_members()
        self.data["members"] = classes.Member.all_members
        self.view.display("Tous les membres ont été chargés!")

    def get_tournaments(self):
        """Load all tournaments"""
        if not classes.Tournament.all_tournaments:
            classes.Tournament.initialize_tournaments()
        self.data["tournaments"] = classes.Tournament.all_tournaments
        self.view.display("Tous les tournois ont été chargés!")

    def create_tournament(self, name, **kwargs):
        """Create a new tournament and return the controller that manages it"""
        new_tournament = classes.Tournament(name, **kwargs)
        self.view.display("Tournoi créé!")
        return self.create_tournament_controller(new_tournament)

    def create_tournament_controller(self, tournament):
        """Create a new controller for a tournament"""
        new_controller = TournamentController(self.view, tournament)
        return new_controller

    def add_member(self, **kwargs):
        """Add a new member"""
        new_member = classes.Member(**kwargs)
        classes.Member.add_member(new_member)
        self.view.display("Ajout réussi!")  # In reality there is a need for a try/except above to deal with the
        # posibility of not being able to add the member. There's also a need to check with the user that the member
        # we're going to add is the correct one.

    def change_ranking(self, name, surname, new_ranking):
        """Change the ranking of a single player"""
        pass
        # TODO : What's under should be in models
        # if name, surname not in DB:
        # view must send that there are no such person
        # if name, surname present several times
        # view must display the name surname gender birthdate and discriminator of all players that fit.
        # The user must choose a number
        # If the member is unique or once it has been chosen, the ranking of the player is replaced by the new_ranking

    def load_tournament(self, name):
        """Load an existing tournament"""
        pass
        # TODO: What's under should be in models
        # if name not in DB:
        # view must send that there are no such tournament
        # if name present several times
        # view must display the name place and date of all the tournaments that fit.
        # the user must choose a number
        # If the tournament is unique or once it has been chosen
        # Create an instance of Tournament with its data.
        # create_tournament_controller(self, tournament)

    def display_members(self, sort_key=None):
        """Display all the members"""
        sorts = {None: None,
                 "classement": lambda x: x.ranking,
                 "alphabet": lambda x: x.name}
        members = classes.Member.all_members.copy()
        members.sort(key=sorts[sort_key])
        for i in range(len(members)):
            member = members[i]
            self.view.display("   ".join([f"{i})",
                                          member.surname,
                                          member.name,
                                          member.birthdate,
                                          member.gender,
                                          member.ranking]))
            # self.view.display("\n")
            # The comment above shouldn't be needed, since it's several print there should naturally be a line skipped

    def display_tournaments(self):
        """Display all the tournaments"""
        tournaments = classes.Tournament.all_tournaments.copy()
        for i in range(len(tournaments)):
            tournament = tournaments[i]
            self.view.display("   ".join([f"{i})",
                                          tournament.name,
                                          tournament.place,
                                          "et ".join(tournament.date),
                                          tournament.type,
                                          tournament.description]))

    def display_help(self):
        pass
        # Send various possible commands


class TournamentController:
    def __init__(self, view_used, tournament):
        self.view = view_used
        self.tournament = tournament

    def display_players(self, sort_key=None):
        """Display all the players in the tournament"""
        sorts = {None: None,
                 "classement": lambda x: -x.points,  # The ranking used here must be that of the tournament.
                 # I use -x.points to have the best at the beginning.
                 "alphabet": lambda x: x.name}
        players = self.tournament.players
        players.sort(key=sorts[sort_key])
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
                    if answer == "o":
                        current_match.score = result
                        self.view.display("Le résultat a été validé!")
                    elif answer != "n":
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