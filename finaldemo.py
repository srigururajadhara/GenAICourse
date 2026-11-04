import pyautogui
import time

# Open Spotlight Search
pyautogui.hotkey('command', 'space', interval=0.1)
time.sleep(2)

# Type Chrome
pyautogui.write('Google Chrome', interval=0.5)
time.sleep(2)

# Press Enter
pyautogui.press('enter')
time.sleep(2)

print("Chrome opened successfully") 

print("Step 2: go to the website")
pyautogui.hotkey('command', 't', interval=0.1)
time.sleep(2)
print("Step 3: type the website URL")
pyautogui.write('https://www.accuweather.com/en/in/bengaluru/204108/weather-forecast/204108?type=locality&city=bengaluru', interval=0.1)
time.sleep(2)
print("Step 4: Press Enter to go to the website")
pyautogui.press('enter')
time.sleep(5)
print("Step 5: Website opened successfully")

print("Step 6: copy the weather information")
pyautogui.hotkey('command', 'a', interval=0.1)
time.sleep(2)
pyautogui.hotkey('command', 'c', interval=0.1)
time.sleep(2)
print("Step 7: Open Notepad")
pyautogui.hotkey('command', 'space', interval=0.1)
time.sleep(2)
pyautogui.write('TextEdit', interval=0.5)
time.sleep(2)
pyautogui.press('enter')
time.sleep(2)
#click new document
pyautogui.hotkey('command', 'n', interval=0.1)
time.sleep(2)

print("Step 8: Paste the weather information")
pyautogui.hotkey('command', 'v', interval=0.1)
time.sleep(2)
print("Step 9: Save the file")
pyautogui.hotkey('command', 's', interval=0.1)
time.sleep(2)
pyautogui.write('weather_info.txt', interval=0.1)
time.sleep(2)
pyautogui.press('enter')
print("File saved successfully")