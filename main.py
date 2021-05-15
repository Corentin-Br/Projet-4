import controller
import view


def main():
    current_view = view.View()
    current_view.display("Bienvenue dans le logiciel de gestion de tournois d'échecs")
    main_controller = current_controller = controller.GlobalController(current_view)
    while True:
        command, kwargs = current_view.ask_command("Que voulez-vous faire?")
        result = current_controller.execute_command(command, kwargs)
        if type(result) == controller.TournamentController:
            current_controller = result
        elif result == "exit":
            current_controller = main_controller
        current_view.display("")  # No need for \n since the print will already create a line.
        pass


if __name__ == "__main__":
    main()
