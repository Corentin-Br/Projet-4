"""Implement a class that will manage all interactions with the model"""
import re

import classes
from exceptions import *

validation_words = ["oui", "o"]
refusal_words = ["non", "n"]


def fix_input(function):
    """Check inputs to make sure they allow the function to run."""
    def fixer(controller, **kwargs):
        """Remove unused arguments and ask required arguments if they are not already in the input."""
        try:
            result = function(controller, **kwargs)
        except TypeError as inst:
            wrong_arg = excess_argument(inst)
            if wrong_arg:
                del(kwargs[wrong_arg])
                controller.view.display(f"Un argument non reconnu était présent, il a été ignoré: "
                                        f"{wrong_arg}")
                return fixer(controller, **kwargs)
            elif not_enough_argument(inst):
                for argument in not_enough_argument(inst):
                    kwargs[argument] = controller.view.ask_argument(argument)
                kwargs, has_changed = checker(controller, **kwargs)
                return fixer(controller, **kwargs)
            else:
                raise TypeError(inst)
        except ValueError as inst:
            kwargs, has_changed = checker(controller, **kwargs)
            if not has_changed:
                raise ValueError(inst)
            return fixer(controller, **kwargs)
        else:
            return result

    def checker(controller, **kwargs):
        """Ensure that arguments have a valid value if they expect a certain format."""
        to_check = {"birthdate": classes.check_date,
                    "discriminator": classes.check_number,
                    "match_number": classes.check_number,
                    "max_round": classes.check_number,
                    "new_ranking": classes.check_number,
                    "participant_amount": classes.check_number,
                    "ranking": classes.check_number,
                    "result": classes.check_result,
                    "tournament_date": classes.check_date,
                    "tournament_type": classes.check_type
                    }
        has_changed = False
        for key in kwargs:
            if key in to_check:
                has_changed = True
                while not to_check[key](kwargs[key]):
                    kwargs[key] = controller.view.ask_correct_argument(key)
        return kwargs, has_changed

    return fixer


class Controller:
    """An abstract class that represents a controller."""
    POSSIBLE_COMMANDS = {}

    def __init__(self, view):
        self.view = view

    def choose_a_member(self, possible_members):
        """Return a member instance picked by the user."""
        if len(possible_members) == 0:
            self.view.display("Il n'y a personne avec ce nom dans la base de données!")
            return
        else:
            if len(possible_members) > 1:
                key_presentation = "nom de famille   prénom   date de naissance   genre   classement   discriminant"
                members = "\n".join([f"{i + 1}) {member.to_display}" for i, member in enumerate(possible_members)])
                self.view.display(f"Il y a {len(possible_members)} personne(s) avec ce nom dans la base de données: \n"
                                  f"{key_presentation}\n{members}")
                number = self.view.ask("Indiquez le numéro du joueur que vous voulez choisir")
                if not number.isnumeric():
                    self.view.display("Vous n'avez pas indiqué un nombre. L'opération est annulée.")
                    return
                elif int(number) not in range(len(possible_members)+1):
                    self.view.display("Vous avez indiqué un nombre non-valide. L'opération est annulée.")
                    return
                else:
                    number = int(number) - 1
            else:
                number = 0
            return possible_members[number]

    def execute_command(self, command, kwargs):
        """Execute a command."""
        if command.lower() in self.POSSIBLE_COMMANDS:  # TODO: Once the translation has been done, it needs to be
            # replaced by a "if hasattr()", POSSIBLE_COMMAND disappear and everything is translated before being given
            # to the program.
            # The possible commands will be in the translation and some errors raised in the view directly
            # (because it won't be able to translate).
            return getattr(self, self.POSSIBLE_COMMANDS[command.lower()])(**kwargs)
        else:
            self.view.display("La fonction n'est pas un appel valide.  Lisez le readme pour"
                              " obtenir plus d'informations.")
            return

    @fix_input
    def display_members(self, key=None):
        """Display all the members."""
        all_members = self.sort_check(classes.Member.get_all_members(), key)
        members = "\n".join([f"{i+1}) {member.to_display}" for i, member in enumerate(all_members)])
        if members:
            key_presentation = "nom de famille   prénom   date de naissance   genre   classement   discriminant"
            self.view.display(f"{key_presentation}\n{members}")
        else:
            self.view.display("Il n'y a pas de membres à afficher!")
        return

    def sort_check(self, elements, key):
        """Sort according to key if key is an attribute of all elements of a list."""
        if key is not None:
            try:
                # key = translate.to_english(key)
                elements.sort(key=lambda x: getattr(x, key), reverse=(key == "points"))
            except AttributeError:
                self.view.display(f"Il est impossible de trier selon {key}.")
                return elements
        return elements


