"""Implement all classes required to create and play a complete tournament"""
from time import time
from datetime import datetime
from random import sample
from re import IGNORECASE

from tinydb import TinyDB, Query

import pairing
from exceptions import *


class Tournament:
    """Class representing a complete Tournament."""

    def __init__(self, *, name, place, date, max_round, participant_amount, tournament_type, description,
                 participants=None, players=None, rounds=None, is_started=False):
        self.name = name
        self.place = place
        # the dates are given as a string in the format dd/mm/yyyy dd/mm/yyyy_.... during the creation of the
        # tournament.
        self.date = [datetime.strptime(date, "%d/%m/%Y") for date in date.split()]
        self.max_round = int(max_round)
        self.type = tournament_type
        self.description = description
        self.participant_amount = int(participant_amount)

        self.participants = participants if type(participants) == list else []
        self.players = players if type(players) == list else []
        self.rounds = rounds if type(rounds) == list else []
        # The user COULD send something for those three attributes. So if they do, it's cancelled
        # because it can't be a list (it's necessarily a string). The user must not be able to change those values.
        self.is_started = is_started

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
        if self.is_started:
            raise TournamentStartedError
        elif member in self.participants:
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
            starting_time = datetime.fromtimestamp(time()).strftime("%H:%M")
            new_round = Round(round_number=len(self.rounds) + 1,
                              players=self.players,
                              starting_time=starting_time)
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

    @property
    def to_dict(self):
        """Return a serialized instance of a tournament"""
        participants_index = [participant.identifiant for participant in self.participants]
        serialized_rounds = [game_round.to_dict(self.players) for game_round in self.rounds]
        serialized_players = [player.to_dict(self.participants) for player in self.players]
        serialized_tournament = {"name": self.name,
                                 "place": self.place,
                                 "date": "_".join([date.strftime("%d/%m/%Y") for date in self.date]),
                                 "max_round": self.max_round,
                                 "tournament_type": self.type,
                                 "description": self.description,
                                 "participant_amount": self.participant_amount,
                                 "participants": participants_index,
                                 "rounds": serialized_rounds,
                                 "players": serialized_players,
                                 "is_started": self.is_started}
        return serialized_tournament

    def save(self):
        """Add or update a tournament in the database"""
        db = TinyDB("db.json")
        tournament_tables = db.table("tournaments")
        tournament = Query()
        tournament_tables.upsert(self.to_dict, ((tournament.name.matches(self.name, flags=IGNORECASE)) &
                                                (tournament.place.matches(self.place, flags=IGNORECASE)) &
                                                (tournament.date == "_".join([date.strftime("%d/%m/%Y")
                                                                              for date in self.date]))))

    @classmethod
    def get_tournament(cls, name):
        """Return all tournaments with a specific name"""
        tournament_tables = TinyDB("db.json").table("tournaments")
        tournament_query = Query()
        return [unserialize_tournament(tournament) for tournament in
                tournament_tables.search(tournament_query.name.matches(str(name), flags=IGNORECASE))]

    @classmethod
    def get_all_tournaments(cls):
        """Return all tournaments in the database"""
        tournament_tables = TinyDB("db.json").table("tournaments")
        return [unserialize_tournament(tournament) for tournament in tournament_tables.all()]

    @property
    def to_display(self):
        return "   ".join([self.name,
                           self.place,
                           "et ".join([date.strftime("%d/%m/%Y") for date in self.date]),
                           self.type,
                           self.description])


class Round:
    """Class representing a round."""
    def __init__(self, *,  players, round_number, starting_time,
                 games=None, ending_time="00:00", finished=False):
        self.players = players
        self.number = int(round_number)
        self.starting_time = datetime.strptime(starting_time, "%H:%M")

        self.name = f"Round {self.number}"

        self.games = games if games else []
        self.ending_time = datetime.strptime(ending_time, "%H:%M")
        self.finished = finished

    def create_games(self):
        """Create all games for the round."""
        players = sorted(self.players, key=lambda player: player.member.ranking)
        ecart = len(players) // 2
        if self.number == 1:
            for i in range(ecart):
                self.games.append(Game(**{"players": (players[i], players[i + ecart])}))
        else:
            players = sorted(players, key=lambda joueur: joueur.points, reverse=True)
            for pair in make_pairs_unique(create_pairs(players)):
                self.games.append(Game(players=(pair[0], pair[1])))

    def finish(self):
        """Check that all games are over and get the time the round ended at."""
        for game in self.games:
            if not game.winner:
                raise GameNotOverError(game)
        self.ending_time = datetime.fromtimestamp(time())
        self.finished = True

    def to_dict(self, players):
        """Serialize an instance of a round"""
        serialized = {"number": self.number,
                      "starting_time": self.starting_time.strftime("%H:%M"),
                      "ending_time": self.ending_time.strftime("%H:%M"),
                      "finished": self.finished,
                      "games": [game.to_dict(players) for game in self.games]}
        return serialized

    def to_display(self):
        return "   ".join([self.name,
                           f"a commencé à {self.starting_time.strftime('%H:%M')}",
                           f"a fini à {self.starting_time.strftime('%H:%M')}",
                           " et ".join(game.name for game in self.games)])


