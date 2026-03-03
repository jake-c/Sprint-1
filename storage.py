# storage.py
# responsible for saving and loading game state to/from a text file.
#
# NOTE:
# - Everything in GameStorage below is YOUR original code (unchanged),
#   except for minor formatting of comments.
# - The ONLY addition for the new user story is the UserAuth class at the bottom.
#   It's clearly marked with big START/END blocks.

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


# ======================================================================
# AUTH CHANGE START (User Story: Admin authentication / registered players)
# ======================================================================
# Goal:
# - New players must REGISTER before they can play the game the first time.
# - Returning players must LOGIN (authenticate) to play.
#
# Where data is stored:
# - users.json file in the same folder as your game.
#
# Security note (for class project):
# - We DO NOT store plaintext passwords.
# - We store a salted PBKDF2 hash.
#
# How you will use this:
# - In main.py, show menu: Login / Register
# - Call auth.register(username, password) or auth.authenticate(username, password)
# - Only launch the game UI if login succeeds.
# ======================================================================

import os
import json
import base64
import hashlib
import hmac


class UserAuth:
    """
    Local registration + authentication system (offline).

    It stores users in a JSON file in this format:
    {
      "users": {
        "jake": { "salt": "...", "hash": "..." },
        ...
      }
    }
    """

    def __init__(self, filename="users.json"):
        # filename where registered users are stored
        self.filename = filename
        # load existing users immediately
        self._data = self._load()

    # ---------------- internal helpers ----------------

    def _load(self):
        """
        Load users.json.
        If file doesn't exist, create an empty structure in memory.
        If file is corrupt, reset to empty (simple + safe for class project).
        """
        if not os.path.exists(self.filename):
            return {"users": {}}

        with open(self.filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # If someone edited the JSON or it broke, reset it.
                data = {"users": {}}

        # Ensure the structure we expect
        if "users" not in data or not isinstance(data["users"], dict):
            data = {"users": {}}

        return data

    def _save(self):
        """
        Write the current in-memory users data back to users.json.
        """
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def _hash_password(self, password: str, salt: bytes) -> bytes:
        """
        PBKDF2-HMAC-SHA256 password hashing.
        - password: plaintext password entered by user (never stored)
        - salt: random bytes stored for each user
        Returns derived key bytes (hash).
        """
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            120_000  # iterations (reasonable for a class project)
        )

    # ---------------- public API you call from main.py ----------------

    def is_registered(self, username: str) -> bool:
        """
        Returns True if username already exists in users.json.
        """
        return username in self._data["users"]

    def register(self, username: str, password: str):
        """
        Register a NEW player.
        Returns (success_bool, message_string).
        """
        username = username.strip()

        # Basic validation
        if not username:
            return False, "Username cannot be empty."
        if any(ch.isspace() for ch in username):
            return False, "Username cannot contain spaces."
        if len(password) < 4:
            return False, "Password must be at least 4 characters."
        if self.is_registered(username):
            return False, "Username already exists. Please login instead."

        # Create salted hash
        salt = os.urandom(16)
        pwd_hash = self._hash_password(password, salt)

        # Store base64 strings (JSON-friendly)
        self._data["users"][username] = {
            "salt": base64.b64encode(salt).decode("utf-8"),
            "hash": base64.b64encode(pwd_hash).decode("utf-8"),
        }

        # Persist to disk
        self._save()
        return True, "Registered successfully."

    def authenticate(self, username: str, password: str):
        """
        Authenticate an EXISTING player (login).
        Returns (success_bool, message_string).
        """
        username = username.strip()

        user = self._data["users"].get(username)
        if not user:
            return False, "User not found. Please register first."

        # Decode stored values
        salt = base64.b64decode(user["salt"])
        expected_hash = base64.b64decode(user["hash"])

        # Hash the attempted password using the same salt
        attempt_hash = self._hash_password(password, salt)

        # Constant-time compare (prevents timing attacks; good habit)
        if hmac.compare_digest(attempt_hash, expected_hash):
            return True, "Login successful."

        return False, "Incorrect password."

# ======================================================================
# AUTH CHANGE END
# ======================================================================

