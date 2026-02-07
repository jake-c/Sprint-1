# ui.py
# Handles all user interaction and display logic.
# No game rules or file logic should be here.

import tkinter as tk
from tkinter import messagebox
import random
from logic import GameLogic
from storage import GameStorage


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

        # ---- Color palette (light theme) ----
        self.bg_main = "#f7f8fa"
        self.bg_tile_empty = "#ffffff"
        self.bg_tile_filled = "#e8f0fe"
        self.bg_hover = "#dde7f5"
        self.text_primary = "#1f2933"
        self.border_soft = "#d1d5db"

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

        # ---- Board ----
        self.board_frame = tk.Frame(self.root, bg=self.bg_main)
        self.board_frame.pack(padx=16, pady=10)

        self.buttons = []
        self.draw_board()

        # ---- Place first number randomly ----
        r = random.randint(0, size - 1)
        c = random.randint(0, size - 1)
        self.board[r][c] = 1
        self.next_number = 2

        self.refresh_board()

        # ---- Bottom controls (scaffold only) ----
        self.control_frame = tk.Frame(self.root, bg=self.bg_main)
        self.control_frame.pack(pady=16)

        tk.Button(
            self.control_frame,
            text="Save",
            width=9,
            relief="solid",
            borderwidth=1,
            fg=self.text_primary,
            bg="#eef1f5",
            disabledforeground="#9ca3af",
            command=self.save_game_data
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            self.control_frame,
            text="Load",
            width=9,
            relief="solid",
            borderwidth=1,
            fg=self.text_primary,
            bg="#eef1f5",
            disabledforeground="#9ca3af",
            command=self.load_game_data
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            self.control_frame,
            text="Undo",
            width=9,
            relief="solid",
            borderwidth=1,
            fg=self.text_primary,
            bg="#eef1f5",
            disabledforeground="#9ca3af",
            command=self.undo_game_data
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            self.control_frame,
            text="Reset",
            width=9,
            relief="solid",
            borderwidth=1,
            fg=self.text_primary,
            bg="#eef1f5",
            disabledforeground="#9ca3af",
            command=self.reset_game_data
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            self.control_frame,
            text="Level 2",
            width=9,
            state=tk.DISABLED,
            relief="solid",
            borderwidth=1,
            fg=self.text_primary,
            bg="#eef1f5",
            disabledforeground="#9ca3af"
        ).pack(side=tk.LEFT, padx=6)

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
                    highlightthickness=0,
                    command=lambda r=r, c=c: self.on_cell_click(r, c)
                )
                btn.grid(row=r, column=c, padx=4, pady=4)
                row.append(btn)
            self.buttons.append(row)

    def refresh_board(self):
        for r in range(self.size):
            for c in range(self.size):
                val = self.board[r][c]
                if val != 0:
                    self.buttons[r][c].config(
                        text=str(val),
                        bg=self.bg_tile_filled
                    )
                else:
                    self.buttons[r][c].config(
                        text="",
                        bg=self.bg_tile_empty
                    )

        self.score_label.config(text=f"Score: {self.score}")

    # ---------------- Game interaction ----------------

    def on_cell_click(self, row, col):
        if self.game_over:
            return

        ok, points, _ = self.logic.place_number(
            self.board,
            self.next_number,
            row,
            col
        )

        if not ok:
            self.game_over = True
            self.root.title(f"Game Over – Final Score: {self.score}")
            return

        self.score += points
        self.next_number += 1
        self.refresh_board()

    # ---------------- Utils --------------------
    def load_game_data(self):
        try:
            [board, next_number, score] = self.game_storage.load("savefile", 5)
            self.board = board
            self.next_number = next_number
            self.score = score
            self.game_over = False
            self.refresh_board()
            messagebox.showinfo(title="Success", message="Game loaded successfully!")
        except:
            messagebox.showerror(title="Error", message="Failed to load")
    
    def save_game_data(self):
        try:
            self.game_storage.save(
                    "savefile", self.board, self.next_number, self.score)
            messagebox.showinfo(title="Success!", message="Game saved successfully!")
        except Exception:
            messagebox.showerror(title="Error", message="Failed to save")

    def undo_game_data(self):
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.next_number = 1
        self.score = 0
        self.game_over = False

    def reset_game_data(self):
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.next_number = 1
        self.score = 0
        self.game_over = False

        # ---- Place first number randomly ----
        r = random.randint(0, self.size - 1)
        c = random.randint(0, self.size - 1)
        self.board[r][c] = 1
        self.next_number = 2

        self.refresh_board()

    def start(self):
        self.root.mainloop()
