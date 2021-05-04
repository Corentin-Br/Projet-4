"""Implement all exceptions needed"""


class TooManyParticipantsError(Exception):
    """Raised when trying to add too many participants in the tournament."""
    pass


class NotEnoughPlayersError(Exception):
    """Raised when there are fewer players than expected in the tournament."""
    pass


class TournamentStartedError(Exception):
    """Raised when trying to add participants when the tournament has already started."""
    pass


class TooManyRoundsError(Exception):
    """Raised when trying to add a round when the expected number of rounds has been played."""
    pass


class GameNotOverError(Exception):
    """Raised when trying to finish a round while a game result has not been given."""
    def __init__(self, game):
        self.game_not_finished = game


class PreviousRoundNotFinishedError(Exception):
    """Raised when trying to create a new round when the previous one is not finished."""
    pass


class AlreadyInTournamentError(Exception):
    """Raised when trying to add the same member twice in a tournament."""
    def __init__(self, member):
        self.problem_member = member


class NotInTournamentError(Exception):
    """Raised when trying to remove a player not already in the tournament."""
    def __init__(self, member):
        self.problem_member = member