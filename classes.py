"""Implement all classes required to create and play a complete tournament"""
from time import time
from datetime import date
from random import sample
from tinydb import TinyDB, Query

import pairing
from exceptions import *


class Tournament:
    """Class representing a complete Tournament."""
    all_tournaments = {}

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.place = kwargs.get("place", "")
        self.date = kwargs.get("date", date.fromtimestamp(time()))
        self.max_round = kwargs.get("max_round", 4)
        self.rounds = kwargs.get("rounds", [])
        self.participants = kwargs.get("participants", [])
        self.players = kwargs.get("players", [])
        self.is_started = kwargs.get("is_started", False)
        self.type = kwargs.get("type", "bullet")
        self.description = kwargs.get("description", "")
        self.participant_amount = kwargs.get("participant_amount", "")

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
            new_round = Round(**{"round_number": len(self.rounds) + 1,
                                 "players": self.players,
                                 "starting_time": starting_time})
            self.rounds.append(new_round)
            new_round.create_games()
        elif not self.rounds[-1].finished:
            raise PreviousRoundNotFinishedError
        elif len(self.rounds) > self.max_round:
            raise TooManyRoundsError

    @property
    def result(self):
        """Return a list of participants sorted by score, to be used to display the result of the tournament."""
        self.players.sort(key=lambda player: player.points, reverse=True)
        return self.players

    @property
    def serialized(self):
        serialized_participants = [participant.serialized for participant in self.participants]
        serialized_rounds = [game_round.serialized for game_round in self.rounds]
        serialized_players = [player.serialized for player in self.players]
        serialized_tournament = {name: value for name, value in self.__dict__.items()}
        serialized_tournament["participants"] = serialized_participants
        serialized_tournament["rounds"] = serialized_rounds
        serialized_tournament["players"] = serialized_players
        return serialized_tournament

    def save(self):
        db = TinyDB("db.json")
        tournament_tables = db.table("tournaments")
        tournament = Query()
        tournament_tables.upsert(self.serialized, (tournament.name == self.name and
                                                   tournament.place == self.place and
                                                   tournament.date == self.date))


class Round:
    """Class representing a round."""
    def __init__(self, **kwargs):
        self.players = kwargs["players"]
        self.number = kwargs["round_number"]
        self.starting_time = kwargs["starting_time"]

        self.name = kwargs.get("name", f"Round {self.number}")
        self.games = kwargs.get("games", [])
        self.ending_time = kwargs.get("ending_time", 0)
        self.finished = kwargs.get("finished", False)

    def create_games(self):
        """Create all games for the round."""
        self.players.sort(key=lambda player: player.ranking)  # Le 1° est le plus fort, donc
        # le tri ascendant marche bien.
        ecart = len(self.players) // 2
        if self.number == 1:
            for i in range(ecart):
                self.games.append(Game(**{"players":(self.players[i], self.players[i + ecart])}))
        else:
            self.players.sort(key=lambda joueur: joueur.points, reverse=True)  # Le joueur avec le plus de points doit
            # être le plus fort donc inversion.
            for pair in make_pairs_unique(create_pairs(self.players)):
                self.games.append(Game(**{"players":(pair[0], pair[1])}))

    def finish(self):
        """Check that all games are over and get the time the round ended at."""
        for game in self.games:
            if not game.winner:
                raise GameNotOverError(game)
        self.ending_time = time()
        self.finished = True

    @property
    def serialized(self):
        pass


class Game:
    """Class representing a game between two players."""
    def __init__(self, **kwargs):
        players = kwargs.get("players", None)
        if players:
            self.white_player = kwargs["white_player"]
            self.black_player = kwargs["black_player"]
        else:
            players_random = sample(players, k=2)
            self.white_player = players_random[0]
            self.black_player = players_random[1]
        self.name = f"{self.white_player.name} VS {self.black_player.name}"
        self.score = kwargs.get("score", "0-0")

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
        self.surname = kwargs.get("surname", "")
        self.name = kwargs.get("name", "")
        self.birthdate = kwargs.get("birthdate", 0)
        self.gender = kwargs.get("gender", "")
        self.ranking = kwargs.get("ranking", "")
        self.discriminator = kwargs.get("discriminator", "")

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


class Player:
    """Represent a player in a tournament."""
    def __init__(self, **kwargs):
        self.member = kwargs["member"]
        self.people_played_against = kwargs.get("people_played_against", dict())
        self.points = kwargs.get("people_played_against", 0)

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


def unserialize_member(serialized):
    return Member(**serialized)


def unserialize_player(serialized):
    return Player(**serialized)


def unserialize_game(serialized, players):
    self.white_player
    return Game(**serialized)


def unserialize_round(serialized, players):
    serialized["players"][i] = players
    for i in range(len(serialized["games"])):
        serialized["games"][i] = unserialize_game(serialized["games"][i], players)
    return Round(**serialized)


def unserialize_tournament(serialized):
    for i in range(len(serialized["participants"])):
        serialized["participants"][i] = unserialize_game(serialized["participants"][i])
    for i in range(len(serialized["players"])):
        serialized["players"][i] = unserialize_player(serialized["players"][i], serialized["participants"][i])
    for i in range(len(serialized["rounds"])):
        serialized["rounds"][i] = unserialize_player(serialized["rounds"][i],  serialized["players"])
    return Tournament(**serialized)


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
