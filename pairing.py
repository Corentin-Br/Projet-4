""""""
import itertools


def first_pairing(player_list):
    """returns a dictionary that matches players starting from the one with the highest score. This may not yield all
    matches we want due to non-predictive conditions on the matchmaking"""
    pairs = dict()
    for player_one in player_list:
        if player_one in pairs:
            continue
        for player_two in player_list:
            if player_one.has_played_against(player_two) or player_two in pairs or player_two is player_one:
                continue
            else:
                pairs = pair(player_one, player_two, pairs)
                break
    return pairs


def get_enough_players(player_list, current_pairing, number_of_matches_not_done):
    """returns a list that has all players not in current_pairing and enough players from player_list, starting
    from the end to play number_of_matches_not_done"""
    items_found = 0
    players_to_pair = [player for player in player_list if player not in current_pairing]
    for player in player_list.__reversed__():
        if player in current_pairing and player not in players_to_pair:
            players_to_pair.append(player)
            players_to_pair.append(current_pairing[player])  # player will have someone else reassigned as its pair. SO
            # of course
            items_found += 1
        if items_found == number_of_matches_not_done:
            break
    return players_to_pair


def pair(player_one, player_two, current_pairing):
    """add (player_one, player_two) and (player_two, player_one) in current_pairing items"""
    current_pairing[player_one] = player_two
    current_pairing[player_two] = player_one
    return current_pairing


def pairing_fixing(player_list, current_pairing, number_of_matches_not_done):
    """"""
    print("I have started fixing")
    players_to_pair = get_enough_players(player_list, current_pairing, number_of_matches_not_done)
    all_valid_pairings = get_all_valid_matchups(players_to_pair, number_of_matches_not_done)
    if len(all_valid_pairings) == 0:
        if number_of_matches_not_done >= len(player_list) // 2:
            return least_played_pairing(player_list)
        else:
            return pairing_fixing(player_list, current_pairing, number_of_matches_not_done + 1)
    else:
        final_pairing = all_valid_pairings[0]
    for player_one, player_two in final_pairing:
        current_pairing = pair(player_one, player_two, current_pairing)
    return current_pairing


def least_played_pairing(player_without_matches):
    """pairs players from player_without_matches with the player they played the least. The players with the highest
    score have priority"""
    pairs = dict()
    for current_player in player_without_matches:
        if current_player in pairs:
            continue
        possible_opponents = [player for player in player_without_matches if (player not in pairs
                                                                              and player != current_player)]
        least_played = current_player.least_played_from(possible_opponents)
        pairs = pair(current_player, least_played, pairs)
    return pairs


def is_valid(pairings):
    """determines if every tuple from pairings has no intersection with every other tuple from pairings"""
    for n in range(len(pairings)):
        for m in range(n):
            if set(pairings[n]) & set(pairings[m]) != set():
                return False
    return True


def is_allowed(pairings):
    """determines if every pair of players in pairings can play against each other"""
    for player_1, player_2 in pairings:
        if player_1.has_played_against(player_2):
            return False
    return True


def game_allowed(pairings):
    return is_valid(pairings) and is_allowed(pairings)


def get_all_valid_matchups(players_to_pair, number_of_matches_not_done, players_per_match=2, func=game_allowed):
    """returns a list that has all possible combination of number_of_matches_not_done tuples of player_per_match
    element from players_to_pair. The list is filtered by func."""
    # First we get all possible combination (for example with (a,b,c,d) we'll get [(a,b), (a,c), (a,d), (b,c), (b,d),
    # (c,d)] (or something equivalent for our purposes))
    # Note that players_to_pair must NOT have repetitions for this to work correctly
    all_pairings = [combination for combination in itertools.combinations(players_to_pair, players_per_match)]
    # Then we get a list of combination of those combinations. With the example above, assuming we need to create 2
    # games, we should get : [((a,b),(a,c)), ((a,b),(a,d)).......]
    all_potential_combinations_of_pairings = [pairings for pairings in
                                              itertools.combinations(all_pairings, number_of_matches_not_done + 1)]
    # Finally we filter the results according to our function.
    all_valid_pairings = list(filter(func, all_potential_combinations_of_pairings))
    return all_valid_pairings
