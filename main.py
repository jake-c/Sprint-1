# main.py
# ============================================================
# ORIGINAL PURPOSE:
# - Ask user for a timer duration using a Tkinter popup
# - Start Level 1 UI (GameUILevel1)
#
# AUTH CHANGE (User Story: Admin authentication / registered players):
# - New players MUST register before they can play.
# - Returning players MUST login before they can play.
# - Only after successful login do we proceed to the timer prompt + game start.
# ============================================================

import tkinter as tk
from tkinter import simpledialog

from ui_level1 import GameUILevel1

# =========================
# AUTH CHANGE START
# =========================
# We import UserAuth from storage.py (the class we added there).
# This handles:
# - register(username, password)
# - authenticate(username, password)
from storage import UserAuth


def auth_gate_tk():
    """
    Tkinter-based login/register gate.

    Returns:
        username (str) if login succeeds
        None if user cancels/closes the dialogs

    Why Tk dialogs?
    - Your project is already using Tkinter dialogs for timer setup,
      so using dialogs for login/register keeps the UX consistent.
    """

    auth = UserAuth("users.json")

    # Create a hidden root for dialogs (like you already do).
    root = tk.Tk()
    root.withdraw()

    while True:
        # Ask whether they want to login or register.
        # They must choose one to proceed.
        choice = simpledialog.askstring(
            "Authentication Required",
            "Welcome!\n\nType one of the following:\n"
            "  login   -> if you already have an account\n"
            "  register-> if you are a new player\n\n"
            "Cancel to exit."
        )

        if choice is None:
            # User cancelled the popup: exit
            root.destroy()
            return None

        choice = choice.strip().lower()

        if choice not in ("login", "register"):
            # Loop again until they type a valid option
            continue

        # Ask for username + password
        username = simpledialog.askstring("Username", "Enter your username:")
        if username is None:
            root.destroy()
            return None

        # NOTE: Tkinter simpledialog does not mask input like a password field.
        # This is fine for a class project offline requirement.
        password = simpledialog.askstring("Password", "Enter your password:")
        if password is None:
            root.destroy()
            return None

        username = username.strip()

        if choice == "register":
            ok, msg = auth.register(username, password)
            # Show result message
            simpledialog.messagebox.showinfo("Register", msg) if hasattr(simpledialog, "messagebox") else None
            # If register succeeds, we can immediately allow play (logged in)
            if ok:
                root.destroy()
                return username

        elif choice == "login":
            ok, msg = auth.authenticate(username, password)
            # Show result message
            simpledialog.messagebox.showinfo("Login", msg) if hasattr(simpledialog, "messagebox") else None
            if ok:
                root.destroy()
                return username

        # If we reach here, login/register failed, so loop again.


# =========================
# AUTH CHANGE END
# =========================


if __name__ == "__main__":
    # ============================================================
    # AUTH CHANGE:
    # - Must authenticate BEFORE playing (before timer setup and before launching UI).
    # ============================================================
    logged_in_user = auth_gate_tk()
    if logged_in_user is None:
        # User cancelled authentication
        raise SystemExit(0)

    # ============================================================
    # ORIGINAL CODE BELOW (Timer popup) — kept in place.
    # ============================================================
    temp_root = tk.Tk()
    temp_root.withdraw()

    # Timer window for the user to enter time
    user_time_str = simpledialog.askstring(
        "Timer Setup",
        "Enter timer duration in seconds for all levels:\n(Leave blank or cancel for default 60s)"
    )

    # Default time limit is 60
    if user_time_str is None or user_time_str.strip() == "":
        time_limit = 60
    else:
        try:
            # Try to convert user typed text into a number
            time_limit = int(user_time_str)

            if time_limit < 5:
                time_limit = 5
        except ValueError:
            # If they user letters like "abc", default to 60
            time_limit = 60

    temp_root.destroy()

    # ============================================================
    # AUTH CHANGE:
    # - We pass player_name into Level 1 UI so the game can "recognize" the player.
    # - If your GameUILevel1 __init__ does NOT accept player_name yet,
    #   you must add it there (I can do that next if you paste ui_level1.py).
    # ============================================================
    GameUILevel1(time_limit=time_limit, player_name=logged_in_user).start()