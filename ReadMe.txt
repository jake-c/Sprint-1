Number placement game (Python)

Files:
- main.py: program entry point, launches Level 1
- ui_level1.py: Level 1 GameUI (5x5 grid gameplay)
- ui_level2.py: Level 2 GameUI (7x7 grid with outer ring)
- ui_level3.py: Level 3 GameUI (7x7 grid with inner ring)
- logic.py: GameLogic class (placement rules and validation)
- storage.py: GameStorage class (save/load and completed-game logging)
- solver.py: functions for solution generation
- ui_helpers.py: sound logic

OS: Windows / macOS / Linux
Python version: 3.9+ recommended

Run:
1) Open a terminal in the project folder
2) Run:
   python main.py
   (or on some systems: python3 main.py)

Gameplay:

Level 1 (5x5 Grid):
- The number 1 is placed randomly at the start
- The player places numbers 2 through 25
- Each number must be placed adjacent (including diagonals) to the previous number
- The next number is automatically generated and displayed
- Invalid placements are rejected
- The level ends when all numbers are placed or no valid moves remain

Level 2 (7x7 Grid with Outer Ring):
- Level 2 is only available after completing Level 1
- The inner 5x5 grid is pre-filled with numbers 1 through 25 and is locked
- The player places numbers 2 through 25 on the outer ring only
- A valid placement must be at the end of the same row or column as the number’s position in the inner grid
- If the number lies on a main diagonal in the inner grid, the corresponding corner cell(s) are also valid
- Each valid placement awards 1 point
- If no valid placements remain for the next number, the player must undo

Level 3 (5x5 and 7x7 Grids to fill out the inner grid):
- Level 3 is only available after completing Level 2
- The outer 7x7 grid is pre-filled with numbers 2 through 25 and is locked
- The player places numbers 2 through 25 on the inner ring only
- The cell to place a number must be the intersection of a row and a column with the number printed in either end of the row or column
- When a dead end occurs, the player needs to undo

Controls:
- Click a cell to place the next number
- Save: saves the current game state
- Load: loads the most recent saved game
- Undo: reverts the last move
- Reset: resets the current level
- Show Solution: shows complete solution for the current level

Save / Load:
- Saved data includes the board layout, next number, and current score
- Completed games are logged with player name, level, date/time, score, and final board

Notes:
- Level 2 cannot be accessed directly without completing Level 1
- Level 3 cannot be accessed directly without completing Level 2
- The game enforces placement rules to prevent invalid or duplicate moves

Authors:
Group project developed collaboratively


