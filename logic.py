# logic.py
# Handles all game rules and scoring logic.
# This class does NOT deal with user input or file I/O.

class GameLogic:
    def __init__(self, size=5):
        # size of the board (5x5)
        self.size = size

    def is_in_bounds(self, r, c):
        # check if a cell is inside the board boundaries
        return 0 <= r < self.size and 0 <= c < self.size

    def cell_is_empty(self, board, r, c):
        # check if a cell exists and is not already filled
        return self.is_in_bounds(r, c) and board[r][c] == 0

    def find_number(self, board, value):
        # locate a specific number on the board
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] == value:
                    return (r, c)
        return None

    def diagonal_corners(self, r, c):
        # Return the four diagonal corner positions around (r, c)
        return [
            (r - 1, c - 1),
            (r - 1, c + 1),
            (r + 1, c - 1),
            (r + 1, c + 1)
        ]

    def score_for_placement(self, board, prev_num, r, c):
        # determine if placing the current number earns a point
        prev_pos = self.find_number(board, prev_num)
        if not prev_pos:
            return 0

        pr, pc = prev_pos
        return 1 if (r, c) in self.diagonal_corners(pr, pc) else 0

    def place_number(self, board, number, r, c):
        """
        Attempt to place a number on the board.

        Returns:
        - ok: whether the placement is valid
        - points_earned: 1 if diagonal corner rule is satisfied, else 0
        - message: status message for the UI
        """

        # Invalid placement: outside board
        if not self.is_in_bounds(r, c):
            return (False, 0, "Invalid: out of bounds. Game over.")

        # Invalid placement: cell already filled
        if board[r][c] != 0:
            return (False, 0, "Invalid: cell already filled. Game over.")

        # Enforce adjacency rule for all numbers after 1
        if number > 1:
            prev_pos = self.find_number(board, number - 1)
            if not prev_pos:
                return (False, 0, "Invalid: predecessor not found.")

            pr, pc = prev_pos
            row_diff = abs(r - pr)
            col_diff = abs(c - pc)

            # Must be one step away (including diagonals), but not same cell
            if row_diff > 1 or col_diff > 1 or (row_diff == 0 and col_diff == 0):
                return (False, 0, "Invalid: not adjacent to predecessor. Game over.")

        # Calculate score
        points = 0
        if number > 1:
            points = self.score_for_placement(board, number - 1, r, c)

        # Place the number
        board[r][c] = number
        return (True, points, f"Placed {number} at ({r+1},{c+1}).")


