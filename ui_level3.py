# ui_level3.py
# Level 3 UI: outer ring contains Level 2 numbers (2..25) and is locked.
# Inner 5x5 is empty except for 1. Player places 2..25 using:
# - Level 1 adjacency rule (including diagonals)
# - Ring-based row/column restriction
# - Corner ring numbers require diagonal placement
# Dead-end does NOT end the game: player must Undo.

import tkinter as tk
from tkinter import messagebox, simpledialog
import platform
import os

from logic import GameLogic
from storage import GameStorage
from solver import solve_level3
from ui_helpers import play_sound


class GameUILevel3:
    def __init__(self, board7=None, player_name: str | None = None, acc_score=0, time_limit=60):
        self.starting_time = time_limit
        self.size = 7
        self.level = 3

        self.logic = GameLogic(size=5)
        self.game_storage = GameStorage()

        self.player_name = player_name
        self.solve_cells = set() # cells filled with solution

        # Game state
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.next_number = 2
        self.score = acc_score
        self.acc_score = acc_score
        self.dead_end = False  # when no valid moves, require Undo
        # We'll use logic.turns as the turn stack for Level 3 placements
        self.logic.turns = []

        # Colors
        self.bg_main = "#f7f8fa"
        self.bg_tile_outer = "#e0e0e0"          # locked ring
        self.bg_tile_inner = "#ffffff"          # playable inner
        self.bg_tile_inner_locked = "#e8f0fe"   # inner locked cell (the 1)
        self.bg_tile_filled = "#e8f0fe"
        self.bg_hover = "#dde7f5"
        self.text_primary = "#1f2933"

        # Window
        self.root = tk.Tk()
        self.root.title("Number Placement Game – Level 3")
        self.root.resizable(False, False)
        self.root.configure(bg=self.bg_main)

        # Info bar
        self.info_frame = tk.Frame(self.root, bg=self.bg_main)
        self.info_frame.pack(pady=12)

        self.level_label = tk.Label(
            self.info_frame,
            text="Level: 3",
            font=("Helvetica", 14),
            fg=self.text_primary,
            bg=self.bg_main
        )
        self.level_label.pack(side=tk.LEFT, padx=16)

        self.score_label = tk.Label(
            self.info_frame,
            text=f"Score: {self.score}",
            font=("Helvetica", 14, "bold"),
            fg=self.text_primary,
            bg=self.bg_main
        )
        self.score_label.pack(side=tk.LEFT, padx=16)

        self.next_label = tk.Label(
            self.info_frame,
            text="Next: 2",
            font=("Helvetica", 14, "bold"),
            fg="blue",
            bg=self.bg_main
        )
        self.next_label.pack(side=tk.LEFT, padx=16)

        # Rules
        messagebox.showinfo("Level 3 Rules:", "1. The inner 5x5 starts with only one cell filled and the player must fill in the rest \n2." \
        " The rules of level 1 are the same, however you must work backwards and fill in the squares that can be placed using the information from level 2\n" \
        "3. In case a deadend occurs before 25 is placed, you need to undo one or more cells and try again")

        # Timer
        self.time_left = time_limit
        self.timer_id = None

        self.timer_label = tk.Label(
            self.info_frame, text=f"Time: {self.time_left}",
            font=("Helvetica", 14, "bold"),
            fg="red", bg=self.bg_main
        )
        self.timer_label.pack(side=tk.LEFT, padx=20)
        # Board
        self.board_frame = tk.Frame(self.root, bg=self.bg_main)
        self.board_frame.pack(padx=16, pady=10)

        self.buttons = []
        self.draw_board()

        # Initializing from Level 2 final board
        # Outer ring preserved; inner cleared except 1 stays where it was.
        if board7 is not None:
            self.board = [row[:] for row in board7]
            self.prepare_level3_from_level2_board()
        else:
            # Fallback: require name and show a message (Level 3 should normally come from Level 2)
            self.board = [[0 for _ in range(self.size)]
                          for _ in range(self.size)]
            # place 1 in top-left of inner as default
            self.board[1][1] = 1

        # Controls
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

        # If we start Level 3 directly, ask for player name once.
        if not self.player_name:
            self.player_name = simpledialog.askstring(
                "Player Name", "Enter player name for Level 3:")
            if not self.player_name:
                self.player_name = "Unknown"

        self.refresh_board()
        self.check_dead_end_after_refresh()

        self.update_timer()

    def stop_timer(self):
        # Check if the timer is currently running
        if getattr(self, "timer_id", None):
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def update_timer(self):
        if self.next_number == 26:
            return
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
                    bg=self.bg_tile_inner,
                    activebackground=self.bg_hover,
                    relief="solid",
                    borderwidth=1,
                    command=lambda r=r, c=c: self.on_cell_click(r, c)
                )
                btn.grid(row=r, column=c, padx=4, pady=4)
                row.append(btn)
            self.buttons.append(row)

    def is_inner_cell(self, r, c) -> bool:
        return 1 <= r <= 5 and 1 <= c <= 5

    def is_outer_cell(self, r, c) -> bool:
        return not self.is_inner_cell(r, c)

    def prepare_level3_from_level2_board(self):
        # Find where the 1 is in the inner board (Level 2 had 1..25 in inner)
        one_pos = self.logic.find_number(self.board, 1)

        # Clear inner 5x5
        for r in range(1, 6):
            for c in range(1, 6):
                self.board[r][c] = 0

        # Restore the 1 (default to (1,1) if not found)
        if one_pos and self.is_inner_cell(*one_pos):
            self.board[one_pos[0]][one_pos[1]] = 1
        else:
            self.board[1][1] = 1

        # Ensure we start placing 2
        self.next_number = 2
        self.score = self.acc_score
        self.dead_end = False
        self.logic.turns = []

    def refresh_board(self):
        for r in range(self.size):
            for c in range(self.size):
                val = self.board[r][c]

                if self.is_outer_cell(r, c):
                    # outer ring is locked
                    self.buttons[r][c].config(
                        state="disabled",
                        text=str(val) if val != 0 else "",
                        bg=self.bg_tile_outer
                    )
                else:
                    # inner 5x5: everything is playable except the "1"
                    if val == 1:
                        self.buttons[r][c].config(
                            state="disabled",
                            text="1",
                            bg=self.bg_tile_inner_locked
                        )
                    else:
                        if val != 0 and (r, c) in self.solve_cells:
                            color = "#caf5a5"
                        elif val != 0:
                            color = self.bg_tile_filled
                        else:
                            color = self.bg_tile_inner
                        self.buttons[r][c].config(
                            state="normal",
                            text=str(val) if val != 0 else "",
                            bg=color
                        )

        self.score_label.config(text=f"Score: {self.score}")
        self.next_label.config(text=f"Next: {self.next_number}")

    # Level 3 rules
    def get_valid_cells_for_next(self):
        return self.logic.get_valid_level3_cells(self.board, self.next_number)

    def on_cell_click(self, r, c):
        if self.dead_end:
            play_sound(False)
            messagebox.showinfo(
                "Dead End", "No valid placements. Use Undo to continue.")
            return

        if not self.is_inner_cell(r, c):
            return  # outer is locked

        if self.board[r][c] != 0:
            play_sound(False)
            messagebox.showinfo("Invalid Move", "Cell already filled.")
            return

        ok, pts, msg = self.logic.place_number_level3(
            self.board, self.next_number, r, c)
        if not ok:
            play_sound(False)
            messagebox.showinfo("Invalid Move", msg or "Invalid placement.")
            return

        self.score += pts
        play_sound(True)

        self.next_number += 1
        self.refresh_board()

        if self.next_number == 26:
            self.handle_level_complete(from_solution=False)
            return

        self.check_dead_end_after_refresh()

    def check_dead_end_after_refresh(self):
        if self.next_number < 26:
            valid = self.get_valid_cells_for_next()
            if len(valid) == 0:
                self.dead_end = True
                messagebox.showinfo(
                    "Dead End", "No valid placements remain. Use Undo to continue.")

    def handle_level_complete(self, from_solution):

        # Calculate the final score if the time is left (if time is over it's already handled)
        self.stop_timer()
        if self.time_left > 0 and not from_solution:
            self.score += self.time_left

        # Log the game
        try:
            self.game_storage.log_completed_game(
                name=self.player_name or "Unknown",
                level=self.level,
                score=self.score,
                board=self.board
            )
        except Exception:
            pass

        messagebox.showinfo(
            "Level Complete", "Level 3 complete! Completed game was logged.")
        self.root.destroy()

    # Save/Load
    def save_game_data(self):
        try:
            self.game_storage.save(
                "savefile_level3", self.board, self.next_number, self.score)
            messagebox.showinfo("Success", "Level 3 saved successfully!")
        except Exception:
            messagebox.showerror("Error", "Failed to save Level 3.")

    def find_inner_position(self, number: int):
        # search only the inner 5x5 for a placed number
        for r in range(1, 6):
            for c in range(1, 6):
                if self.board[r][c] == number:
                    return (r, c)
        return None

    def load_game_data(self):
        try:
            board, next_number, score = self.game_storage.load(
                "savefile_level3", size=7)
            self.board = board
            self.next_number = next_number
            self.score = score

            # rebuild turns list based on placed inner numbers 2..(next-1)
            self.logic.turns = []
            for k in range(2, self.next_number):
                pos = self.find_inner_position(k)
                if pos:
                    self.logic.turns.append((pos[0], pos[1]))

            self.dead_end = False
            self.refresh_board()
            self.check_dead_end_after_refresh()
            messagebox.showinfo("Success", "Level 3 loaded successfully!")
        except Exception:
            messagebox.showerror("Error", "Failed to load Level 3.")

    def undo_game_data(self):
        try:
            ok, delta_pts = self.logic.undo_level3(self.board)
        except Exception:
            return

        if ok:
            # Undo returns negative points if we removed a diagonal-corner bonus
            self.score += delta_pts
            # next_number should revert to the undone number
            self.next_number -= 1
            if self.next_number < 2:
                self.next_number = 2

            self.dead_end = False
            self.refresh_board()
            self.check_dead_end_after_refresh()

    def reset_game_data(self):
        if not messagebox.askyesno("Reset Level 3", "Reset Level 3 inner grid?"):
            return

        # clear inner except 1
        one_pos = self.logic.find_number(self.board, 1)
        for r in range(1, 6):
            for c in range(1, 6):
                self.board[r][c] = 0
        if one_pos and self.is_inner_cell(*one_pos):
            self.board[one_pos[0]][one_pos[1]] = 1
        else:
            self.board[1][1] = 1

        cells_placed = len(self.logic.turns)
        self.next_number = 2
        self.score -= cells_placed
        self.dead_end = False
        self.logic.turns = []
        self.refresh_board()
        self.check_dead_end_after_refresh()

    def show_solution(self):
        solved = solve_level3(self.board)

        if solved is None:
            # Clear cells and solve from scratch
            blank = [row[:] for row in self.board]
            one_pos = self.logic.find_number(self.board, 1)
            for r in range(1, 6):
                for c in range(1, 6):
                    blank[r][c] = 0
            if one_pos and self.is_inner_cell(*one_pos):
                blank[one_pos[0]][one_pos[1]] = 1
            else:
                blank[1][1] = 1
            self.logic.turns = []
            self.next_number = 2
            solved = solve_level3(blank)
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
        self.dead_end = False
        self.refresh_board()
        self.handle_level_complete(from_solution=True)

    def start(self):
        self.root.mainloop()
