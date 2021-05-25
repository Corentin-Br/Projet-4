"""Implement a class that will manage all interactions with the model"""
import re
from datetime import datetime

from models import core, exceptions
from models.translate import TRANSLATION

VALIDATION_WORDS = TRANSLATION["yes"]
REFUSAL_WORDS = TRANSLATION["no"]
SENTENCES = TRANSLATION["controller"]
HEADERS = TRANSLATION["headers"]
VALID_TIME_CONTROLS = TRANSLATION["valid_types"]


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
                controller.view.display(SENTENCES['unknown_argument'](wrong_arg))
                return fixer(controller, **kwargs)
            elif not_enough_argument(inst):
                for argument in not_enough_argument(inst):
                    kwargs[argument] = controller.view.ask_argument(f"{argument}_{function.__name__}")
                kwargs = checker(controller, **kwargs)
                return fixer(controller, **kwargs)
        except ValueError:
            kwargs = checker(controller, **kwargs)
            return fixer(controller, **kwargs)
        else:
            return result

    def checker(controller, **kwargs):
        """Ensure that arguments have a valid value if they expect a certain format."""
        to_check = {"birthdate": check_date,
                    "discriminator": check_number,
                    "match_number": check_number,
                    "max_round": check_number,
                    "ranking": check_number,
                    "participant_amount": check_number,
                    "result": check_result,
                    "date": check_date,
                    "tournament_type": check_type
                    }
        for key in kwargs:
            if key in to_check:
                while not to_check[key](kwargs[key]):
                    kwargs[key] = controller.view.ask_correct_argument(key)
        return kwargs

    return fixer


class Controller:
    """An abstract class that represents a controller."""

    def __init__(self, view):
        self.view = view

    def choose_a_member(self, possible_members):
        """Return a member instance picked by the user."""
        if len(possible_members) == 0:
            self.view.display(SENTENCES["no_member_in_DB"])
            return
        else:
            if len(possible_members) > 1:
                members = "\n".join([f"{i + 1}) {member.to_display}" for i, member in enumerate(possible_members)])
                self.view.display(SENTENCES['existing_members'](len(possible_members)) + "\n" +
                                  HEADERS['member_choice'] + "\n" + f"{members}")
                number = self.view.ask(SENTENCES["player_number"])
                if not number.isnumeric():
                    self.view.display(SENTENCES["not_a_number"])
                    return
                elif int(number) not in range(len(possible_members)+1):
                    self.view.display(SENTENCES["not_a_valid_number"])
                    return
                else:
                    number = int(number) - 1
            else:
                number = 0
            return possible_members[number]

    @fix_input
    def display_members(self, key=None):
        """Display all the members."""
        all_members = self.sort_check(core.Member.get_all_members(), key)
        members = "\n".join([f"{i+1}) {member.to_display}" for i, member in enumerate(all_members)])
        if members:
            self.view.display(f"{HEADERS['member_choice']}\n{members}")
        else:
            self.view.display(SENTENCES["no_member"])
        return

    def sort_check(self, elements, key):
        """Sort according to key if key is an attribute of all elements of a list."""
        if key is not None:
            try:
                key = TRANSLATION["argument_names"][key]
                elements.sort(key=lambda x: getattr(x, key), reverse=(key == "points"))
            except (AttributeError, KeyError):  # AttributeError deals with problem with the sort,
                # KeyError with the translatiob
                self.view.display(SENTENCES["can't_sort"](key))
                return elements

        return elements


