#main.py
#Entry point of the application.
#cordinates UI, game logic, and storage.

# main.py
from ui import GameUI

def main():
    ui = GameUI(size=5)
    ui.start()

if __name__ == "__main__":
    main()



