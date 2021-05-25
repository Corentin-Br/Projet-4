"""Implement all classes required to create and play a complete tournament"""
from time import time
from datetime import datetime
from random import sample

from . import pairing, exceptions, db


class Tournament:
    """Class representing a complete Tournament."""

    def __init__(self, *, name, place, date, max_round, participant_amount, tournament_type, description,
                 participants=None, players=None, rounds=None, is_started=False):
        self.name = name.capitalize()
        self.place = place
        # the dates are given as a string in the format dd/mm/yyyy dd/mm/yyyy_.... during the creation of the
        # tournament.
        self.date = [datetime.strptime(date, "%d/%m/%Y") for date in date.split()]
        self.max_round = int(max_round)
        self.type = tournament_type.capitalize()
        self.description = description.capitalize()
        self.participant_amount = int(participant_amount)
        if self.participant_amount % 2 != 0:
            raise exceptions.OddParticipantError

        self.participants = participants if type(participants) == list else []
        self.players = players if type(players) == list else []
        self.rounds = rounds if type(rounds) == list else []
        # The user COULD send something for those three attributes. So if they do, it's cancelled
        # because it can't be a list (it's necessarily a string). The user must not be able to change those values.
        self.is_started = is_started

    def add_participant(self, member):
        """Add a participant for the tournament."""
        if self.is_started:
            raise exceptions.TournamentStartedError
        else:
            if len(self.participants) < self.participant_amount:
                if member not in self.participants:
                    self.participants.append(member)
                else:
                    raise exceptions.AlreadyInTournamentError(member)
            else:
                raise exceptions.TooManyParticipantsError

    def remove_participant(self, member):
        """Remove a participant from the tournament."""
        if self.is_started:
            raise exceptions.TournamentStartedError
        elif member in self.participants:
            self.participants.remove(member)
        else:
            raise exceptions.NotInTournamentError(member)

    def start(self):
        """Generate the players and prevent adding more participants."""
        if len(self.participants) < self.participant_amount:
            raise exceptions.NotEnoughPlayersError
        elif self.is_started:
            raise exceptions.AlreadyStartedError
        else:
            self.players = [Player(**{"member": member}) for member in self.participants]
            self.is_started = True

    def create_round(self):
        """Create a round."""
        if not self.is_started:
            raise exceptions.TournamentNotStartedError
        if len(self.rounds) == 0 or (len(self.rounds) < self.max_round and self.rounds[-1].finished):
            starting_time = datetime.fromtimestamp(time()).strftime("%H:%M")
            new_round = Round(round_number=len(self.rounds) + 1,
                              players=self.players,
                              starting_time=starting_time)
            self.rounds.append(new_round)
            new_round.create_games()
        elif not self.rounds[-1].finished:
            raise exceptions.PreviousRoundNotFinishedError
        elif len(self.rounds) >= self.max_round:
            raise exceptions.TooManyRoundsError

    @property
    def result(self):
        """A list of participants sorted by score, to be used to display the result of the tournament."""
        return sorted(self.players, key=lambda player: player.points, reverse=True)

    @property
    def to_dict(self):
        """Return a serialized instance of a tournament."""
        participants_index = [participant.identifiant for participant in self.participants]
        serialized_rounds = [game_round.to_dict(self.players) for game_round in self.rounds]
        serialized_players = [player.to_dict(self.participants) for player in self.players]
        serialized_tournament = {"name": self.name,
                                 "place": self.place,
                                 "date": " ".join([date.strftime("%d/%m/%Y") for date in self.date]),
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
        """Add or update a tournament in the database."""
        db.TOURNAMENT_TABLES.upsert(self.to_dict, ((db.QUERY.name == self.name) &
                                                   (db.QUERY.place == self.place) &
                                                   (db.QUERY.date == " ".join([date.strftime("%d/%m/%Y")
                                                                               for date in self.date]))))

    @property
    def already_exist(self):
        """Return a boolean determining if the tournament already exists."""
        return db.TOURNAMENT_TABLES.count((db.QUERY.name == self.name) &
                                          (db.QUERY.place == self.place) &
                                          (db.QUERY.date == " ".join([date.strftime("%d/%m/%Y")
                                                                      for date in self.date]))) != 0

    @classmethod
    def get_tournament(cls, name: str):
        """Return all tournaments with a specific name."""
        return [unserialize_tournament(tournament) for tournament in
                db.TOURNAMENT_TABLES.search(db.QUERY.name == name.capitalize())]

    @classmethod
    def get_all_tournaments(cls):
        """Return all tournaments in the database."""
        return [unserialize_tournament(tournament) for tournament in db.TOURNAMENT_TABLES.all()]

    @property
    def to_display(self):
        """A string that contains all relevant data of the tournament to be displayed."""
        return "   ".join([self.name,
                           self.place,
                           " et ".join([date.strftime("%d/%m/%Y") for date in self.date]),
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
        if self.finished:
            raise exceptions.AlreadyFinishedError
        for game in self.games:
            if game.score == "0-0":
                raise exceptions.GameNotOverError(game)
        self.ending_time = datetime.fromtimestamp(time())
        self.finished = True

    def to_dict(self, players):
        """Serialize an instance of a round."""
        serialized = {"round_number": self.number,
                      "starting_time": self.starting_time.strftime("%H:%M"),
                      "ending_time": self.ending_time.strftime("%H:%M"),
                      "finished": self.finished,
                      "games": [game.to_dict(players) for game in self.games]}
        return serialized

    @property
    def to_display(self):
        """A string that contains all relevant data of the round to be displayed."""
        games = '\n'.join([game.to_display for game in self.games])
        return f"{self.name}    a commencé à {self.starting_time.strftime('%H:%M')}   " \
               f"a fini à {self.ending_time.strftime('%H:%M')}\n{games}"


class Game:
    """Class representing a game between two players."""
    def __init__(self, players=None, score="0-0", new=True, white_player=None, black_player=None):
        if new:
            players_random = sample(players, k=2)
            self.white_player = players_random[0]
            self.black_player = players_random[1]
        else:
            self.white_player = white_player
            self.black_player = black_player
        self.score = score

    @property
    def name(self):
        """A string containing the name of the two players, with the white player first."""
        return f"{self.white_player.name} VS {self.black_player.name}"

    def set_score(self, score: str):
        """Create the result of the game."""
        self.score = score
        self.give_points()
        self.white_player.played_against(self.black_player)
        self.black_player.played_against(self.white_player)

    def give_points(self):
        """Give the points to the players."""
        score = self.score.split("-")
        if score[0] == score[1]:
            score = (0.5, 0.5)
        self.white_player.points += float(score[0])
        self.black_player.points += float(score[1])

    def to_dict(self, players):
        """Serialize an instance of a game."""
        serialized = {"white_player_index": players.index(self.white_player),
                      "black_player_index": players.index(self.black_player),
                      "score": self.score}
        return serialized

    @property
    def to_display(self):
        """A string that contains all relevant data of the game to be displayed."""
        return f"{self.name}    {self.score}"


class Member:
    """Represent a member of the chess club."""

    def __init__(self, surname: str, name: str, birthdate, gender, ranking, discriminator=0):
        self.surname = surname.upper()
        self.name = name.capitalize()
        self.birthdate = datetime.strptime(birthdate, "%d/%m/%Y")
        self.gender = gender.capitalize()
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
    def to_dict(self):
        """Serialize an instance of a member."""
        serialized_member = {"surname": self.surname,
                             "name": self.name,
                             "birthdate": self.birthdate.strftime("%d/%m/%Y"),
                             "gender": self.gender,
                             "ranking": self.ranking,
                             "discriminator": self.discriminator}
        return serialized_member

    def save(self):
        """Add or update a member in the database."""
        db.MEMBER_TABLES.upsert(self.to_dict, ((db.QUERY.surname == self.surname) &
                                               (db.QUERY.name == self.name) &
                                               (db.QUERY.discriminator == self.discriminator)))

    @property
    def identifiant(self):
        """The unique identifiant in the database."""
        result = db.MEMBER_TABLES.get((db.QUERY.surname == self.surname) &
                                      (db.QUERY.name == self.name) &
                                      (db.QUERY.discriminator == self.discriminator))
        return result.doc_id

    @property
    def to_display(self):
        """Return a string that contains all relevant data of the member to be displayed."""
        return "   ".join([self.surname,
                           self.name,
                           self.birthdate.strftime("%d/%m/%Y"),
                           self.gender,
                           str(self.ranking),
                           str(self.discriminator)])

    @property
    def already_exist(self):
        """Return the number of members in the database that have the same name and surname."""
        return db.MEMBER_TABLES.count((db.QUERY.surname == self.surname) &
                                      (db.QUERY.name == self.name))

    @classmethod
    def get_member(cls, name: str, surname: str, discriminator=None):
        """Return all the members with a specific name and surname in the database."""
        if discriminator:
            return [Member(**member) for member in db.MEMBER_TABLES.search((db.QUERY.name == name.capitalize()) &
                                                                           (db.QUERY.surname == surname.upper()) &
                                                                           (db.QUERY.discriminator == discriminator))]
        else:
            return [Member(**member) for member in db.MEMBER_TABLES.search((db.QUERY.name == name.capitalize()) &
                                                                           (db.QUERY.surname == surname.upper()))]

    @classmethod
    def get_member_from_id(cls, identifiant):
        """Return a member from the identifiant in the database."""
        if db.MEMBER_TABLES.contains(doc_id=identifiant):
            member = db.MEMBER_TABLES.get(doc_id=identifiant)
        else:
            raise exceptions.NotInDatabaseError
        return Member(**member)

    @classmethod
    def get_all_members(cls):
        """Return all the members in the database."""
        return [Member(**member) for member in db.MEMBER_TABLES.all()]


class Player:
    """Represent a player in a tournament."""
    def __init__(self, member, people_played_against=None, points=0):
        self.member = member

        self.people_played_against = people_played_against if people_played_against else {}
        self.points = points

    def to_dict(self, participants):
        """Serialize an instance of a player."""
        serialized_player = {"member_index": participants.index(self.member),
                             "people_played_against": self.people_played_against,
                             "points": self.points}
        return serialized_player

    def least_played_from(self, players):
        """Return the player who has been faced the least in a list."""
        comparison_list = [(player, self.people_played_against.get(player.name, 0)) for player in players]
        comparison_list.sort(key=lambda element: element[0].points, reverse=True)
        comparison_list.sort(key=lambda element: element[1])
        return comparison_list[0][0]

    def played_against(self, player):
        """Change the amount of time a player has been faced by another."""
        if player.name in self.people_played_against:
            self.people_played_against[player.name] += 1
        else:
            self.people_played_against[player.name] = 1

    def has_played_against(self, player):
        """Return a boolean determining if two players have faced each other."""
        return player.name in self.people_played_against

    @property
    def name(self):
        """Return a string with the name, surname and discriminator of a player."""
        if self.member.discriminator != 0:
            return f"{self.member.surname} {self.member.name} {self.member.discriminator}"
        else:
            return f"{self.member.surname} {self.member.name}"

    @property
    def to_display(self):
        """Return a string that contains all relevant data of the player to be displayed."""
        return "   ".join([self.name, str(self.points)])


def unserialize_member(serialized):
    """Create an instance of a member from a dictionary."""
    return Member(**serialized)


def unserialize_player(serialized, participants):
    """Create an instance of a player from a dictionary.

    It should only be used when creating/loading an instance of a tournament. It also requires the list of participants
    in the tournament."""
    return Player(member=participants[serialized["member_index"]],
                  people_played_against=serialized["people_played_against"],
                  points=serialized["points"])


def unserialize_game(serialized, players):
    """Create an instance of a game from a dictionary.

    It should only be used when creating/loading an instance of a tournament. It also requires the list of players
    in the tournament."""
    return Game(new=False,
                white_player=players[serialized["white_player_index"]],
                black_player=players[serialized["black_player_index"]],
                score=serialized["score"])


def unserialize_round(serialized, players):
    """Create an instance of a round from a dictionary.

    It should only be used when creating/loading an instance of a tournament. It also requires the list of players
    in the tournament."""
    return Round(players=players, round_number=serialized["round_number"], starting_time=serialized["starting_time"],
                 games=[unserialize_game(game, players) for game in serialized["games"]],
                 ending_time=serialized["ending_time"], finished=serialized["finished"])


def unserialize_tournament(serialized):
    """Create an instance of a tournament from a dictionary."""
    try:
        participants = [Member.get_member_from_id(participant) for participant in serialized["participants"]]
    except exceptions.NotInDatabaseError:
        raise exceptions.InvalidTournamentError(serialized)
    players = [unserialize_player(player, participants) for player in serialized["players"]]
    return Tournament(name=serialized["name"], place=serialized["place"], date=serialized["date"],
                      max_round=serialized["max_round"], participant_amount=serialized["participant_amount"],
                      tournament_type=serialized["tournament_type"], description=serialized["description"],
                      participants=participants, players=players,
                      rounds=[unserialize_round(game_round, players) for game_round in serialized["rounds"]],
                      is_started=serialized["is_started"])


def create_pairs(player_list):
    """Return a dictionary pairing players for a round."""
    pairs = pairing.first_pairing(player_list)
    if len(pairs) == len(player_list):
        return pairs
    else:
        return pairing.pairing_fixing(player_list, pairs, (len(player_list) - len(pairs)) // 2)


def make_pairs_unique(pairs):
    """Turn a dictionary pairing players into a list that can be used to generate rounds."""
    unique_pairs = []
    for key, value in pairs.items():
        j = {key, value}
        if j not in unique_pairs:
            unique_pairs.append(j)
    unique_pairs = [tuple(element) for element in unique_pairs]
    return unique_pairs
