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

        points = self.score_for_placement(
            board, number - 1, r, c) if number > 1 else 0
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

    # ---------------- Level 3 helpers ----------------
    def is_inner_5x5_of_7x7(self, r, c):
        return 1 <= r <= 5 and 1 <= c <= 5

    def is_outer_ring_cell_7x7(self, r, c):
        return r in (0, 6) or c in (0, 6)

    def is_outer_corner_7x7(self, r, c):
        return (r, c) in [(0, 0), (0, 6), (6, 0), (6, 6)]

    def on_main_diagonals_7x7(self, r, c):
        return (r == c) or (r + c == 6)

    def find_number_on_outer_ring(self, board7, value):
        """
        Find value ONLY on the outer ring of the 7x7 board.
        This avoids accidentally finding the same number after it's placed inside.
        """
        for r in range(7):
            for c in range(7):
                if self.is_outer_ring_cell_7x7(r, c) and board7[r][c] == value:
                    return (r, c)
        return None

    def find_number_in_inner_7x7(self, board7, value):
        """
        Find value ONLY in the inner 5x5 (rows/cols 1..5) of a 7x7 board.
        Level 3 needs this because numbers also appear on the outer ring.
        """
        for r in range(1, 6):
            for c in range(1, 6):
                if board7[r][c] == value:
                    return (r, c)
        return None

    def ring_constraint_allows_cell(self, ring_pos, target_r, target_c):
        """
        Level 3 Rule #3:
        Use the ring position of the number to restrict placement in the inner 5x5.

        Deterministic rule:
        - If number is on LEFT or RIGHT edge of ring -> must place in SAME ROW (inner)
        - If number is on TOP or BOTTOM edge of ring -> must place in SAME COLUMN (inner)
        """
        rr, cc = ring_pos

        # Left / Right edge => same row
        if cc == 0 or cc == 6:
            return target_r == rr

        # Top / Bottom edge => same column
        if rr == 0 or rr == 6:
            return target_c == cc

        return False

    def get_valid_level3_cells(self, board7, next_number):
        """
        Returns valid inner cells for placing next_number in Level 3.

        Assumes:
        - board7 is 7x7
        - outer ring contains the Level 2 final placements (2..25)
        - inner 5x5 is empty except for 1 and any already placed 2..k
        - next_number is in [2..25]
        """
        if next_number < 2 or next_number > 25:
            return []

        ring_pos = self.find_number_on_outer_ring(board7, next_number)
        if ring_pos is None:
            return []

        # Previous number must be the INNER one (not the ring copy)
        prev_pos = self.find_number_in_inner_7x7(board7, next_number - 1)
        if prev_pos is None:
            return []

        pr, pc = prev_pos

        # Level 1 adjacency candidates around previous inner number
        candidates = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r = pr + dr
                c = pc + dc
                if self.is_inner_5x5_of_7x7(r, c) and board7[r][c] == 0:
                    candidates.append((r, c))

        # Rule #3 (row/column intersection) applies only to NON-corner ring cells.
        # Rule #4 (yellow corner ring cells) replaces it with diagonal-board constraint.
        if self.is_outer_corner_7x7(*ring_pos):
            filtered = [(r, c)
                        for (r, c) in candidates if self.on_main_diagonals_7x7(r, c)]
        else:
            filtered = [
                (r, c)
                for (r, c) in candidates
                if self.ring_constraint_allows_cell(ring_pos, r, c)
            ]

        return filtered

    def place_number_level3(self, board7, number, r, c):
        """
        Place 'number' in Level 3 inside the inner 5x5.
        Level 3 places 2..25 in order, with 1 already on the board.

        We use self.turns for Level 3 placements only (2..25).
        Required number = len(self.turns) + 2
        """
        if not (0 <= r < 7 and 0 <= c < 7):
            return False, 0, "Out of bounds."

        if not self.is_inner_5x5_of_7x7(r, c):
            return False, 0, "Must place inside the inner 5x5."

        if board7[r][c] != 0:
            return False, 0, "Cell already filled."

        required = len(self.turns) + 2
        if number != required:
            return False, 0, "Wrong number."

        valid = self.get_valid_level3_cells(board7, number)
        if (r, c) not in valid:
            return False, 0, "Invalid placement."

        # IMPORTANT: Level 3 scoring must reference the INNER previous number, not the ring copy
        prev_inner = self.find_number_in_inner_7x7(board7, number - 1)
        if prev_inner is None:
            points = 0
        else:
            pr, pc = prev_inner
            points = 1 if (r, c) in self.diagonal_corners(pr, pc) else 0

        board7[r][c] = number
        self.turns.append((r, c))
        return True, points, ""

    def undo_level3(self, board7):
        """
        Undo last Level 3 placement.
        """
        if not self.turns:
            raise Exception("No turns to undo.")

        r, c = self.turns.pop()

        # Determine which number we removed: it was (len(turns)+2) before pop
        removed_number = len(self.turns) + 3  # after pop
        points = 0

        if removed_number > 2:
            # check score impact using INNER previous number
            prev_inner = self.find_number_in_inner_7x7(
                board7, removed_number - 1)
            if prev_inner is not None:
                pr, pc = prev_inner
                if (r, c) in self.diagonal_corners(pr, pc):
                    points -= 1

        board7[r][c] = 0
        return True, points
