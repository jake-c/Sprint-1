# logic.py
# Handles all game rules and scoring logic.
# This class does NOT deal with user input or file I/O.

class GameLogic:
    def __init__(self, size=5):
        # size of the board (5x5)
        self.size = size
        # the number of turns made
        self.turns = []

    def is_in_bounds(self, r, c):
        # check if a cell is inside the board boundaries
        return 0 <= r < self.size and 0 <= c < self.size

    def cell_is_empty(self, board, r, c):
        return board[r][c] == 0

    def find_number(self, board, value):
        # locate a specific number on the board (works for 5x5 or 7x7)
        for r in range(len(board)):
            for c in range(len(board[0])):
                if board[r][c] == value:
                    return (r, c)
        return None

    def diagonal_corners(self, r, c):
        return [
            (r - 1, c - 1),
            (r - 1, c + 1),
            (r + 1, c - 1),
            (r + 1, c + 1)
        ]

    def score_for_placement(self, board, prev_num, r, c):
        prev_pos = self.find_number(board, prev_num)
        if not prev_pos:
            return 0
        return 1 if (r, c) in self.diagonal_corners(*prev_pos) else 0

    def undo(self, board):
        if not self.turns:
            raise Exception("No turns to undo.")

        r, c = self.turns.pop()
        points = 0

        if self.turns:
            prev_number = len(self.turns)
            if self.score_for_placement(board, prev_number, r, c):
                points -= 1

        board[r][c] = 0
        return True, points

    def place_number(self, board, number, r, c):
        if board[r][c] != 0:
            return False, 0, "Cell already filled."

        if number != len(self.turns) + 1:
            return False, 0, "Wrong number."

        if number > 1:
            pr, pc = self.find_number(board, number - 1)
            if abs(pr - r) > 1 or abs(pc - c) > 1:
                return False, 0, "Must be adjacent."

        points = self.score_for_placement(board, number - 1, r, c) if number > 1 else 0
        board[r][c] = number
        self.turns.append((r, c))
        return True, points, ""

    # ---------------- Level 2 helpers ----------------
    def get_valid_outer_cells(self, board7, inner_pos):
        """
        Level 2: given a 7x7 board and the position (r,c) of the target number
        inside the inner 5x5 (indices 1..5), return the valid empty cells on the
        outer ring where that same number may be placed.
        """
        if inner_pos is None:
            return []

        r, c = inner_pos
        candidates = []

        # Row ends
        candidates.append((r, 0))
        candidates.append((r, 6))

        # Column ends
        candidates.append((0, c))
        candidates.append((6, c))

        # Diagonal ends (only if the number lies on a major diagonal)
        if r == c:
            candidates.append((0, 0))
            candidates.append((6, 6))

        if r + c == 6:
            candidates.append((0, 6))
            candidates.append((6, 0))

        # Unique + empty only
        out = []
        for cell in candidates:
            if cell not in out:
                rr, cc = cell
                if 0 <= rr < 7 and 0 <= cc < 7 and board7[rr][cc] == 0:
                    out.append(cell)
        return out
