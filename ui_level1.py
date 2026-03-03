# ui_level1.py
# Handles all user interaction and display logic for Level 1

import tkinter as tk
from tkinter import messagebox, simpledialog
import random

from ui_helpers import play_sound

from logic import GameLogic
from storage import GameStorage

from solver import solve_level1


class GameUILevel1:
    def __init__(self, size=5, time_limit=60, player_name=None):
        self.player_name = player_name
        self.starting_time = time_limit
        self.size = size
        self.logic = GameLogic(size=size)
        self.game_storage = GameStorage()
        self.solve_cells = set() # cells filled with solution

        # ---- Game state ----
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.next_number = 1
        self.score = 0
        self.level = 1
        self.one_pos = None

        # ---- Colors ----
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

        # ---- Info bar ----
        self.info_frame = tk.Frame(self.root, bg=self.bg_main)
        self.info_frame.pack(pady=12)

        self.score_label = tk.Label(
            self.info_frame, text="Score: 0",
            font=("Helvetica", 14, "bold"),
            fg=self.text_primary, bg=self.bg_main
        )
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.level_label = tk.Label(
            self.info_frame, text="Level: 1",
            font=("Helvetica", 14),
            fg=self.text_primary, bg=self.bg_main
        )
        self.level_label.pack(side=tk.LEFT, padx=20)

        self.next_label = tk.Label(
            self.info_frame, text="Next: 1",
            font=("Helvetica", 14, "bold"),
            fg="blue", bg=self.bg_main
        )
        self.next_label.pack(side=tk.LEFT, padx=20)

        # --- Timer ---
        self.time_left = time_limit 
        self.timer_id = None

        self.timer_label = tk.Label(
            self.info_frame, text=f"Time: {self.time_left}",
            font=("Helvetica", 14, "bold"),
            fg="red", bg=self.bg_main
        )
        self.timer_label.pack(side=tk.LEFT, padx=20)

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
        self.one_pos = (r, c)

        self.refresh_board()

        # ---- Controls ----
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
        tk.Button(self.control_frame, text="Show Solution", width=12,
                  command=self.show_solution).pack(side=tk.LEFT, padx=6)

        self.update_timer()

    def stop_timer(self):
        # Check if the timer is currently running
        if getattr(self, "timer_id", None):
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def update_timer(self):
        if self.check_level_complete():
            return  # Stop the timer if they win

        self.time_left -= 1
        self.timer_label.config(text=f"Time: {self.time_left}")
        if self.time_left < 0:
            self.score -= 1
            self.timer_label.config(fg="darkred") # color in red to notify the user of time
        self.timer_id = self.root.after(1000, self.update_timer)

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
                if val != 0 and (r, c) in self.solve_cells:
                    color = "#caf5a5"
                elif val != 0:
                    color = self.bg_tile_filled
                else:
                    color = self.bg_tile_empty
                self.buttons[r][c].config(
                    text=str(val) if val != 0 else "",
                    bg=color
                )

        self.score_label.config(text=f"Score: {self.score}")
        self.next_label.config(text=f"Next: {self.next_number}")

    # ---------------- Game logic ----------------
    def check_level_complete(self):
        return self.next_number == 26

    def on_cell_click(self, row, col):
        ok, points, message = self.logic.place_number(
            self.board, self.next_number, row, col
        )

        if ok:
            play_sound(True)
            self.score += points
            self.next_number += 1
            self.refresh_board()

            # -------- Level 1 completion --------
            if self.check_level_complete():
                name = simpledialog.askstring(
                    "Level Complete",
                    "Level 1 complete!\nEnter player name:"
                )
                if not name:
                    name = "Unknown"

                self.stop_timer()
                if self.time_left > 0:
                    self.score += self.time_left

                # User Story 7 logging
                self.game_storage.log_completed_game(
                    name=name,
                    level=self.level,
                    score=self.score,
                    board=self.board
                )

                messagebox.showinfo(
                    "Level Complete",
                    "Level 1 complete!\nLevel 2 is now unlocked."
                )

                # Launch Level 2
                try:
                    from ui_level2 import GameUILevel2
                    self.root.destroy()
                    GameUILevel2(player_name=name,
                                 level1_board=self.board, acc_score=self.score, time_limit=self.starting_time).start()
                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Failed to launch Level 2:\n{e}"
                    )

        else:
            play_sound(False)
            messagebox.showinfo("Invalid Move", message)

    # Save/Load
    def save_game_data(self):
        try:
            self.game_storage.save(
                "savefile", self.board, self.next_number, self.score
            )
            messagebox.showinfo("Success", "Game saved successfully!")
        except Exception:
            messagebox.showerror("Error", "Failed to save")

    def load_game_data(self):
        try:
            board, next_number, score = self.game_storage.load(
                "savefile", self.size)
            self.board = board
            self.next_number = next_number
            self.score = score

            # rebuild turn history
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
        if not messagebox.askyesno("Reset Game", "Are you sure you want to reset Level 1?"):
            return

        cells_placed = len(self.logic.turns)
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.logic.turns = []
        self.score -= cells_placed

        r, c = self.one_pos
        self.board[r][c] = 1
        self.next_number = 2
        self.refresh_board()

        return

    def show_solution(self):
        solved = solve_level1(self.board)

        if solved is None:
            # Clear cells and solve from scratch
            blank = [[0]*self.size for _ in range(self.size)]
            r, c = self.one_pos
            blank[r][c] = 1
            solved = solve_level1(blank)
            if solved is None:
                messagebox.showerror("No Solution", "No solution could be found for this board.")
                return
            self.board = blank

        # Record which cells the solver filled
        self.solve_cells = set()
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0 and solved[r][c] != 0:
                    self.solve_cells.add((r, c))

        self.board = solved
        self.next_number = 26
        self.refresh_board()
        # Game is finished, name is the one that is equal to the username entered in the auth stage
        name = self.player_name or "Unknown"

        # Log completion
        self.game_storage.log_completed_game(
            name=name,
            level=self.level,
            score=self.score,
            board=self.board
        )

        messagebox.showinfo(
            "Level Complete",
            "Level 1 complete!\nLevel 2 is now unlocked."
        )

        # Launch Level 2
        try:
            from ui_level2 import GameUILevel2
            self.root.destroy()
            print(self.score)
            GameUILevel2(player_name=name, level1_board=self.board,
                         acc_score=self.score, time_limit=self.starting_time).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Level 2:\n{e}")

    def start(self):
        self.root.mainloop()
