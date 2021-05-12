import controller
import view


def main():
    current_view = view.View()
    current_view.display("Bienvenue dans le logiciel de gestion de tournois d'échecs")
    main_controller = current_controller = controller.GlobalController(current_view)
    while True:
        command, args, kwargs = current_view.ask("Que voulez-vous faire?")
        result = current_controller.does(command, args, kwargs)
        if type(result) == controller.TournamentController:
            current_controller = result
        elif result == "exit":
            current_controller = main_controller
        pass
