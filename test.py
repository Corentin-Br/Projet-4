import pairing


class Tournament:
    MAX_PARTICIPANTS_AMOUNT = 8

    def __init__(self, **kwargs):  # TODO: Doit inclure un attribut max_round (présent dans le controlleur)
        self.participants = []
        self.rounds = []
        for name, value in kwargs.items():
            setattr(self, name, value)

    def add_participant(self, player):
        if len(self.participants) < self.MAX_PARTICIPANTS_AMOUNT:
            self.participants.append(player)
        else:
            raise TooManyParticipantsError

    def create_round(self):
        if len(self.rounds) < self.max_round:
            self.rounds.append(Round(len(self.rounds) + 1, self.joueurs))
        else:
            raise TooManyRoundsError


class TooManyParticipantsError(Exception):
    pass


class TooManyRoundsError(Exception):
    pass


class Round:
    def __init__(self, round_number, players):
        self.players = players
        self.number = round_number
        self.games = []

    def create_games(self):
        self.players.sort(key=lambda player: player.ranking)  # Le 1° est le plus fort, donc
        # le tri ascendant marche bien.
        ecart = len(self.players) // 2
        if self.number == 1:
            for i in range(ecart):
                self.games.append(Game(self.players[i], self.players[i + ecart]))
        else:
            self.players.sort(key=lambda joueur: joueur.points, reverse=True)  # Le joueur avec le plus de points doit
            # être le plus fort donc inversion.
            for pair in make_pairs_unique(create_pairs(self.players)):
                self.games.append(Game(pair[0], pair[1]))


class Game:
    def __init__(self, player_one, player_two):
        self.joueur_1 = player_one
        self.joueur_2 = player_two


class Member:
    def __init__(self, **kwargs):
        pass


class Player(Member):
    def __init__(self, number, **kwargs):
        super().__init__(**kwargs)
        # for name, value in kwargs.items():
        # setattr(self, name, value)
        self.people_played_against = dict()  # It will store the name of the player and the number of time he was faced
        self.name = f"joueur {number}"  # Ca, ça sera viré. Pour le moment ça reste des fois que je veuille refaire des
        # tests
        self.points = 0

    def least_played_from(self, players):
        """return the player who has been faced the least in a list"""
        comparison_list = [(player, self.people_played_against.get(player, 0)) for player in players]
        comparison_list.sort(key=lambda element: element[1])
        return comparison_list[0][0]

    def played_against(self, player):
        """Changes the amount of time player has been faced by self"""
        if player in self.people_played_against:
            self.people_played_against[player] += 1
        else:
            self.people_played_against[player] = 1

    def has_played_against(self, player):
        """returns a boolean that described if self has faced player"""
        return player in self.people_played_against


def create_pairs(player_list):
    """returns a dictionary that pairs every player in player_list with another player in accordance to swiss rounds
    rules"""
    pairs = pairing.first_pairing(player_list)
    if len(pairs) == len(player_list):
        return pairs
    else:
        return pairing.pairing_fixing(player_list, pairs, (len(player_list) - len(pairs)) // 2)


def make_pairs_unique(pairs):
    """transform pairs in a list of tuple that can be used to initialize match"""
    unique_pairs = []
    for key, value in pairs.items():
        j = {key, value}
        if j not in unique_pairs:
            unique_pairs.append(tuple(j))
    return unique_pairs


if __name__ == "__main__":
    pass
