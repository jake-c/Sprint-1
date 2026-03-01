# solver.py
from copy import deepcopy
from logic import GameLogic

# ----------------------------
# Helpers to detect start number
# ----------------------------
def _next_number_level1(board5):
    # Level 1: numbers are on 5x5 only
    max_seen = 0
    for row in board5:
        for v in row:
            if isinstance(v, int) and v > max_seen:
                max_seen = v
    return max_seen + 1


def _next_number_level2(board7):
    # Level 2: outer ring contains 2..25 (inner is locked 1..25)
    # Find smallest number in 2..25 not already on the OUTER ring
    logic = GameLogic()
    placed = set()
    for r in range(7):
        for c in range(7):
            if logic.is_outer_ring_cell_7x7(r, c) and isinstance(board7[r][c], int):
                v = board7[r][c]
                if 2 <= v <= 25:
                    placed.add(v)

    for k in range(2, 26):
        if k not in placed:
            return k
    return 26


def _next_number_level3(board7):
    # Level 3: inner 5x5 contains 1..25 placements during play
    max_seen = 0
    for r in range(1, 6):
        for c in range(1, 6):
            v = board7[r][c]
            if isinstance(v, int) and v > max_seen:
                max_seen = v
    return max_seen + 1


# ----------------------------
# Backtracking solvers
# ----------------------------
def _bt_level1(logic, board, num):
    if num > 25:
        return True

    prev = logic.find_number(board, num - 1)
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
                if _bt_level1(logic, board, num + 1):
                    return True
                board[r][c] = 0
    return False


def _bt_level2(logic, board7, num):
    if num > 25:
        return True

    # Find the number INSIDE the inner 5x5 (it’s pre-filled 1..25 in Level 2)
    inner_pos = logic.find_number(board7, num)
    if inner_pos is None:
        return False

    valid_cells = logic.get_valid_outer_cells(board7, inner_pos)

    for (r, c) in valid_cells:
        if board7[r][c] == 0:
            board7[r][c] = num
            if _bt_level2(logic, board7, num + 1):
                return True
            board7[r][c] = 0

    return False


def _bt_level3(logic, board7, num):
    if num > 25:
        return True

    valid = logic.get_valid_level3_cells(board7, num)

    for (r, c) in valid:
        if board7[r][c] == 0:
            board7[r][c] = num
            if _bt_level3(logic, board7, num + 1):
                return True
            board7[r][c] = 0

    return False


# ----------------------------
# Public functions used by UI
# ----------------------------
def solve_level1(board5):
    temp = deepcopy(board5)
    logic = GameLogic(size=5)

    start_num = _next_number_level1(temp)
    if start_num <= 1:
        start_num = 2

    ok = _bt_level1(logic, temp, start_num)
    return temp if ok else None


def solve_level2(board7):
    temp = deepcopy(board7)
    logic = GameLogic(size=5)

    start_num = _next_number_level2(temp)
    ok = _bt_level2(logic, temp, start_num)
    return temp if ok else None


def solve_level3(board7):
    temp = deepcopy(board7)
    logic = GameLogic(size=5)

    start_num = _next_number_level3(temp)
    if start_num <= 1:
        start_num = 2

    ok = _bt_level3(logic, temp, start_num)
    return temp if ok else None
