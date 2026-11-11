import pyautogui
import time

def type_text(text):
    # This simulates keyboard typing
    pyautogui.typewrite("Sri guru") 
    
    # If you want output in the console, you must use print()
    print("\nCommand finished running in the console.")

    #hold Key down for 2 seconds
    pyautogui.keyDown('shift')

    pyautogui.typewrite("test")


    #hotkey press
    pyautogui.hotkey('ctrl', 'c') 

# 1. Pause for 3 seconds so you can click into a blank text area
time.sleep(3)

# 2. Actually call the function to make it run
type_text("test")



