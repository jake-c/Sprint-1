# ui.py
# Handles all user interaction and display logic.
# No game rules or file logic should be here.

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import platform
from logic import GameLogic
from storage import GameStorage
import os

# This function plays sounds according to the OS used
def play_sound(success):
    system_name = platform.system()

    if system_name == "Windows":
        try:
            import winsound
            winsound.Beep(700 if success else 200, 200 if success else 400)
        except ImportError:
            pass
    elif system_name == "Darwin":
        os.system(
            "afplay /System/Library/Sounds/Glass.aiff &"
            if success
            else "afplay /System/Library/Sounds/Basso.aiff &"
        )
    elif system_name == "Linux":
        print('\a')


class GameUI:
    def __init__(self, size=5):
        self.size = size
        self.logic = GameLogic(size=size)
        self.game_storage = GameStorage()

        # ---- Game state ----
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.next_number = 1
        self.score = 0
        self.game_over = False
        self.level = 1
        self.one_pos = None

        # ---- Color palette (light theme) ----
        self.bg_main = "#f7f8fa"
        self.bg_tile_empty = "#ffffff"
        self.bg_tile_filled = "#e8f0fe"
        self.bg_hover = "#dde7f5"
        self.text_primary = "#1f2933"

        # ---- Window ----
        self.root = tk.Tk()
        self.root.title("Number Placement Game – Level 1")
        self.root.resizable(False, False)
        self.root.configure(bg=self.bg_main)

        # ---- Top info bar ----
        self.info_frame = tk.Frame(self.root, bg=self.bg_main)
        self.info_frame.pack(pady=12)

        self.score_label = tk.Label(
            self.info_frame,
            text="Score: 0",
            font=("Helvetica", 14, "bold"),
            fg=self.text_primary,
            bg=self.bg_main
        )
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.level_label = tk.Label(
            self.info_frame,
            text="Level: 1",
            font=("Helvetica", 14),
            fg=self.text_primary,
            bg=self.bg_main
        )
        self.level_label.pack(side=tk.LEFT, padx=20)

        self.next_label = tk.Label(
            self.info_frame,
            text="Next: 1",
            font=("Helvetica", 14, "bold"),
            fg="blue",
            bg=self.bg_main
        )
        self.next_label.pack(side=tk.LEFT, padx=20)

        # ---- Board ----
        self.board_frame = tk.Frame(self.root, bg=self.bg_main)
        self.board_frame.pack(padx=16, pady=10)

        self.buttons = []
        self.draw_board()

        # ---- Place first number randomly ----
        r = random.randint(0, size - 1)
        c = random.randint(0, size - 1)
        self.board[r][c] = 1
        self.logic.turns.append((r, c))
        self.next_number = 2
        self.one_pos = (r, c)

        self.refresh_board()

        # ---- Bottom controls ----
        self.control_frame = tk.Frame(self.root, bg=self.bg_main)
        self.control_frame.pack(pady=16)

        tk.Button(self.control_frame, text="Save", width=9,
                  command=self.save_game_data).pack(side=tk.LEFT, padx=6)
        tk.Button(self.control_frame, text="Load", width=9,
                  command=self.load_game_data).pack(side=tk.LEFT, padx=6)
        tk.Button(self.control_frame, text="Undo", width=9,
                  command=self.undo_game_data).pack(side=tk.LEFT, padx=6)
        tk.Button(self.control_frame, text="Reset", width=9,
                  command=self.reset_game_data).pack(side=tk.LEFT, padx=6)

    # ---------------- UI helpers ----------------

    def draw_board(self):
        for r in range(self.size):
            row = []
            for c in range(self.size):
                btn = tk.Button(
                    self.board_frame,
                    text="",
                    width=4,
                    height=2,
                    font=("Helvetica", 14, "bold"),
                    fg=self.text_primary,
                    bg=self.bg_tile_empty,
                    activebackground=self.bg_hover,
                    relief="solid",
                    borderwidth=1,
                    command=lambda r=r, c=c: self.on_cell_click(r, c)
                )
                btn.grid(row=r, column=c, padx=4, pady=4)
                row.append(btn)
            self.buttons.append(row)

    def refresh_board(self):
        for r in range(self.size):
            for c in range(self.size):
                val = self.board[r][c]
                self.buttons[r][c].config(
                    text=str(val) if val != 0 else "",
                    bg=self.bg_tile_filled if val != 0 else self.bg_tile_empty
                )

        self.score_label.config(text=f"Score: {self.score}")
        self.next_label.config(text=f"Next: {self.next_number}")

    # ---------------- Game interaction ----------------

    def on_cell_click(self, row, col):
        ok, points, message = self.logic.place_number(
            self.board,
            self.next_number,
            row,
            col
        )

        if ok:
            play_sound(success=True)
            self.score += points
            self.next_number += 1
            self.refresh_board()
        else:
            play_sound(success=False)
            messagebox.showinfo("Invalid Move", message)

    def load_game_data(self):
        try:
            board, next_number, score = self.game_storage.load("savefile", self.size)
            self.board = board
            self.next_number = next_number
            self.score = score
            self.logic.turns = []

            positions = {}
            for r in range(self.size):
                for c in range(self.size):
                    if board[r][c] != 0:
                        positions[board[r][c]] = (r, c)

            for i in range(1, next_number):
                if i in positions:
                    self.logic.turns.append(positions[i])
                    if i == 1:
                        self.one_pos = positions[i]

            self.refresh_board()
            messagebox.showinfo("Success", "Game loaded successfully!")
        except Exception:
            messagebox.showerror("Error", "Failed to load")

    def save_game_data(self):
        try:
            self.game_storage.save("savefile", self.board, self.next_number, self.score)
            messagebox.showinfo("Success", "Game saved successfully!")
        except Exception:
            messagebox.showerror("Error", "Failed to save")

    def undo_game_data(self):
        try:
            success, score_change = self.logic.undo(self.board)
            if success:
                self.score += score_change
                self.next_number -= 1
                self.refresh_board()
        except Exception:
            messagebox.showerror("Error", "Cannot undo")

    def reset_game_data(self):
        if not messagebox.askyesno("Reset Game", "Are you sure you want to reset the board?"):
            return

        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.logic.turns = []
        self.score = 0
        self.next_number = 1

        r, c = self.one_pos
        self.board[r][c] = 1
        self.logic.turns.append((r, c))
        self.next_number = 2
        self.refresh_board()

    def start(self):
        self.root.mainloop()
