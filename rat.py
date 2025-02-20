# This file is for the listener in audio_handler.py.  It has its own file because it is the rat in the story of the pied piper that is moved
#   by his music into action, much like how this function, rat, presses a key based on the music being played.
import notemap as nm
import pyautogui

# Gather the notemap, keybind, and input, then perform the correct keypress
def rat(notemap, keybind, note):
    keypress = keybind[notemap[note]]
    pyautogui.press(keypress)
    
