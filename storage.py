# storage.py
# responsible for saving and loading game state to/from a text file.

class GameStorage:
    def save(self, filename, board, next_number, score):
        # save current game state into a text file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"next={next_number}\n")
            f.write(f"score={score}\n")
            for row in board:
                f.write(" ".join(str(x) for x in row) + "\n")

    def load(self, filename, size=5):
        # load a saved game state from a text file
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        # basic validation of save file structure
        if len(lines) < 2 + size:
            raise ValueError("Save file is missing data.")

        if not lines[0].startswith("next=") or not lines[1].startswith("score="):
            raise ValueError("Save file header is invalid.")

        # parse metadata
        next_number = int(lines[0].split("=", 1)[1])
        score = int(lines[1].split("=", 1)[1])

        # parse board contents
        board = []
        for i in range(size):
            parts = lines[2 + i].split()
            if len(parts) != size:
                raise ValueError("Board row has wrong number of columns.")
            board.append([int(x) for x in parts])

        return board, next_number, score

    # log completed games
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

# The following is the part for authentication (storing data in users.json)

import os
import json
import hashlib

class UserAuth:
    def __init__(self, filename="users.json"):
        # filename where registered users are stored
        self.filename = filename
        # load existing users
        self._data = self._load()

    # internal helpers
    def _load(self):
        # Load users.json
        if not os.path.exists(self.filename):
            return {"users": {}}

        with open(self.filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # if someone edited the JSON or it broke, reset it
                return {"users": {}}    

    # Write the current in-memory users data back to users.json.
    def _save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    # Password hashing
    def _hash_password(self, password, salt):
        return hashlib.sha256((salt + password).encode()).hexdigest()
    
    # Checks if username already exists in users.json
    def is_registered(self, username):
        return username in self._data["users"]

    # Register a new player
    def register(self, username, password):
        username = username.strip()

        # Validating the player
        if not username:
            return False, "Username cannot be empty."
        if " " in username:
            return False, "Username cannot contain spaces."
        if len(password) < 4:
            return False, "Password must be at least 4 characters."
        if self.is_registered(username):
            return False, "Username already exists. Please login instead."

        
        salt = os.urandom(16).hex()
        hashed = self._hash_password(password, salt)
        self._data["users"][username] = {"salt": salt, "hash": hashed}
        self._save()
        return True, "Registered successfully."

    # Authenticate a player that exists
    def authenticate(self, username, password):
        username = username.strip()

        user = self._data["users"].get(username)
        if not user:
            return False, "User not found. Please register first."

        hashed = self._hash_password(password, user["salt"])
        if hashed == user["hash"]:
            return True, "Login successful."

        return False, "Incorrect password."
