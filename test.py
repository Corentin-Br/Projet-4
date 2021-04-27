import itertools
import random
import time


class Tournoi:
    NOMBRE_PARTICIPANTS_MAX = 8

    def __init__(self, **kwargs):  # #TODO: Doit inclure un attribut rondes_max (présent dans le controlleur)
        self.participants = []
        self.rondes = []
        for nom, valeur in kwargs.items():
            setattr(self, nom, valeur)

    def ajouter_participant(self, joueur):
        if len(self.participants) < self.NOMBRE_PARTICIPANTS_MAX:
            self.participants.append(joueur)
        else:
            raise TropDeParticipantsError

    def creer_une_ronde(self):
        if len(self.rondes) < self.rondes_max:
            self.rondes.append(Ronde(len(self.rondes)+1, self.joueurs))
        else:
            raise TropDeRondesError


class TropDeParticipantsError(Exception):
    pass


class TropDeRondesError(Exception):
    pass


class Ronde:
    def __init__(self, num_de_ronde, joueurs):
        self.joueurs = joueurs
        self.numero = num_de_ronde
        self.matchs = []

    def creer_matchs(self):
        self.joueurs.sort(key=lambda joueur: joueur.classement)  # Le 1° est le plus fort, donc
        # le tri ascendant marche bien.
        ecart = len(self.joueurs) // 2
        if self.numero == 1:
            for i in range(ecart):
                self.matchs.append(Match(self.joueurs[i], self.joueurs[i + ecart]))
        else:
            self.joueurs.sort(key=lambda joueur: joueur.points, reverse=True)  # #Le joueur avec le plus de points doit
            # être le plus fort donc inversion.


class Match:
    def __init__(self, joueur_1, joueur_2):
        self.joueur_1 = joueur_1
        self.joueur_2 = joueur_2


class Player:
    def __init__(self, number):
        # for name, value in kwargs.items():
        # setattr(self, name, value)
        self.played_against = list()
        self.name = f"joueur {number}"
        self.points = 0

    def has_played_against(self, player):
        return player in self.played_against


def pairing(player_list):
    pairs = first_pairing(player_list)
    if len(pairs) == len(player_list):
        return pairs
    else:
        return pairing_fixing(player_list, pairs, (len(player_list)-len(pairs))//2)


def first_pairing(player_list):
    pairs = dict()
    for player_one in player_list:
        if player_one in pairs:
            continue
        for player_two in player_list:
            if player_one.has_played_against(player_two) or player_two in pairs or player_two is player_one:
                continue
            else:
                pairs[player_one] = player_two
                pairs[player_two] = player_one
                break
    return pairs

def pairing_fixing(player_list, current_pairing, number_of_matches_not_done):
    items_found = 0
    items_to_pair = [player for player in player_list if player not in current_pairing]
    for player in player_list.__reversed__():
        if player in current_pairing and player not in items_to_pair:
            items_to_pair.append(player)
            items_to_pair.append(current_pairing[player])
            items_found += 1
        if items_found == number_of_matches_not_done:
            break
    all_pairings = [combination for combination in itertools.combinations(items_to_pair, 2)]
    all_combinations_of_pairings = itertools.combinations(all_pairings, number_of_matches_not_done+1)
    all_potential_combinations_of_pairings = [pairings for pairings in all_combinations_of_pairings]
    all_valid_pairings = list(filter(match_allowed, all_potential_combinations_of_pairings))
    if len(all_valid_pairings) == 0:
        if number_of_matches_not_done >= len(player_list)//2:
            return first_pairing(player_list) # TODO: Need to change that to a new function that pairs according to the number of times you played against someone. Peut-être en remplaçant le "in played_against"
                                              #       par "<= minimum de fois qu'un match est répété.

                                              # TODO: Une autre anomalie, il semble possible d'arriver ici SANS qu'il soit nécessairement impossible de faire un appariement. Ca ne se produit pas pour 4 rondes, mais ça se produit pour 7 rondes. Il faut vérifier mes conditions. :(
        else:
            return pairing_fixing(player_list, current_pairing, number_of_matches_not_done+1)
    else:
        final_pairing = all_valid_pairings[0]
    for player_one, player_two in final_pairing:
        current_pairing[player_one] = player_two
        current_pairing[player_two] = player_one
    return current_pairing


def is_valid(pairings):
    """determines if every tuple from a list of tuples has no intersection with every other tuple"""
    for n in range(len(pairings)):
        for m in range(n):
            if set(pairings[n]) & set(pairings[m]) != set():
                return False
    return True


def is_allowed(pairings):
    """determines if every pair of players in a list of pair of players can play against each other"""
    for player_1, player_2 in pairings:
        if player_1.has_played_against(player_2):
            return False
    return True


def match_allowed(pairings):
    return is_valid(pairings) and is_allowed(pairings)


def multiple_pairing(): # A virer ça, c'est uniquement pour du test
    all_players = [Player(i) for i in range(8)]
    for i in range(7):
        k = pairing(all_players)
        for player in k:
            player.played_against.append(k[player])
            player.points += random.randint(0,10)
        all_players.sort(key=lambda player: player.points)
    answer = []
    return [player.played_against for player in all_players]


if __name__ == "__main__": # A virer ça, c'est uniquement pour du test
    for i in range(1000):
        k = multiple_pairing()
        for mini_list in k:
            print(len(mini_list))
        print("another one")
    print("finished")
