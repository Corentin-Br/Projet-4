# Chess tournament management

This program helps managing chess tournament, allowing to add club members in a data base, create a tournament with these membres, inputing the result of matches to automatically generate rounds...

## Setup and execution:

This program can be executed offline and can be installed following these steps:

### Setup
1. Clone the repository using`$git clone https://github.com/Corentin-Br/Projet-4.git` or downloading [the zip file](https://github.com/Corentin-Br/Projet-4/archive/refs/heads/master.zip).
2. Create the virtual environment with `$ py -m venv env` on windows or `$ python3 -m venv env` on macos or linux.
3. Activate the virtuel environment with `$ env\Scripts\activate` on windows or `$ source env/bin/activate` on macos or linux.
4. Install the dependencies with `$ pip install -r requirements.txt` .

### Execution
1. If that's not already the case, activate the virtual environment as you did during the setup.
2. Get in the folder chess with `$ cd chess`
3. Launch the program with `$ python __main__.py`

#### Use
Once the program is launched in the terminal, it starts interacting with you by asking you what you want to do. Note that the program uses a french interface. If you wish to change that, you'll need to modify translate.py.

To interact with the program, you must provide it with commands with the syntax: ```command_name --argument_name argument value --other_argument value of the other argument```.

Note that any amount of argument may be given, the program will automatically ask missing arguments and remove unneeded arguments.

Some arguments are optional (if they are given they will be used, if they aren't, the program won't ask them).

Some commands may ask further informations.

## Translation:
In chess/models/translate.py are all translations used by the script. Editing the file allows to make all the interface behave differently: It will accept different names for the commands and arguments, and will display different messages.

## Interaction with the database:
chess/models/db.json is the database (if it doesn't exist, it will automatically be created when needed), saving the state of tournaments and members.

It's not possible to edit arbitrarily the database from inside the program. For example editing the birthdate (because it was mistyped) is not directly possible.

Editing the database manually is, of course, possible. However members should **never** be removed from the database. Their identifiant is used when saving tournaments, and it will lead to abnormal behaviour (wrong players being displayed, or tournament not loading) if they are deleted.
