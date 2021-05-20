import controllers
import views
from models.core import TRANSLATION

WELCOME_TEXT = TRANSLATION["welcome"]
ASK_TEXT = TRANSLATION["main_ask"]
INVALID_COMMAND_ERROR = TRANSLATION["invalid_command"]


def main():
    current_view = views.View()
    current_view.display(WELCOME_TEXT)
    main_controller = current_controller = controllers.GlobalController(current_view)
    running = True
    while running:
        try:
            command, kwargs = current_view.ask_command(ASK_TEXT)
        except KeyError:
            current_view.display(INVALID_COMMAND_ERROR)
        else:
            result = getattr(current_controller, command)(**kwargs)
            if type(result) == controllers.TournamentController:
                current_controller = result
            elif result == "exit":
                current_controller = main_controller
            elif result == "close":
                running = False
        current_view.display("")  # No need for \n since the print will already create a line.
        pass


if __name__ == "__main__":
    main()
