import tkinter as tk
from tkinter import simpledialog, messagebox

from ui_level1 import GameUILevel1

# Import UserAuth from storage.py for authentication and registration
from storage import UserAuth


def auth_gate_tk():

    auth = UserAuth("users.json")

    # Create a root for dialogs
    root = tk.Tk()
    root.withdraw()

    while True:
        # Asking the user whether they want to login or register
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
            # Loop again until they enter a valid option
            continue

        # Ask for username + password
        username = simpledialog.askstring("Username", "Enter your username:")
        if username is None:
            root.destroy()
            return None

        # Password processing
        password = simpledialog.askstring("Password", "Enter your password:")
        if password is None:
            root.destroy()
            return None

        username = username.strip()

        if choice == "register":
            ok, msg = auth.register(username, password)
            # Show result message
            messagebox.showinfo("Register", msg)
            # If register succeeds, we can allow the user to play
            if ok:
                root.destroy()
                return username

        elif choice == "login":
            ok, msg = auth.authenticate(username, password)
            # Show result message
            messagebox.showinfo("Login", msg)
            if ok:
                root.destroy()
                return username

        # If we reach here, login/register failed, so loop again.

if __name__ == "__main__":
    # User must login
    logged_in_user = auth_gate_tk()
    if logged_in_user is None:
        raise SystemExit(0)

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

    GameUILevel1(time_limit=time_limit, player_name=logged_in_user).start()