class GlobalController(Controller):
    """A class managing the interactions with the main menu."""

    def __init__(self, view):
        super().__init__(view)

    @fix_input
    def add_tournament(self, *, name, place, date, max_round, participant_amount,
                       tournament_type, description=""):
        """Create a new tournament and return the controller that manages it."""
        try:
            new_tournament = core.Tournament(name=name, place=place, date=date,
                                             max_round=max_round, participant_amount=participant_amount,
                                             tournament_type=tournament_type, description=description)
        except exceptions.OddParticipantError:
            self.view.display(SENTENCES["odd_number"])
            return
        else:
            if new_tournament.already_exist:
                self.view.display(SENTENCES["tournament_already_exists"])
                return
            self.view.display(SENTENCES["created_tournament"])
            new_tournament.save()
            return self.create_tournament_controller(new_tournament)

    @fix_input
    def add_member(self, *, name, surname, birthdate, gender, ranking):
        """Add a new member with all required fields and make sure they are unique."""
        new_member = core.Member(name=name, surname=surname, birthdate=birthdate, gender=gender, ranking=ranking)
        try:
            self.add_discriminator(new_member)
        except exceptions.NotCreatedError:
            return
        new_member.save()
        if new_member.discriminator == 0:  # This prevents displaying twice the confirmation message
            self.view.display(SENTENCES["member_added"])
        return

    @fix_input
    def change_ranking(self, *, name, surname, ranking):
        """Change the ranking of a single player."""
        member = self.choose_a_member(core.Member.get_member(name, surname))
        if not member:
            return
        member.ranking = ranking
        member.save()
        self.view.display(SENTENCES["ranking_changed"])
        return

    @fix_input
    def load_tournament(self, *, name):
        """Load an existing tournament."""
        try:
            tournament = self.choose_a_tournament(core.Tournament.get_tournament(name))
        except exceptions.InvalidTournamentError:
            self.view.display(SENTENCES["can't_charge_tournament"])
            return
        if not tournament:
            return
        self.view.display(SENTENCES["tournament_loaded"])
        return self.create_tournament_controller(tournament)

    @fix_input
    def display_tournaments(self):
        """Display all the tournaments."""
        try:
            tournaments = core.Tournament.get_all_tournaments()
        except exceptions.InvalidTournamentError as inst:
            self.view.display(SENTENCES["can't_charge_tournament_critical"](inst.problem))
            return
        tournaments_to_display = "\n".join([f"{i+1}) {tournament.to_display}"
                                            for i, tournament in enumerate(tournaments)])
        if tournaments_to_display:
            self.view.display(HEADERS["tournament_display"])
            self.view.display(tournaments_to_display)
        else:
            self.view.display(SENTENCES["no_tournament"])
        return

    def create_tournament_controller(self, tournament):
        """Create a new controller for a tournament."""
        new_controller = TournamentController(tournament, self.view)
        return new_controller

    def add_discriminator(self, member):
        """Ensure the member has a number to make them different from other members with same informations."""
        if member.already_exist > 0:
            add = self.view.ask(SENTENCES["member_already_exist"])
            if add.lower() in VALIDATION_WORDS:
                member.discriminator = member.already_exist
                self.view.display(SENTENCES["added_but_exist"](member.discriminator))
            elif add.lower() not in REFUSAL_WORDS:
                self.view.display(SENTENCES["invalid_member_answer"])
                raise exceptions.NotCreatedError
            else:
                self.view.display(SENTENCES["not_added"])
                raise exceptions.NotCreatedError
        else:
            member.discriminator = 0
        return

    def choose_a_tournament(self, possible_tournaments):
        """Return a tournament instance picked by the user."""
        if len(possible_tournaments) == 0:
            self.view.display(SENTENCES["no_tournament_in_DB"])
            return
        else:
            if len(possible_tournaments) > 1:
                values = "\n".join(
                    [f"{i + 1}) {tournament.to_display}" for i, tournament in enumerate(possible_tournaments)])
                self.view.display(SENTENCES["existing_tournaments"](len(possible_tournaments)))
                self.view.display(HEADERS["tournament_display"])
                self.view.display(values)
                number = self.view.ask(SENTENCES["tournament_number"])
                if not number.isnumeric():
                    self.view.display(SENTENCES["not_a_number"])
                    return
                elif int(number) not in range(len(possible_tournaments)+1):
                    self.view.display(SENTENCES["not_a_valid_number"])
                    return
                else:
                    number = int(number) - 1
            else:
                number = 0
            return possible_tournaments[number]

    @fix_input
    def close(self):
        """Exit the program entirely"""
        self.view.display(SENTENCES["ending"])
        return "close"


