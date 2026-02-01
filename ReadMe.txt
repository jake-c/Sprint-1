Ass1 - 5x5 Matrix Game (Python)

Files:
- main.py: runs the program
- ui.py: GameUI class (command-line UI + menu)
- logic.py: GameLogic class (rules + scoring)
- storage.py: GameStorage class (save/load text file)
- sample_save.txt: sample incomplete saved game

OS: Windows/macOS/Linux
Python version: 3.9+ recommended

Run:
1) Open a terminal in the Ass1 folder
2) python main.py
   (or on some systems: python3 main.py)

How to play:
- Choose option 1 to place the next number
- Enter row col (1-5 1-5)
- +1 point if the placement is in a diagonal corner cell of the previous number
- Invalid placement ends the game automatically
- Use Save/Load to resume later
