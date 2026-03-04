import platform
import os
import threading


# Function to play the sound based on success value (True/False)
def _play_sound(success):
    system_name = platform.system()

    # Windows
    if system_name == "Windows":
        try:
            import winsound
            wav = r".\assets\success.wav" if success else r".\assets\wrong.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except ImportError:
            pass

    # MacOS
    elif system_name == "Darwin":
        os.system(
            "afplay /System/Library/Sounds/Glass.aiff &"
            if success
            else "afplay /System/Library/Sounds/Basso.aiff &"
        )

    # Linux
    elif system_name == "Linux":
        print("\a", end="", flush=True)


def play_sound(success):
    threading.Thread(target=_play_sound, args=(success,), daemon=True).start()