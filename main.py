import controller
import view
import translate

WELCOME_TEXT = translate.data["welcome"]
ASK_TEXT = translate.data["main_ask"]


def main():
    current_view = view.View()
    current_view.display(WELCOME_TEXT)
    main_controller = current_controller = controller.GlobalController(current_view)
    running = True
    while running:
        command, kwargs = current_view.ask_command(ASK_TEXT)
        result = current_controller.execute_command(command, kwargs)
        if type(result) == controller.TournamentController:
            current_controller = result
        elif result == "exit":
            current_controller = main_controller
        elif result == "close":
            running = False
        current_view.display("")  # No need for \n since the print will already create a line.
        pass


if __name__ == "__main__":
    main()