class Game:
    """Class representing a game between two players."""
    def __init__(self, players=None, score="0-0", new=True, white_player=None, black_player=None):
        if not new:
            self.white_player = white_player
            self.black_player = black_player
        else:
            players_random = sample(players, k=2)
            self.white_player = players_random[0]
            self.black_player = players_random[1]
        self.name = f"{self.white_player.name} VS {self.black_player.name}"
        self.score = score

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

    @property
    def to_display(self):
        return "   ".join([self.name, self.score])


class Member:
    """Represent a member of the chess club."""

    def __init__(self, surname, name, birthdate, gender, ranking, discriminator=0):
        self.surname = surname.upper()
        self.name = name.capitalize()
        self.birthdate = datetime.strptime(birthdate, "%d/%m/%Y")
        self.gender = gender
        self.ranking = int(ranking)
        self.discriminator = discriminator

    # Changing the way equality is defined so that we compare all the attributes instead of the memory address.
    # This makes it much easier to check for a member already participating in a tournament
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def complete_name(self):
        return self.surname + self.name

    @property
    def to_dict(self):
        """Serialize an instance of a member"""
        serialized_member = {"surname": self.surname,
                             "name": self.name,
                             "birthdate": self.birthdate.strftime("%d/%m/%Y"),
                             "gender": self.gender,
                             "ranking": self.ranking,
                             "discriminator": self.discriminator}
        return serialized_member

    def save(self):
        """Add or update a member in the database"""
        member_tables = TinyDB("db.json").table("members")
        member = Query()
        member_tables.upsert(self.to_dict, ((member.surname.matches(self.surname, flags=IGNORECASE)) &
                                            (member.name.matches(self.name, flags=IGNORECASE)) &
                                            (member.discriminator == self.discriminator)))

    @property
    def identifant(self):
        member_tables = TinyDB("db.json").table("members")
        member = Query()
        result = member_tables.get((member.surname.matches(self.surname, flags=IGNORECASE)) &
                                   (member.name.matches(self.name, flags=IGNORECASE)) &
                                   (member.discriminator == self.discriminator))
        return result.doc_id

    @property
    def to_display(self):
        return "   ".join([self.surname,
                           self.name,
                           self.birthdate.strftime("%d/%m/%Y"),
                           self.gender,
                           str(self.ranking),
                           str(self.discriminator)])

    @property
    def already_exist(self):
        """Return the number of members in the database that have the same name, surname, birthdate and gender."""
        member_tables = TinyDB("db.json").table("members")
        member = Query()
        return member_tables.count((member.surname.matches(str(self.surname), flags=IGNORECASE)) &
                                   (member.name.matches(str(self.name), flags=IGNORECASE)))

    @classmethod
    def get_member(cls, name, surname, discriminator=None):
        """Return all the members with a specific name and surname in the database"""
        member_tables = TinyDB("db.json").table("members")
        member = Query()
        if discriminator:
            return [Member(**member) for member in member_tables.search((member.name.matches(str(name),
                                                                                             flags=IGNORECASE)) &
                                                                        (member.surname.matches(str(surname),
                                                                                                flags=IGNORECASE)) &
                                                                        (member.discriminator == discriminator))]
        else:
            return [Member(**member) for member in member_tables.search((member.name.matches(str(name),
                                                                                             flags=IGNORECASE)) &
                                                                        (member.surname.matches(str(surname),
                                                                                                flags=IGNORECASE)))]

    @classmethod
    def get_member_from_id(cls, identifiant):
        member_tables = TinyDB("db.json").table("members")
        if member_tables.contains(doc_id=identifiant):
            member = member_tables.get(doc_id=identifiant)
        else:
            raise NotInDatabaseError
        return Member(**member)

    @classmethod
    def get_all_members(cls):
        """Return all the members in the database"""
        member_tables = TinyDB("db.json").table("members")
        return [Member(**member) for member in member_tables.all()]


class Player:
    """Represent a player in a tournament."""
    def __init__(self, member, people_played_against=None, points=0):
        self.member = member

        self.people_played_against = people_played_against if people_played_against else {}
        self.points = points

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

    @property
    def name(self):
        """Return a string with the name surname and discriminator of a player."""
        if self.member.discriminator != 0:
            return f"{self.member.surname} {self.member.name} {self.member.discriminator}"
        else:
            return f"{self.member.surname} {self.member.name}"

    @property
    def to_display(self):
        return "   ".join([self.name, str(self.points)])


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
    return Game(new=False, **serialized)


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
        try:
            serialized["participants"][i] = Member.get_member_from_id(serialized["participants"][i])
        except NotInDatabaseError:
            raise InvalidTournamentError(serialized)
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
