# Programme de gestion de tournois d'échecs

Ce programme aide à la gestion de tournois d'échecs, en permettant l'ajout de membres du club dans une base de données, de créer un tournoi à partir de ces membres, en entrant les résultats des matchs pour automatiser la création des tours...

## Installation et exécution

Ce programme est exécutable sans connexion et peut être installé en suivant ces étapes:

### Installation
1. Cloner le dépôt en utilisant `$git clone https://github.com/Corentin-Br/Projet-4.git` ou en téléchargeant [le fichier zip](https://github.com/Corentin-Br/Projet-4/archive/refs/heads/master.zip).
2. Créer un environnement virtuel avec `$ py -m venv env` sur windows ou `$ python3 -m venv env` sur macos ou linux.
3. Activer l'environnement virtuel avec `$ env\Scripts\activate` sur windows ou `$ source env/bin/activate` sur macos ou linux.
4. Installer les dépendences avec `$ pip install -r requirements.txt` .

### Exécution
1. Si ce n'est pas déjà le cas, activer l'environnement virtuel comme lors de l'installation.
2. Placez-vous dans le dossier chess, avec `$ cd chess`
3. Exécutez le programme avec `$ python __main__.py`

#### Utilisation:
Une fois que le programme est exécuté dans le terminal, il commence à interagir avec vous en vous demandant quelle action vous souhaitez exécuter.

Ces actions doivent suivre la syntaxe```nom_de_commande --nom_d_argument valeur de l'argument --autre_argument valeur de l'autre argument```.

De plus, certaines de ces actions peuvent vous demander des informations supplémentaires.

Si certains arguments sont manquants lors de l'appel, ils vous seront demandés.

Si la valeur de certains arguments est incorrecte, ils vous seront redemandés jusqu'à ce qu'une valeur valide soit présente.

Si certains arguments que vous avez donnés ne sont pas requis par la commande, ils seront explicitement ignorés.

Certains arguments sont optionnels (et seront mis en parenthèse ci-dessous). S'ils sont fournis, la fonction les utilisera, sinon ils ne seront pas demandés.

Les arguments peuvent être donnés dans n'importe quel ordre.

Les actions sont automatiquement sauvegardées par le programme. Il n'y a donc pas besoin (ni possibilité) de sauvegarder manuellement.


Liste des commandes valides:
##### Menu Principal
`afficher_acteurs (--clé)`
Affiche tous les membres présents dans la base de donnée.

Si clé est fournie et que c'est un attribut valide, les membres seront triés selon cet attribut.

`afficher_tournois`
Affiche tous les tournois qui sont dans la base de données.

`créer_tournoi --nom_tournoi --lieu, --date, --nombre_de_rondes --nombre_de_participants --type_de_tournoi (--description)
Crée un tournoi avec les informations requises.

Le nombre de participants doit être pair.

/!\ Une fois le tournoi créé, vous serez déplacé dans la gestion de tournoi, et n'aurez plus accès à certaines fonctions.

`ajouter_acteur --prénom --nom --date_de_naissance --genre --classement
Ajoute un membre à la base de données.

`changer_classement --prénom --nom --classement`
Remplace le classement d'un joueur avec le nom et prénom par le classement fourni.

S'il y a plusieurs personnes avec ce nom et prénom, une désambiguation sera demandée.

S'il n'y a personne avec ce nom et prénom, l'action sera annulée.

`charger_tournoi --nom_du_tournoi`
Charge le tournoi avec le nom donné.

Si plusieurs tournois ont le même nom, une désambiguation sera demandée.

S'il n'y a aucune tournoi avec ce nom, l'action sera annulée.

/!\ Une fois le tournoi chargé, vous serez déplacé dans la gestion de tournoi, et n'aurez plus accès à certaines fonctions.

`fermer`
Ferme le programme.

##### Gestion de tournoi
/!\ Lors du lancement du programme, vous serez dans le menu principal. Il faut créer ou charger un tournoi pour accéder à certaines de ces fonctions.

`afficher_acteurs (--clé)`
Affiche tous les membres présents dans la base de donnée.

Si clé est fournie et que c'est un attribut valide, les membres seront triés selon cet attribut.

`afficher_participants (--clé)`
Affiche tous les membres participant au tournoi.

Si clé est fournie et que c'est un attribut valide, les membres seront triés selon cet attribut.

`afficher_joueurs (--clé)`
Affiche tous les joueurs participant au tournoi.

Si clé est fournie et que c'est un attribut valide, les joueurs seront triés selon cet attribut.

/!\ afficher_participants et afficher_joueurs sont similaires. Si vous souhaitez trier selon des informations personnelles (nom, prénom....), utilisez afficher_participants. Si vous souhaitez trier selon des informations du tournoi en cours (points...), utilisez afficher_joueurs.

`afficher_tours`
Affiche toutes les rondes déjà créées du tournoi.

`afficher_matchs`
Affiche tous les matchs de toutes les rondes déjà créées du tournoi.

`afficher_tour_actuel`
Affiche tous les matchs de la ronde actuelle.

`ajouter_participant  --prénom --nom`
Ajoute le membre avec ce nom et ce prénom en tant que participant au tournoi.

S'il y a plusieurs personnes avec ce nom et prénom dans la base de données, une désambiguation sera demandée.
Si la personne est déjà dans le tournoi, l'action sera annulée.

`enlever_participant --prénom --nom`
Enlève le membre avec ce nom et ce prénom des participants au tournoi.

S'il y a plusieurs personnes avec ce nom et prénom dans la base de données, une désambiguation sera demandée.
Si la personne n'est pas dans le tournoi, l'action sera annulée.

`détails --prénom --nom --discriminant`
Obtient les informations d'un membre (genre, date de naissance, classement...) pour pouvoir lever toute ambiguité.
Si personne n'a ce nom, prénom et discriminant, l'action sera annulée.

`commencer`
Lance le tournoi.

Si le tournoi est déjà lancé ou s'il n'a pas assez de participants, l'action sera annulée.

`tour_suivant`
Crée la ronde suivante, et affiche les matchs de celle-ci.

S'il existe une ronde précédente et qu'elle n'est pas terminée, l'action sera annulée.

Si toutes les rondes du tournoi ont déjà été joué, l'action sera aussi annulée.

`finir_tour`
Finis la ronde en cours.

Si les scores de certains matchs n'ont pas été entrés, l'action sera annulée.

`résultat --numéro_du_match --résultat`
Affecte le résultat donné au match choisi et attribue les points aux joueurs. Les matchs sont numérotés à partir de 1 en partant du match affiché le plus haut lors de la création du tour. Utilisez `afficher_tour_actuel` pour obtenir les numéros des matchs explicitement en cas de doute.

/!\ Une fois un résultat donné, il ne peut plus être changé.

`exit`
Quitte la gestion de tournoi et retourne au menu principal.


## Génération du rapport flake8

### Installation
1. Installer flake8 avec la commande `$ python -m pip install flake8`

En cas de difficultés, consulter https://flake8.pycqa.org/en/latest/index.html
2. Installer flake8-html avec la commande `$ pip install flake8-html`

En cas de difficultés, consulter https://pypi.org/project/flake8-html/

### Exécution
1. Placez-vous dans le dossier chess, avec `$ cd chess`
2. Exécutez flake8 avec la commande suivante: `$ flake8 --format=html --htmldir=flake-report --max-line-length 119`

Un dossier flake-report est créé, contenant un fichier index.html, ouvrir ce fichier permettra de visualiser s'il y a des erreurs et où elles sont s'il y en a.