# Chess tournament management

## Setup:

Create a virtual environment and install the dependencies found in requirements.txt .

## Use:
Execute the __main__.py file in the chess folder through the terminal.

The program will ask you what you want to do. You must provide a command name followed by any number of named arguments, following the syntax: ```command_name --argument_name full argument value --other_argument_name value of other argument name```
The name of the command and all argument names will be translated in english to be used by the script and executed.
All missing arguments required to execute the command will be asked consequently. All excess arguments that are not required will be explicitly mentioned and ignored. If an argument is invalid, a new value for it will be asked until a valid value is given.
All arguments can be given in any order.
i.e, for the command above:
```command_name```
```command_name --argument_name full argument value```
```command_name --other_argument_name value of other argument name --argument_name full argument value```
all are valid calls for the same command, though some of them call will ask additional inputs from the user.




## Translation:
In chess/models/fr.json are all translations used by the script. Editing the file allows to make all the interface behave differently: It will accept different names for the commands and arguments, and will display different messages.
While it allows for a translation in other languages, it may also break the script if edited carelessly.

## Interaction with the database:
chess/models/db.json will be the database, saving the state of tournaments and members.
It's not possible to edit arbitrarily the database from inside the program. For example editing the birthdate (because it was mistyped) is not directly possible.
Editing the database manually is, of course, possible. However members should **never** be removed from the database. Their identifiant is used when saving tournaments, and it will lead to abnormal behaviour (wrong players being displayed, or tournament not loading).