class TournamentController(Controller):
    """A class managing the interactions with a tournament."""

    def __init__(self, tournament, view):
        super().__init__(view)
        self.tournament = tournament

    @fix_input
    def display_players(self, key=None):
        """Display all the players in the tournament."""
        players = sorted(self.tournament.players, key=lambda x: x.member.ranking)
        players = self.sort_check(players, key)
        if not players:
            self.view.display(SENTENCES["players_not_created"])
            return
        else:
            self.view.display(HEADERS["player_display"])
        for i, player in enumerate(players):
            self.view.display(f"{i+1}) {player.to_display}")
        return

    @fix_input
    def display_participants(self, key=None):
        """Display all the participants in the tournament."""
        participants = self.sort_check(self.tournament.participants, key)
        if not participants:
            self.view.display(SENTENCES["no_participants"])
        else:
            participants = "\n".join([f"{i + 1}) {participant.to_display}"
                                      for i, participant in enumerate(participants)])
            self.view.display(f"{HEADERS['member_choice']}\n{participants}")

    @fix_input
    def display_rounds(self):
        """Display all the rounds in the tournament."""
        rounds = self.tournament.rounds
        if not rounds:
            self.view.display(SENTENCES["no_rounds"])
        else:
            self.view.display(HEADERS["round_display"])
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
            self.view.display(SENTENCES["no_games"])
            return
        else:
            self.view.display(HEADERS["games_display"])
            for i in range(round_amount):
                tournament_round = self.tournament.rounds[-(i+1)]
                for j, game in enumerate(tournament_round.games):
                    self.view.display(f"{j+1}) {game.to_display}")
                self.view.display("")

    @fix_input
    def add_participant(self, *, name, surname):
        """Add a participant to the tournament."""
        new_participant = self.choose_a_member(core.Member.get_member(name, surname))
        if new_participant:
            try:
                self.tournament.add_participant(new_participant)
            except exceptions.TournamentStartedError:
                self.view.display(SENTENCES["tournament_started"])
                return
            except exceptions.TooManyParticipantsError:
                self.view.display(SENTENCES["enough_participants"])
                return
            except exceptions.AlreadyInTournamentError as inst:
                self.view.display(SENTENCES["already_in_tournament"](inst.problem_member.name,
                                                                     inst.problem_member.surname))
                return
            else:
                self.view.display(SENTENCES["has_been_added"](name.capitalize(),
                                                              surname.upper()))
        self.tournament.save()
        return

    @fix_input
    def remove_participant(self, *, name, surname):
        """Remove a participant from the tournament."""
        participant_to_remove = self.choose_a_member(core.Member.get_member(name, surname))
        if participant_to_remove:
            try:
                self.tournament.remove_participant(participant_to_remove)
            except exceptions.TournamentStartedError:
                self.view.display(SENTENCES["tournament_started"])
            except exceptions.NotInTournamentError as inst:
                self.view.display(SENTENCES["not_in_tournament"](inst.problem_member.name,
                                                                 inst.problem_member.surname,
                                                                 inst.problem_member.discriminator))
            else:
                self.view.display(SENTENCES["has_been_removed"](name.capitalize(), surname.upper()))
        self.tournament.save()
        return

    @fix_input
    def get_info_player(self, *, name, surname, discriminator):
        """Get all the information of a player for disambiguation when players share the same name."""
        member = core.Member.get_member(name, surname, discriminator=int(discriminator))
        if member:
            member = member[0]
        else:
            self.view.display(SENTENCES["doesn't_exist"])
            return
        self.view.display(SENTENCES["informations"])
        self.view.display(HEADERS["member_choice"])
        self.view.display(member.to_display)
        return

    @fix_input
    def start(self):
        """Start the tournament."""
        try:
            self.tournament.start()
        except exceptions.NotEnoughPlayersError:
            self.view.display(SENTENCES["not_enough_players"])
        except exceptions.AlreadyStartedError:
            self.view.display(SENTENCES["tournament_started"])
        else:
            self.view.display(SENTENCES["tournament_launched"])
            self.tournament.save()
        return

    @fix_input
    def next_round(self):
        """Create the next round."""
        try:
            self.tournament.create_round()
        except exceptions.PreviousRoundNotFinishedError:
            self.view.display(SENTENCES["round_not_finished"])
        except exceptions.TooManyRoundsError:
            self.view.display(SENTENCES["all_rounds_played"])
        except exceptions.TournamentNotStartedError:
            self.view.display(SENTENCES["tournament_not_started"])
        else:
            self.view.display(SENTENCES["round_created"])
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
        except exceptions.GameNotOverError as inst:
            self.view.display(SENTENCES["game_not_finished"](inst.game_not_finished.name))
        except exceptions.AlreadyFinishedError:
            self.view.display(SENTENCES["round_already_finished"])
        else:
            self.view.display(SENTENCES["round_finished"])
            self.tournament.save()
        return

    @fix_input
    def give_results(self, *, match_number, result):
        """Set the result for a match of the current round."""
        if not check_result(result):
            raise ValueError
        match_number = int(match_number)
        try:
            current_match = self.tournament.rounds[-1].games[match_number-1]
        except IndexError:
            self.view.display(SENTENCES["game_doesn't_exist"])
            return
        else:
            if current_match.score != "0-0":
                self.view.display(SENTENCES["game_already_has_score"])
            else:
                answer = self.view.ask(SENTENCES["validation_result"](current_match.name, result))
                if answer.lower() in VALIDATION_WORDS:
                    current_match.set_score(result)
                    self.view.display(SENTENCES["result_ok"])
                    self.tournament.save()
                elif answer.lower() not in REFUSAL_WORDS:
                    self.view.display(SENTENCES["invalid_result_answer"])
                else:
                    self.view.display(SENTENCES["result_not_ok"])

        return

    @fix_input
    def finish(self):
        """Finish the tournament and display the result."""
        if len(self.tournament.rounds) == self.tournament.max_round and self.tournament.rounds[-1].finished:
            result = self.tournament.result
            self.view.display(HEADERS["result"])
            for i, player in enumerate(result):
                self.view.display(f"{i+1}) {player.to_display}")
            self.tournament.save()
            return self.exit()
        else:
            self.view.display(SENTENCES["tournament_not_finished"])
            return

    @fix_input
    def exit(self):
        """Return to the main menu."""
        self.view.display(SENTENCES["back_main_menu"])
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


def check_result(result):
    """Return a boolean indicating if the input is a valid result or not."""
    valid_results = {"0-1", "1-0", "1/2-1/2"}
    return result in valid_results


def check_date(value):
    """Return a boolean indicating if the input can be turned into one or several dates or not."""
    potential_dates = value.split()
    for date in potential_dates:
        try:
            datetime.strptime(date, "%d/%m/%Y")
        except ValueError:
            return False
    return True


def check_number(value):
    """Return a boolean indicating if the input can be turned into an integer or not."""
    try:
        int(value)
    except ValueError:
        return False
    else:
        return int(value) > 0


def check_type(value):
    """Return a boolean indicating if the input is a valid type of time control."""
    return value.lower() in VALID_TIME_CONTROLS
