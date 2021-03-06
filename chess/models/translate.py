"""Contain all the text required by other modules."""
TRANSLATION = {
    "valid_types": [
        "coup rapide",
        "bullet",
        "blitz"
    ],
    "yes": [
        "oui",
        "o"
    ],
    "no": [
        "non",
        "n"
    ],
    "argument_names": {
        "date_de_naissance": "birthdate",
        "discriminant": "discriminator",
        "numéro_du_match": "match_number",
        "classement": "ranking",
        "nombre_de_participants": "participant_amount",
        "résultat": "result",
        "date": "date",
        "type_de_tournoi": "tournament_type",
        "prénom": "name",
        "nom_du_tournoi": "name",
        "genre": "gender",
        "lieu": "place",
        "nombre_rondes": "max_round",
        "nom": "surname",
        "clé": "key",
        "description": "description",
        "points": "points"
    },
    "command_names": {
        "créer_tournoi": "add_tournament",
        "ajouter_acteur": "add_member",
        "changer_classement": "change_ranking",
        "charger_tournoi": "load_tournament",
        "afficher_acteurs": "display_members",
        "afficher_tournois": "display_tournaments",
        "fermer": "close",
        "afficher_joueurs": "display_players",
        "afficher_participants": "display_participants",
        "afficher_tours": "display_rounds",
        "afficher_tour_actuel": "display_current_games",
        "afficher_matchs": "display_games",
        "ajouter_participant": "add_participant",
        "enlever_participant": "remove_participant",
        "détails": "get_info_player",
        "commencer": "start",
        "tour_suivant": "next_round",
        "finir_tour": "finish_round",
        "résultat": "give_results",
        "finir_tournoi": "finish",
        "exit": "exit"
    },
    "ask_argument": {
        "name_add_tournament": "Quel est le nom du tournoi?",
        "place_add_tournament": "Où se déroule le tournoi?",
        "date_add_tournament": "A quelle(s) date(s) se déroule le tournoi? (format jj/mm/aaaa, avec un espace "
                               "entre chaque date s'il y en a plusieurs).",
        "max_round_add_tournament": "Combien de rondes comportera le tournoi?",
        "participant_amount_add_tournament": "Combien de joueurs participeront au tournoi?",
        "tournament_type_add_tournament": "Quel contrôle de temps sera utilisé pour le tournoi?",
        "name_add_member": "Quel est le prénom du nouveau membre?",
        "surname_add_member": "Quel est le nom de famille du nouveau membre?",
        "birthdate_add_member": "Quel est la date de naissance du nouveau membre?",
        "gender_add_member": "Quel est le genre du nouveau membre?",
        "ranking_add_member": "Quel est le classement du nouveau membre?",
        "name_change_ranking": "Quel est le prénom du membre dont vous voulez changer le classement?",
        "surname_change_ranking": "Quel est le nom de famille du membre dont vous voulez changer le classement?",
        "ranking_change_ranking": "Quel est le nouveau classement du membre dont vous voulez changer le classement?",
        "name_load_tournament": "Quel est le nom du tournoi que vous voulez charger?",
        "name_add_participant": "Quel est le prénom du joueur que vous voulez ajouter au tournoi?",
        "surname_add_participant": "Quel est le nom de famille du joueur que vous voulez ajouter au tournoi?",
        "name_remove_participant": "Quel est le prénom du joueur que vous voulez retirer du tournoi?",
        "surname_remove_participant": "Quel est le nom de famille du joueur que vous voulez retirer du tournoi?",
        "name_get_info_player": "Quel est le prénom du joueur dont vous voulez les détails?",
        "surname_get_info_player": "Quel est le nom de famille du joueur dont vous voulez les détails?",
        "discriminator_get_info_player": "Quel est le discriminant du joueur dont vous voulez les détails?",
        "match_number_give_results": "Quel est le numéro du match dont vous voulez donner le résultat?",
        "result_give_results": "Quel est le résultat du match?"
    },
    "fix_argument": {
        "birthdate": "La date de naissance n'est pas valide, entrez une date correcte (au format jj/mm/aaaa).",
        "discriminator": "Le discriminant du joueur doit être un nombre positif. Entrez un entier positif.",
        "match_number": "Le numéro du match doit être un nombre. Entrez un entier positif.",
        "max_round": "Le nombre de rondes doit être un nombre. Entrez un entier positif.",
        "new_ranking": "Le nouveau classement du joueur doit être un nombre. Entrez un entier positif.",
        "participant_amount": "Le nombre de participants doit être un nombre. Entrez un entier positif.",
        "ranking": "Le classement d'un joueur doit être un nombre. Entrez un entier positif.",
        "result": "Le résultat du match n'est pas valide. Entrez un résultat valide (1-0, 0-1 ou 1/2-1/2).",
        "tournament_date": "La date du tournoi n'est pas valide, entrez une date correcte (au format jj/mm/aaaa avec "
                           "des espaces entre chaque date s'il y en a plusieurs.",
        "tournament_type": "Le contrôle de temps du tournoi ne fait pas partie des noms autorisés. "
                           "Indiquez un nom valide."
    },
    "welcome": "Bienvenue dans le logiciel de gestion de tournois d'échecs.",
    "main_ask": "Que voulez-vous faire?",
    "controller": {
        "tournament_already_exists": "Un tournoi avec le même nom, la même date et le même lieu existe déjà dans la "
                                     "base de données. Le tournoi n'a pas été créé.",
        "unknown_argument": lambda argument: f"Un argument non requis était présent, il a été ignoré: {argument}",
        "no_member": "Il n'y a pas de membres à afficher!",
        "existing_members": lambda number: f"Il y a {number} personne(s) avec ce nom dans la base de données: \n",
        "player_number": "Indiquez le numéro du joueur que vous voulez choisir",
        "not_a_number": "Vous n'avez pas indiqué un nombre. L'opération est annulée.",
        "not_a_valid_number": "Vous avez indiqué un nombre non-valide. L'opération est annulée.",
        "no_member_in_DB": "Il n'y a personne avec ce nom dans la base de données!",
        "can't_sort": lambda key: f"Il est impossible de trier selon {key}.",
        "odd_number": "Vous ne pouvez pas avoir un nombre impair de joueurs. Le tournoi n'a pas été créé.",
        "created_tournament": "Tournoi créé!\nVous êtes désormais dans la gestion de ce nouveau tournoi.",
        "member_added": "La personne a été correctement ajoutée à la base de données!",
        "ranking_changed": "Le classement du joueur a été correctement changé!",
        "can't_charge_tournament": "Un ou plusieurs membres ne peuvent pas être trouvés. Le tournoi n'a pas pu être "
                                   "chargé.",
        "tournament_loaded": "Tournoi chargé!\nVous êtes désormais dans la gestion de ce tournoi",
        "can't_charge_tournament_critical": lambda problem: f"Le tournoi {problem} n'a pas pu être chargé. L'opération"
                                                            f" a donc été annulée. Il est nécessaire de supprimer ce "
                                                            f"tournoi ou de recréer entièrement la base de données",
        "no_tournament": "Il n'y a pas de tournois à afficher!",
        "member_already_exist": "Cette personne semble déjà exister dans la base de données. Êtes-vous sûr de vouloir "
                                "la rajouter malgré tout? (o/n)",
        "added_but_exist": lambda number: f"Cette personne a bien été ajoutée. Pour la distinguer des personnes "
                                          f"similaires, un discriminant ({number}) a été ajouté. Assurez-vous de vous "
                                          f"en souvenir pour distinguer les personnes!",
        "invalid_member_answer": "Votre réponse n'est pas valide. La personne n'a pas été ajoutée à la base de "
                                 "données",
        "not_added": "La personne n'a pas été ajoutée à la base de données.",
        "no_tournament_in_DB": "Il n'y a pas de tournoi avec ce nom dans la base de données!",
        "existing_tournaments": lambda number: f"Il y a {number} tournoi(s) avec ce nom dans la base de données:",
        "tournament_number": "Indiquez le numéro du tournoi que vous voulez charger.",
        "ending": "Le gestionnaire de tournois va s'éteindre!",
        "players_not_created": "Les joueurs n'ont pas encore été créés!",
        "no_participants": "Il n'y a pas encore de participants!",
        "no_rounds": "Il n'y a pas encore de rondes créées dans ce tournoi!",
        "no_games": "Il n'y a pas de parties dans ce tournoi!",
        "tournament_started": "Le tournoi a déjà commencé!",
        "enough_participants": "Il y a déjà assez de participants!",
        "already_in_tournament": lambda name, surname: f"{name} {surname} est déjà dans le tournoi.",
        "has_been_added": lambda name, surname: f"{name} {surname} a bien été ajouté au tournoi en cours.",
        "not_in_tournament": lambda name, surname, number: f"{name} {surname} {number} n'est pas dans le tournoi.",
        "has_been_removed": lambda name, surname: f"{name} {surname} a bien été enlevé du tournoi en cours",
        "doesn't_exist": "Ce joueur n'existe pas!",
        "informations": "Voilà les informations du joueur",
        "not_enough_players": "Il n'y a pas assez de joueurs.",
        "tournament_launched": "Le tournoi est lancé.",
        "round_not_finished": "La ronde précédente n'a pas été terminée.",
        "all_rounds_played": "Toutes les rondes prévues ont déjà été jouées!",
        "tournament_not_started": "Le tournoi n'est pas encore lancé!",
        "round_created": "La prochaine ronde a été créée!",
        "game_not_finished": lambda name: f"Le match {name} n'est pas fini.",
        "round_already_finished": "La ronde est déjà finie.",
        "round_finished": "La ronde actuelle a bien été finie.",
        "game_doesn't_exist": "Ce match n'existe pas.",
        "game_already_has_score": "Le résultat du match a déjà été entré.",
        "validation_result": lambda name, result: f"Le résultat de {name} va être {result}. Il ne pourra plus être "
                                                  f"changé après. Êtes-vous sûr de vouloir valider? (o/n)",
        "result_ok": "Le résultat a été validé!",
        "invalid_result_answer": "Votre réponse n'était pas valide. Le résultat n'a pas été validé.",
        "result_not_ok": "Le résultat n'a pas été validé.",
        "tournament_not_finished": "Le tournoi n'est pas fini! Il reste une ou plusieurs rondes à jouer ou "
                                   "à terminer.",
        "back_main_menu": "Retour au menu principal!"
    },
    "headers": {
        "member_choice": "nom   prénom   date de naissance   genre   classement   discriminant",
        "tournament_display": "nom   lieu   date(s)   type de tournoi   description",
        "player_display": "nom complet   points",
        "rounds_display": "nom   heure de début   heure de fin",
        "games_display": "nom de la partie   score",
        "result": "place   nom complet   points"
    },
    "invalid_command_argument": "La fonction n'est pas un appel valide, ou un des arguments n'existe pas.  "
                                "Lisez le readme pour obtenir plus d'informations.",
    "invalid_command": "La fonction n'est pas un appel valide."
                       "Lisez le readme pour obtenir plus d'informations."
}
