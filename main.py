# main.py
import tkinter as tk
from tkinter import simpledialog
from ui_level1 import GameUILevel1

if __name__ == "__main__":
    temp_root = tk.Tk()
    temp_root.withdraw()
    
    # Timer window for the user to enter time
    user_time_str = simpledialog.askstring(
        "Timer Setup",
        "Enter timer duration in seconds for all levels:\n(Leave blank or cancel for default 60s)"
    )
    
    # Default time limit is 60
    if user_time_str is None or user_time_str.strip() == "":
        time_limit = 60
    else:
        try:
            # Try to convert user typed text into a number
            time_limit = int(user_time_str)
            
            if time_limit < 5:
                time_limit = 5
        except ValueError:
            # If they user letters like "abc", default to 60
            time_limit = 60
    
    temp_root.destroy()
    
    # Pass the time_limit into Level 1
    GameUILevel1(time_limit=time_limit).start()