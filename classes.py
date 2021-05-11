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
        elif self.is_started:
            raise AlreadyStartedError
        else:
            self.players = [Player(**{"member": member}) for member in self.participants]
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
        return sorted(self.players, key=lambda player: player.points, reverse=True)

    def to_dict(self):
        """Return a serialized instance of a tournament"""
        serialized_participants = [participant.to_dict() for participant in self.participants]
        serialized_rounds = [game_round.to_dict(self.players) for game_round in self.rounds]
        serialized_players = [player.to_dict(self.participants) for player in self.players]
        serialized_tournament = {name: value for name, value in self.__dict__.items()}
        serialized_tournament["participants"] = serialized_participants
        serialized_tournament["rounds"] = serialized_rounds
        serialized_tournament["players"] = serialized_players
        return serialized_tournament

    def save(self):
        """Add or update a tournament in the database"""
        db = TinyDB("db.json")
        tournament_tables = db.table("tournaments")
        tournament = Query()
        tournament_tables.upsert(self.to_dict(), (tournament.name == self.name &
                                                  tournament.place == self.place &
                                                  tournament.date == self.date))

    @classmethod
    def get_tournament(cls, name):
        tournament_tables = TinyDB("db.json").table("tournaments")
        tournament = Query()
        return tournament_tables.search(tournament.name == name)


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
        players = sorted(self.players, key=lambda player: player.ranking)
        ecart = len(players) // 2
        if self.number == 1:
            for i in range(ecart):
                self.games.append(Game(**{"players": (players[i], players[i + ecart])}))
        else:
            players = sorted(players, key=lambda joueur: joueur.points, reverse=True)
            for pair in make_pairs_unique(create_pairs(players)):
                self.games.append(Game(**{"players": (pair[0], pair[1])}))

    def finish(self):
        """Check that all games are over and get the time the round ended at."""
        for game in self.games:
            if not game.winner:
                raise GameNotOverError(game)
        self.ending_time = time()
        self.finished = True

    def to_dict(self, players):
        """Serialize an instance of a round"""
        serialized = {"number": self.number,
                      "starting_time": self.starting_time,
                      "name": self.name,
                      "ending_time": self.ending_time,
                      "finished": self.finished,
                      "games": [game.to_dict(players) for game in self.games]}
        return serialized


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

    def to_dict(self, players):
        """Serialize an instance of a game"""
        serialized = {"white_player_index": players.index(self.white_player),
                      "black_player_index": players.index(self.black_player),
                      "score": self.score}
        return serialized


class Member:
    """Represent a member of the chess club."""

    def __init__(self, **kwargs):
        self.surname = kwargs.get("surname", "")
        self.name = kwargs.get("name", "")
        self.birthdate = kwargs.get("birthdate", 0)
        self.gender = kwargs.get("gender", "")
        self.ranking = kwargs.get("ranking", "")
        self.discriminator = kwargs.get("discriminator", 0)

    def to_dict(self):
        """Serialize an instance of a member"""
        serialized_member = {name: value for name, value in self.__dict__.items()}
        return serialized_member

    def save(self):
        """Add or update a member in the database"""
        member_tables = TinyDB("db.json").table("members")
        member = Query()
        member_tables.upsert(self.to_dict(), (member.surname == self.surname &
                                              member.name == self.name &
                                              member.birthdate == self.birthdate &
                                              member.gender == self.gender &
                                              member.discriminator == self.discriminator))

    @property
    def already_exist(self):
        member_tables = TinyDB("db.json").table("members")
        member = Query()
        return len(member_tables.search(member.surname == self.surname &
                                        member.name == self.name &
                                        member.birthdate == self.birthdate &
                                        member.gender == self.gender))

    @classmethod
    def get_member(cls, name, surname):
        member_tables = TinyDB("db.json").table("members")
        member = Query()
        return member_tables.search(member.name == name & member.surname == surname)


class Player:
    """Represent a player in a tournament."""
    def __init__(self, **kwargs):
        self.member = kwargs["member"]
        if self.member.discriminator != 0:
            self.name = f"{self.member.name}{self.member.discriminator}"
        else:
            self.name = self.member.name
        self.people_played_against = kwargs.get("people_played_against", dict())
        self.points = kwargs.get("people_played_against", 0)

    def to_dict(self, participants):
        """Serialize an instance of a player"""
        serialized_player = {"member_index": participants.index(self.member),
                             "people_played_against_index": {participants.index(participant):
                                                             self.people_played_against[participant]
                                                             for participant in self.people_played_against},
                             "points": self.points}
        return serialized_player

    def least_played_from(self, players):
        """Return the player who has been faced the least in a list."""
        comparison_list = [(player, self.people_played_against.get(player.member, 0)) for player in players]
        comparison_list.sort(key=lambda element: element[0].points, reverse=True)
        comparison_list.sort(key=lambda element: element[1])
        return comparison_list[0][0]

    def played_against(self, player):
        """Change the amount of time a player has been faced by another."""
        if player.member in self.people_played_against:
            self.people_played_against[player.member] += 1
        else:
            self.people_played_against[player.member] = 1

    def has_played_against(self, player):
        """Return a boolean determining if two players have faced each other."""
        return player.member in self.people_played_against


def unserialize_member(serialized):
    """Create an instance of a member from a dictionary."""
    return Member(**serialized)


def unserialize_player(serialized, participants):
    """Create an instance of a player from a dictionary.

    It should only be used when creating/loading an instance of a tournament. It also requires the list of participants
    in the tournament."""
    serialized["member"] = participants[serialized["member_index"]]
    serialized["people_played_against"] = {participants[index]: serialized["people_played_against_index"][index]
                                           for index in serialized["people_played_against_index"]}
    return Player(**serialized)


def unserialize_game(serialized, players):
    """Create an instance of a game from a dictionary.

    It should only be used when creating/loading an instance of a tournament. It also requires the list of players
    in the tournament."""
    serialized["white_player"] = players[serialized["white_player_index"]]
    serialized["black_player"] = players[serialized["black_player_index"]]
    return Game(**serialized)


def unserialize_round(serialized, players):
    """Create an instance of a round from a dictionary.

    It should only be used when creating/loading an instance of a tournament. It also requires the list of players
    in the tournament."""
    serialized["players"] = players
    for i in range(len(serialized["games"])):
        serialized["games"][i] = unserialize_game(serialized["games"][i], players)
    return Round(**serialized)


def unserialize_tournament(serialized):
    """Create an instance of a tournament"""
    for i in range(len(serialized["participants"])):
        serialized["participants"][i] = unserialize_member(serialized["participants"][i])
    for i in range(len(serialized["players"])):
        serialized["players"][i] = unserialize_player(serialized["players"][i], serialized["participants"])
    for i in range(len(serialized["rounds"])):
        serialized["rounds"][i] = unserialize_round(serialized["rounds"][i],  serialized["players"])
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