class GlobalController(Controller):
    """A class managing the interactions with the main menu."""
    POSSIBLE_COMMANDS = {"créer_tournoi": "add_tournament",
                         "ajouter_acteur": "add_member",
                         "changer_classement": "change_ranking",
                         "charger_tournoi": "load_tournament",
                         "afficher_acteurs": "display_members",
                         "afficher_tournois": "display_tournaments",
                         "fermer": "close"}  

    def __init__(self, view):
        super().__init__(view)

    @fix_input
    def add_tournament(self, *, tournament_name, place, tournament_date, max_round, participant_amount, tournament_type,
                       description=""):
        """Create a new tournament and return the controller that manages it."""
        try:
            new_tournament = classes.Tournament(name=tournament_name, place=place, date=tournament_date,
                                                max_round=max_round, participant_amount=participant_amount,
                                                tournament_type=tournament_type, description=description)
        except OddParticipantError:
            self.view.display("Vous ne pouvez pas avoir un nombre impair de joueurs. Le tournoi n'a pas été créé.")
            return
        else:
            self.view.display("Tournoi créé!\nVous êtes désormais dans la gestion de ce nouveau tournoi.")
            new_tournament.save()
            return self.create_tournament_controller(new_tournament)

    @fix_input
    def add_member(self, *, name, surname, birthdate, gender, ranking):
        """Add a new member with all required fields and make sure they are unique."""
        new_member = classes.Member(name=name, surname=surname, birthdate=birthdate, gender=gender, ranking=ranking)
        try:
            self.add_discriminator(new_member)
        except NotCreatedError:
            return
        new_member.save()
        self.view.display("La personne a été correctement ajoutée à la base de données!")
        return

    @fix_input
    def change_ranking(self, *, name_ranking, surname_ranking, new_ranking):
        """Change the ranking of a single player."""
        member = self.choose_a_member(classes.Member.get_member(name_ranking, surname_ranking))
        if not member:
            return
        member.ranking = new_ranking
        member.save()
        self.view.display("Le classement du joueur a été correctement changé!")
        return

    @fix_input
    def load_tournament(self, *, tournament_name_to_load):
        """Load an existing tournament."""
        try:
            tournament = self.choose_a_tournament(classes.Tournament.get_tournament(tournament_name_to_load))
        except InvalidTournamentError:
            self.view.display("Un ou plusieurs membres ne peuvent pas être trouvés. Le tournoi n'a pas pu être chargé.")
            return
        if not tournament:
            return
        self.view.display("Tournoi chargé!\nVous êtes désormais dans la gestion de ce tournoi")
        return self.create_tournament_controller(tournament)

    @fix_input
    def display_tournaments(self):
        """Display all the tournaments."""
        try:
            tournaments = classes.Tournament.get_all_tournaments()
        except InvalidTournamentError as inst:
            self.view.display(f"Le tournoi {inst.problem} n'a pas pu être chargé. L'opération a donc été annulée. "
                              f"Il est nécessaire de supprimer ce tournoi ou de recréer entièrement la base de données")
            return
        tournaments_to_display = "\n".join([f"{i+1}) {tournament.to_display}"
                                            for i, tournament in enumerate(tournaments)])

        if tournaments_to_display:
            self.view.display("nom   lieu   date(s)   type de tournoi   description")
            self.view.display(tournaments_to_display)
        else:
            self.view.display("Il n'y a pas de tournois à afficher!")
        return

    def create_tournament_controller(self, tournament):
        """Create a new controller for a tournament."""
        new_controller = TournamentController(tournament, self.view)
        return new_controller

    def add_discriminator(self, member):
        """Ensure the member has a number to make them different from other members with same informations."""
        if member.already_exist > 0:
            add = self.view.ask("Cette personne semble déjà exister dans la base de données. Êtes-vous sûr de vouloir "
                                "la rajouter malgré tout? (o/n)")
            if add.lower() in validation_words:
                member.discriminator = member.already_exist
                self.view.display(f"Cette personne a bien été ajoutée. Pour la distinguer des personnes similaires, un"
                                  f" discriminant ({member.discriminator}) a été ajouté. Assurez-vous de vous en"
                                  f" souvenir pour distinguer les personnes!")
            elif add.lower() not in refusal_words:
                self.view.display("Votre réponse n'est pas valide. La personne n'a pas été ajoutée à la base de données"
                                  "")
                raise NotCreatedError
            else:
                self.view.display("La personne n'a pas été ajoutée à la base de données.")
                raise NotCreatedError
        else:
            member.discriminator = 0
        return

    def choose_a_tournament(self, possible_tournaments):
        """Return a tournament instance picked by the user."""
        if len(possible_tournaments) == 0:
            self.view.display("Il n'y a pas de tournoi avec ce nom dans la base de données!")
            return
        else:
            if len(possible_tournaments) > 1:
                values = "\n".join(
                    [f"{i + 1}) {tournament.to_display}" for i, tournament in enumerate(possible_tournaments)])
                self.view.display(f"Il y a {len(possible_tournaments)} tournoi(s) avec ce nom dans la base de données:")
                self.view.display("nom   lieu   date(s)   type de tournoi   description")
                self.view.display(values)
                number = self.view.ask("Indiquez le numéro du tournoi que vous voulez charger.")
                if not number.isnumeric():
                    self.view.display("Vous n'avez pas indiqué un nombre. L'opération est annulée.")
                    return
                elif int(number) not in range(len(possible_tournaments)+1):
                    self.view.display("Vous avez indiqué un nombre non-valide. L'opération est annulée.")
                    return
                else:
                    number = int(number) - 1
            else:
                number = 0
            return possible_tournaments[number]

    def close(self):
        """Exit the program entirely"""
        self.view.display("Le gestionnaire de tournois va s'éteindre!")
        return "close"


