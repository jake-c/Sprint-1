# ui_level2.py
# Level 2 UI: inner 5x5 is pre-filled (1..25) and locked. Player places 2..25 on the outer ring
# at the ends of the row/column (and diagonals when applicable) of the corresponding inner number.

import tkinter as tk
from tkinter import messagebox, simpledialog
from ui_helpers import play_sound

from logic import GameLogic
from storage import GameStorage
from solver import solve_level2


class GameUILevel2:
    def __init__(self, player_name: str | None = None, level1_board: list[list[int]] | None = None, acc_score=0, time_limit=60):
        # Level 2 uses a 7x7 grid: outer ring + inner 5x5
        self.starting_time = time_limit
        self.size = 7
        self.level = 2
        self.acc_score = acc_score
        # Level 1 size doesn't matter for Level 2 helpers
        self.logic = GameLogic(size=5)
        self.game_storage = GameStorage()

        self.player_name = player_name  # carry over from Level 1 if available
        self.solve_cells = set() # cells filled with solution

        # ---- Game state ----
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.next_number = 2  # numbers 2..25 to be placed on outer ring
        self.score = acc_score
        self.turns_outer = []  # stack of (r, c, number) for undo

        # ---- Colors (match refined light scheme) ----
        self.bg_main = "#f7f8fa"
        self.bg_tile_outer = "#ffffff"
        self.bg_tile_outer_filled = "#e8f0fe"
        self.bg_tile_inner = "#e0e0e0"
        self.bg_hover = "#dde7f5"
        self.text_primary = "#1f2933"

        # ---- Window ----
        self.root = tk.Tk()
        self.root.title("Number Placement Game – Level 2")
        self.root.resizable(False, False)
        self.root.configure(bg=self.bg_main)

        # ---- Info bar ----
        self.info_frame = tk.Frame(self.root, bg=self.bg_main)
        self.info_frame.pack(pady=12)

        self.level_label = tk.Label(
            self.info_frame,
            text="Level: 2",
            font=("Helvetica", 14),
            fg=self.text_primary,
            bg=self.bg_main
        )
        self.level_label.pack(side=tk.LEFT, padx=16)

        self.score_label = tk.Label(
            self.info_frame,
            text="Score: 0",
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

        # ---- Initialize inner 5x5 with 1..25 and lock those cells ----
        self.populate_inner_board(level1_board)

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

        self.refresh_board()

        # If we start Level 2 directly (not from Level 1), ask for player name once.
        if not self.player_name:
            self.player_name = simpledialog.askstring(
                "Player Name", "Enter player name for Level 2:")
            if not self.player_name:
                self.player_name = "Unknown"

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
                    bg=self.bg_tile_outer,
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

    def populate_inner_board(self, prev_board: list[list[int]] | None = None):
        # If prev_board is passed we should remap it
        if prev_board:
            for r in range(1, 6):
                for c in range(1, 6):
                    self.board[r][c] = prev_board[r - 1][c - 1]
        else:
            num = 1
            for r in range(1, 6):
                for c in range(1, 6):
                    self.board[r][c] = num
                    num += 1

    def refresh_board(self):
        for r in range(self.size):
            for c in range(self.size):
                val = self.board[r][c]
                if self.is_inner_cell(r, c):
                    # locked inner cell
                    self.buttons[r][c].config(
                        text=str(val),
                        state="disabled",
                        bg=self.bg_tile_inner
                    )
                else:
                    # outer ring cell
                    if val != 0 and (r, c) in self.solve_cells:
                        color = "#caf5a5"
                    elif val != 0:
                        color = self.bg_tile_outer_filled
                    else:
                        color = self.bg_tile_outer
                    self.buttons[r][c].config(
                        state="normal",
                        text=str(val) if val != 0 else "",
                        bg=color
                    )

        self.score_label.config(text=f"Score: {self.score}")
        self.next_label.config(text=f"Next: {self.next_number}")

    # ---------------- Level 2 rules ----------------
    def get_valid_cells_for_next(self):
        inner_pos = self.logic.find_number(self.board, self.next_number)
        return self.logic.get_valid_outer_cells(self.board, inner_pos)

    # What happens when a cell is clicked
    def on_cell_click(self, r, c):
        if self.is_inner_cell(r, c):
            return  # inner is locked

        if self.board[r][c] != 0:
            play_sound(False)
            messagebox.showinfo("Invalid Move", "Cell already filled.")
            return

        valid = self.get_valid_cells_for_next()
        if (r, c) not in valid:
            play_sound(False)
            messagebox.showinfo(
                "Invalid Move", "Invalid outer-ring placement for this number.")
            return

        # Place the number
        self.board[r][c] = self.next_number
        self.turns_outer.append((r, c, self.next_number))

        # Simple scoring: +1 per correct placement
        self.score += 1

        play_sound(True)
        self.next_number += 1
        self.refresh_board()

        # Win condition: placed 2..25 (next becomes 26)
        if self.next_number == 26:
            self.handle_level_complete(False)
            return

        # Dead-end condition: no valid cells for the next number
        if len(self.get_valid_cells_for_next()) == 0:
            messagebox.showinfo(
                "Game Over", "No valid moves remaining for the next number.")
            return

    def handle_level_complete(self, from_solution):
        # Log completed Level 2 game (User Story 7 applies to all levels)
        self.stop_timer()
        if not from_solution and self.time_left > 0:
            self.score += self.time_left

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
            "Level Complete", "Level 2 complete! Launching Level 3...")

        # Launch Level 3 using this final board (outer ring becomes the constraints)
        try:
            from ui_level3 import GameUILevel3
            self.root.destroy()
            print(self.score)
            GameUILevel3(board7=self.board, player_name=self.player_name,
                         acc_score=self.score, time_limit=self.starting_time).start()
        except Exception:
            # If Level 3 file isn't present, just close cleanly
            self.root.destroy()

    # Save/Load
    def save_game_data(self):
        try:
            self.game_storage.save(
                "savefile_level2", self.board, self.next_number, self.score)
            messagebox.showinfo("Success", "Level 2 saved successfully!")
        except Exception:
            messagebox.showerror("Error", "Failed to save Level 2.")

    # Function to find the outer ring position number
    def find_outer_position(self, number: int):
        for r in range(self.size):
            for c in range(self.size):
                if self.is_outer_cell(r, c) and self.board[r][c] == number:
                    return (r, c)
        return None

    # Loading game information
    def load_game_data(self):
        try:
            board, next_number, score = self.game_storage.load(
                "savefile_level2", size=7)
            self.board = board
            self.next_number = next_number
            self.score = score
            self.acc_score = score

            self.turns_outer = []
            for k in range(2, self.next_number):
                pos = self.find_outer_position(k)
                if pos:
                    self.turns_outer.append((pos[0], pos[1], k))

            self.refresh_board()
            messagebox.showinfo("Success", "Level 2 loaded successfully!")
        except Exception:
            messagebox.showerror("Error", "Failed to load Level 2.")

    # Function for the undo command
    def undo_game_data(self):
        if not self.turns_outer:
            return

        r, c, num = self.turns_outer.pop()
        self.board[r][c] = 0
        self.next_number = num
        self.score -= 1
        self.refresh_board()

    # Function for the reset button
    def reset_game_data(self):
        if not messagebox.askyesno("Reset Level 2", "Reset Level 2 outer ring?"):
            return

        for r in range(self.size):
            for c in range(self.size):
                if self.is_outer_cell(r, c):
                    self.board[r][c] = 0

        cells_placed = len(self.turns_outer)
        self.next_number = 2
        self.score -= cells_placed
        self.turns_outer = []
        self.refresh_board()

    # Function to show full solution when requested
    def show_solution(self):
        solved = solve_level2(self.board)

        if solved is None:
            # Clear cells and solve from scratch
            blank = [row[:] for row in self.board]
            for r in range (self.size):
                for c in range(self.size):
                    if self.is_outer_cell(r, c):
                        blank[r][c] = 0
            self.turns_outer = []
            self.next_number = 2
            solved = solve_level2(blank)
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
        self.next_number = 26  # marks level complete visually
        self.refresh_board()
        # Automatically move to Level 3
        self.handle_level_complete(True)

    def start(self):
        self.root.mainloop()
