"""Implement all classes required to create and play a complete tournament"""
from time import time
from datetime import date
from random import sample

import pairing
from exceptions import *


class Tournament:
    """Class representing a complete Tournament."""
    all_tournaments = {}

    def __init__(self, name, **kwargs):
        self.name = name
        self.place = ""
        self.date = [date.fromtimestamp(time())]
        self.max_round = 4
        self.rounds = []
        self.participants = []
        self.players = []
        self.is_started = False
        self.type = "bullet"
        self.description = ""
        self.participant_amount = 8
        for name, value in kwargs.items():
            setattr(self, name, value)

    def add_participant(self, member):
        """Add a participant for the tournament."""
        if self.is_started:
            raise TournamentStartedError
        else:
            if len(self.participants) < self.participant_amount:
                if member not in self.participants:
                    self.participants.append(member)
                else:
                    raise AlreadyInTournamentError(member)
            else:
                raise TooManyParticipantsError

    def remove_participant(self, member):
        """Remove a participant from the tournament."""
        if member in self.participants:
            self.participants.remove(member)
        else:
            raise NotInTournamentError(member)

    def start(self):
        """Generate the players and prevent adding more participants."""
        if len(self.participants) < self.participant_amount:
            raise NotEnoughPlayersError
        elif self.is_started :
            raise AlreadyStartedError
        else:
            self.players = [Player(member) for member in self.participants]
            self.is_started = True

    def create_round(self):
        """Create a round."""
        if len(self.rounds) == 0 or (len(self.rounds) <= self.max_round and self.rounds[-1].finished):
            starting_time = time()
            self.rounds.append(Round(len(self.rounds) + 1, self.players, starting_time))
        elif not self.rounds[-1].finished:
            raise PreviousRoundNotFinishedError
        elif len(self.rounds) > self.max_round:
            raise TooManyRoundsError

    @property
    def result(self):
        """Return a list of participants sorted by score, to be used to display the result of the tournament."""
        self.players.sort(key=lambda player: player.points, reverse=True)
        return self.players

    @classmethod
    def initialize_tournaments(cls):
        pass
        # DB request
        # cls.all_tournaments = request_result

    @classmethod
    def add_tournament(cls, tournament):
        if not cls.all_tournaments():
            cls.initialize_tournaments()
        cls.all_tournaments[f"{tournament.name} {tournament.place}"] = tournament
        pass


class Round:
    """Class representing a round."""
    def __init__(self, round_number, players, starting_time):
        self.players = players
        self.number = round_number
        self.name = f"Round {self.number}"
        self.games = []
        self.starting_time = starting_time
        self.ending_time = 0
        self.finished = False
        self.create_games()

    def create_games(self):
        """Create all games for the round."""
        self.players.sort(key=lambda player: player.ranking)  # Le 1° est le plus fort, donc
        # le tri ascendant marche bien.
        ecart = len(self.players) // 2
        if self.number == 1:
            for i in range(ecart):
                self.games.append(Game((self.players[i], self.players[i + ecart])))
        else:
            self.players.sort(key=lambda joueur: joueur.points, reverse=True)  # Le joueur avec le plus de points doit
            # être le plus fort donc inversion.
            for pair in make_pairs_unique(create_pairs(self.players)):
                self.games.append(Game((pair[0], pair[1])))

    def finish(self):
        """Check that all games are over and get the time the round ended at."""
        for game in self.games:
            if not game.winner:
                raise GameNotOverError(game)
        self.ending_time = time()
        self.finished = True


class Game:
    """Class representing a game between two players."""
    def __init__(self, players):
        players_random = sample(players, k=2)
        self.white_player = players_random[0]
        self.black_player = players_random[1]
        self.name = f"{self.white_player.name} VS {self.black_player.name}"
        self.score = "0-0"

    def set_score(self, score):
        """Create the result of the game."""
        self.score = score
        self.give_points()
        self.white_player.played_against(self.black_player)
        self.black_player.played_against(self.white_player)

    def give_points(self):
        """Give the points to the players."""
        score = self.score.split("-")
        self.white_player.points += float(score[0])
        self.black_player.points += float(score[1])


class Member:
    """Represent a member of the chess club."""
    all_members = {}

    def __init__(self, **kwargs):
        self.surname = ""
        self.name = ""
        self.birthdate = 0
        self.gender = ""
        self.ranking = 0
        self.discriminator = 0
        for name, value in kwargs.items():
            setattr(self, name, value)

    @classmethod
    def initialize_members(cls):
        pass
        # TODO: DB request
        # cls.all_members = request_result

    @classmethod
    def add_member(cls, member):
        if not cls.all_members:
            cls.initialize_members()
        # TODO: Find if a member shares the same name, surname, birthdate and gender
        # if False, add the member to all_members
        # if True, warn the user that the member may already exist and ask confirmation that it's a different person
        # if it is indeed someone else, the discriminator attribute should be equal to the number of other people
        # with the same name/surname/birthdate/gender already in the DB.

    @classmethod
    def save(cls):
        pass
        # save in the DB


class Player(Member):
    """Represent a player in a tournament."""
    def __init__(self, member):
        super().__init__(**member.__dict__)
        self.people_played_against = dict()  # It will store the name of the player and the number of time he was faced
        self.points = 0

    def least_played_from(self, players):
        """Return the player who has been faced the least in a list."""
        comparison_list = [(player, self.people_played_against.get(player, 0)) for player in players]
        comparison_list.sort(key=lambda element: element[0].points, reverse=True)
        comparison_list.sort(key=lambda element: element[1])
        return comparison_list[0][0]

    def played_against(self, player):
        """Change the amount of time a player has been faced by another."""
        if player in self.people_played_against:
            self.people_played_against[player] += 1
        else:
            self.people_played_against[player] = 1

    def has_played_against(self, player):
        """Return a boolean determining if two players have faced each other."""
        return player in self.people_played_against


def create_pairs(player_list):
    """Return a dictionary pairing players for a round."""
    pairs = pairing.first_pairing(player_list)
    if len(pairs) == len(player_list):
        return pairs
    else:
        return pairing.pairing_fixing(player_list, pairs, (len(player_list) - len(pairs)) // 2)


def make_pairs_unique(pairs):
    """Turn a dictionary pairing players into a list that can be used to generate rounds"""
    unique_pairs = []
    for key, value in pairs.items():
        j = {key, value}
        if j not in unique_pairs:
            unique_pairs.append(tuple(j))
    return unique_pairs