class TournamentController(Controller):
    """A class managing the interactions with a tournament."""
    POSSIBLE_COMMANDS = {"afficher_joueurs": "display_players",
                         "afficher_participants": "display_participants",
                         "afficher_tours": "display_rounds",
                         "afficher_tour_actuel": "display_current_games",
                         "afficher_matchs": "display_games",
                         "ajouter_participant": "add_participant",
                         "enlever_participant": "remove_participant",
                         "détails": "get_info_player",
                         "commencer": "start",
                         "tour_suivant": "next_round",
                         "finir_tour": "finish_round",
                         "résultat": "give_results",
                         "finir_tournoi": "finish",
                         "afficher_acteurs": "display_members",
                         "exit": "exit"}

    def __init__(self, tournament, view):
        super().__init__(view)
        self.tournament = tournament

    @fix_input
    def display_players(self, key=None):
        """Display all the players in the tournament."""
        players = sorted(self.tournament.players, key=lambda x: x.member.ranking)
        players = self.sort_check(players, key)
        if not players:
            self.view.display("Les joueurs n'ont pas encore été créés!")
            return
        else:
            self.view.display("nom complet   points")
        for i, player in enumerate(players):
            self.view.display(f"{i+1}) {player.to_display}")
        return

    @fix_input
    def display_participants(self, key=None):
        """Display all the participants in the tournament."""
        participants = self.sort_check(self.tournament.participants, key)
        if not participants:
            self.view.display("Il n'y a pas encore de participants!")
        else:
            participants = "\n".join([f"{i + 1}) {participant.to_display}"
                                      for i, participant in enumerate(participants)])
            key_presentation = "nom de famille   prénom   date de naissance   genre   classement   discriminant"
            self.view.display(f"{key_presentation}\n{participants}")

    @fix_input
    def display_rounds(self, key=None):
        """Display all the rounds in the tournament."""
        rounds = self.sort_check(self.tournament.rounds, key)
        if not rounds:
            self.view.display("Il n'y a pas encore de rondes créées dans ce tournoi!")
        else:
            self.view.display("nom   heure de début   heure de fin")
        for game_round in rounds:
            self.view.display(game_round.to_display)
        return

    @fix_input
    def display_games(self):
        """Display all the games in the tournament."""
        self.games_to_display(len(self.tournament.rounds))
        return

    @fix_input
    def display_current_games(self):
        """Display games of the current round."""
        self.games_to_display(1)
        return

    def games_to_display(self, round_amount):
        """Display the games of certain rounds"""
        if len(self.tournament.rounds) == 0:
            self.view.display("Il n'y a pas de parties dans ce tournoi!")
            return
        else:
            self.view.display("nom de la partie   score")
            for i in range(round_amount):
                tournament_round = self.tournament.rounds[-(i+1)]
                for j, game in enumerate(tournament_round.games):
                    self.view.display(f"{i+1}) {game.to_display}")
                self.view.display("")

    @fix_input
    def add_participant(self, *, participant_name, participant_surname):
        """Add a participant to the tournament."""
        new_participant = self.choose_a_member(classes.Member.get_member(participant_name, participant_surname))
        if new_participant:
            try:
                self.tournament.add_participant(new_participant)
            except TournamentStartedError:
                self.view.display("Le tournoi a déjà commencé!")
                return
            except TooManyParticipantsError:
                self.view.display("Il y a déjà assez de participants!")
                return
            except AlreadyInTournamentError as inst:
                self.view.display(f"{inst.problem_member.name} {inst.problem_member.surname} est déjà dans le tournoi.")
                return
            else:
                self.view.display(f"{new_participant.name} {new_participant.surname} "
                                  f"a bien été ajouté au tournoi en cours.")
        self.tournament.save()
        return

    @fix_input
    def remove_participant(self, *, name_to_remove, surname_to_remove):
        """Remove a participant from the tournament."""
        participant_to_remove = self.choose_a_member(classes.Member.get_member(name_to_remove, surname_to_remove))
        if participant_to_remove:
            try:
                self.tournament.remove_participant(participant_to_remove)
            except TournamentStartedError:
                self.view.display("Le tournoi a déjà commencé!")
            except NotInTournamentError as inst:
                self.view.display(f"{inst.problem_member.name} {inst.problem_member.surname} "
                                  f"{inst.problem_member.discriminator} n'est pas dans le tournoi.")
            else:
                self.view.display(f"{name_to_remove} {surname_to_remove} a bien été enlevé du tournoi en cours")
        self.tournament.save()
        return

    @fix_input
    def get_info_player(self, *, name_info, surname_info, discriminator):
        """Get all the information of a player for disambiguation when players share the same name."""
        member = classes.Member.get_member(name_info, surname_info, discriminator=int(discriminator))
        if member:
            member = member[0]
        else:
            self.view.display("Ce joueur n'existe pas!")
            return
        self.view.display("Voilà les informations du joueur")
        self.view.display("nom de famille   prénom   date de naissance   genre   classement   discriminant")
        self.view.display(member.to_display)
        return

    @fix_input
    def start(self):
        """Start the tournament."""
        try:
            self.tournament.start()
        except NotEnoughPlayersError:
            self.view.display("Il n'y a pas assez de joueurs.")
        except AlreadyStartedError:
            self.view.display("Le tournoi est déjà lancé!")
        else:
            self.view.display("Le tournoi est lancé.")
            self.tournament.save()
        return

    @fix_input
    def next_round(self):
        """Create the next round."""
        try:
            self.tournament.create_round()
        except PreviousRoundNotFinishedError:
            self.view.display("La ronde précédente n'a pas été terminée.")
        except TooManyRoundsError:
            self.view.display("Toutes les rondes prévues ont déjà été jouées!")
        except TournamentNotStartedError:
            self.view.display("Le tournoi n'est pas encore lancé!")
        else:
            self.view.display("La prochaine ronde a été créée!")
            game_round = self.tournament.rounds[-1]
            for game in game_round.games:
                self.view.display(game.name)
            self.tournament.save()
        return

    @fix_input
    def finish_round(self):
        """Finish the current round."""
        try:
            self.tournament.rounds[-1].finish()
        except GameNotOverError as inst:
            self.view.display(f"Le match {inst.game_not_finished.name} n'est pas fini.")
        except AlreadyFinishedError:
            self.view.display("La ronde est déjà finie.")
        else:
            self.view.display("La ronde actuelle a bien été finie.")
            self.tournament.save()
        return

    @fix_input
    def give_results(self, *, match_number, result):
        """Set the result for a match of the current round."""
        if not classes.check_result(result):
            raise ValueError
        match_number = int(match_number)
        try:
            current_match = self.tournament.rounds[-1].games[match_number-1]
        except IndexError:
            self.view.display("Ce match n'existe pas.")
            return
        else:
            if current_match.score != "0-0":
                self.view.display("Le résultat du match a déjà été entré.")
            else:
                answer = self.view.ask(f"Le résultat de {current_match.name} va être {result}. Il ne pourra plus"
                                       f" être changé après. Êtes-vous sûr de vouloir valider? (o/n)")
                if answer.lower() in validation_words:
                    current_match.set_score(result)
                    self.view.display("Le résultat a été validé!")
                    self.tournament.save()
                elif answer.lower() not in refusal_words:
                    self.view.display("Votre réponse n'était pas valide. Le résultat n'a pas été validé.")
                else:
                    self.view.display("Le résultat n'a pas été validé.")

        return

    @fix_input
    def finish(self):
        """Finish the tournament."""
        if len(self.tournament.rounds) == self.tournament.max_round and self.tournament.rounds[-1].finished:
            result = self.tournament.result
            self.view.display("place   Nom complet   points")
            for i, player in enumerate(result):
                self.view.display(f"{i+1}) {player.to_display}")
            self.tournament.save()
            self.exit()
        else:
            self.view.display("Le tournoi n'est pas fini! Il reste une ou plusieurs rondes à jouer ou à terminer.")
            return

    @fix_input
    def exit(self):
        """Return to the main menu."""
        self.view.display("Retour au menu principal!")
        self.tournament.save()
        return "exit"


def excess_argument(error):
    """Determine if there are unneeded arguments in a function from an error message, and return one of them, if so."""
    error_text = str(error)
    if "unexpected keyword argument" not in error_text:
        return False
    regex = re.compile(r"'(.+)'")
    return regex.search(error_text).group(1)


def not_enough_argument(error):
    """Determine all the arguments missing in a function from an error message."""
    error_text = str(error)
    regex = re.compile(r"'(.+?)'")
    arguments_missing = [match.group(1) for match in regex.finditer(error_text)]
    return arguments_missing
