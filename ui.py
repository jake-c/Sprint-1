#ui.py
#handles all user interaction and display logic.
#No game rules or file logic should be here.

class GameUI:
    def print_board(self, board, score, next_number):
        #display the board, score, and next number
        print("\n" + "=" * 30)
        print(f"Score: {score} | Next number: {next_number}")
        print("=" * 30)

        header = "     " + " ".join([f"{i+1:>3}" for i in range(len(board))])
        print(header)
        for r, row in enumerate(board):
            row_str = " ".join([f"{v:>3}" if v != 0 else "  ." for v in row])
            print(f"{r+1:>3}  {row_str}")
        print()

    def print_menu(self):
        #show main menu options
        print("Menu:")
        print("1) Place next number")
        print("2) Save game")
        print("3) Load game")
        print("4) Quit")

    def ask_choice(self):
        #ask user for a menu selection
        return input("Choose an option (1-4): ").strip()

    def ask_position(self):
        #ask user for row and column input
        raw = input("Enter row col (1-5 1-5): ").strip()
        parts = raw.split()
        if len(parts) != 2:
            return None
        try:
            return int(parts[0]) - 1, int(parts[1]) - 1
        except ValueError:
            return None

    def ask_filename(self, default_name="save.txt"):
        #ask user for a filename, allowing default
        raw = input(f"Filename (Enter for '{default_name}'): ").strip()
        return raw if raw else default_name

    def show_message(self, msg):
        #display a status message
        print(msg)

