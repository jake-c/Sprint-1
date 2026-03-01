# solver.py
from copy import deepcopy

class GameSolver:
    def __init__(self, logic):
        self.logic = logic

    # ---------- Level 1 (5x5) ----------
    def solve_level1(self, board5, start_num):
        return self._bt_level1(board5, start_num)

    def _bt_level1(self, board, num):
        if num > 25:
            return True

        prev = self.logic.find_number(board, num - 1)
        if prev is None:
            return False

        pr, pc = prev
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = pr + dr, pc + dc
                if 0 <= r < 5 and 0 <= c < 5 and board[r][c] == 0:
                    board[r][c] = num
                    if self._bt_level1(board, num + 1):
                        return True
                    board[r][c] = 0
        return False

    # ---------- Level 2 (7x7 outer ring) ----------
    def solve_level2(self, board7, start_num):
        return self._bt_level2(board7, start_num)

    def _bt_level2(self, board7, num):
        if num > 25:
            return True

        inner_pos = self.logic.find_number_in_inner_7x7(board7, num)
        if inner_pos is None:
            return False

        valid_cells = self.logic.get_valid_outer_cells(board7, inner_pos)
        for (r, c) in valid_cells:
            if board7[r][c] == 0:
                board7[r][c] = num
                if self._bt_level2(board7, num + 1):
                    return True
                board7[r][c] = 0
        return False

    # ---------- Level 3 (7x7 inner 5x5) ----------
    def solve_level3(self, board7, start_num):
        return self._bt_level3(board7, start_num)

    def _bt_level3(self, board7, num):
        if num > 25:
            return True

        valid = self.logic.get_valid_level3_cells(board7, num)
        for (r, c) in valid:
            if board7[r][c] == 0:
                board7[r][c] = num
                if self._bt_level3(board7, num + 1):
                    return True
                board7[r][c] = 0
        return False

    # ---------- Wrapper ----------
    def solve_copy(self, board, level, start_num):
        temp = deepcopy(board)
        if level == 1:
            ok = self.solve_level1(temp, start_num)
        elif level == 2:
            ok = self.solve_level2(temp, start_num)
        else:
            ok = self.solve_level3(temp, start_num)
        return ok, temp
