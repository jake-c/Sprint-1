import platform
import os
import threading


# ---------------- Sound ----------------

# To improve the game feel, dispatch audio on another thread, eliminating UI freeze.


def _play_sound(success):
    system_name = platform.system()

    if system_name == "Windows":
        try:
            import winsound
            wav = r".\assets\success.wav" if success else r".\assets\wrong.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except ImportError:
            pass

    elif system_name == "Darwin":
        os.system(
            "afplay /System/Library/Sounds/Glass.aiff &"
            if success
            else "afplay /System/Library/Sounds/Basso.aiff &"
        )

    elif system_name == "Linux":
        print("\a", end="", flush=True)


def play_sound(success):
    threading.Thread(target=_play_sound, args=(success,), daemon=True).start()