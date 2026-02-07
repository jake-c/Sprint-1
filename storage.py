#storage.py
#responsible for saving and loading game state to/from a text file.

class GameStorage:
    def save(self, filename, board, next_number, score):
        #save current game state into a text file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"next={next_number}\n")
            f.write(f"score={score}\n")
            for row in board:
                f.write(" ".join(str(x) for x in row) + "\n")

    def load(self, filename, size=5):
        #load a saved game state from a text file
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        #basic validation of save file structure
        if len(lines) < 2 + size:
            raise ValueError("Save file is missing data.")

        if not lines[0].startswith("next=") or not lines[1].startswith("score="):
            raise ValueError("Save file header is invalid.")

        #parse metadata
        next_number = int(lines[0].split("=", 1)[1])
        score = int(lines[1].split("=", 1)[1])

        #parse board contents
        board = []
        for i in range(size):
            parts = lines[2 + i].split()
            if len(parts) != size:
                raise ValueError("Board row has wrong number of columns.")
            board.append([int(x) for x in parts])

        return board, next_number, score
            
    # User Story 7: log completed games
    def log_completed_game(self, name, level, score, board, filename="completed_games.log"):
        from datetime import datetime

        with open(filename, "a", encoding="utf-8") as f:
            f.write("=== Completed Game ===\n")
            f.write(f"Player: {name}\n")
            f.write(f"Date/Time: {datetime.now()}\n")
            f.write(f"Level: {level}\n")
            f.write(f"Score: {score}\n")
            f.write("Board:\n")
            for row in board:
                f.write(" ".join(str(x) for x in row) + "\n")
            f.write("\n")

        

