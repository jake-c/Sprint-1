#main.py
#Entry point of the application.
#cordinates UI, game logic, and storage.

from ui import GameUI
from logic import GameLogic
from storage import GameStorage


def new_board(size=5):
#    Create an empty game board
    return [[0 for _ in range(size)] for _ in range(size)]


def board_is_full(board):
    # Check if the board has no empty cells
    return all(cell != 0 for row in board for cell in row)


def main():
    #initialize components
    ui = GameUI()
    logic = GameLogic(size=5)
    storage = GameStorage()

    #Initial game state
    board = new_board(5)
    next_number = 1
    score = 0
    game_over = False

    #main game loop
    while True:
        ui.print_board(board, score, next_number)

        if game_over:
            ui.show_message("Game ended due to an invalid placement.")
        elif board_is_full(board):
            ui.show_message("Board is full. Game complete!")

        ui.print_menu()
        choice = ui.ask_choice()

        if choice == "1":
            if game_over or board_is_full(board):
                ui.show_message("You can't place a number right now.")
                continue

            pos = ui.ask_position()
            if pos is None:
                ui.show_message("Invalid input format. Game over.")
                game_over = True
                continue

            r, c = pos
            ok, points, msg = logic.place_number(board, next_number, r, c)
            ui.show_message(msg)

            if not ok:
                game_over = True
                continue

            score += points
            next_number += 1

        elif choice == "2":
            filename = ui.ask_filename("save.txt")
            storage.save(filename, board, next_number, score)
            ui.show_message("Game saved.")

        elif choice == "3":
            filename = ui.ask_filename("sample_save.txt")
            board, next_number, score = storage.load(filename)
            game_over = False
            ui.show_message("Game loaded.")

        elif choice == "4":
            ui.show_message("Goodbye.")
            break

        else:
            ui.show_message("Invalid menu choice.")


if __name__ == "__main__":
    main()

