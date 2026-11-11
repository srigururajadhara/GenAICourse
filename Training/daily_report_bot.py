import pyautogui
import pyperclip
import time
from datetime import datetime

def open_spotlight_and_launch(app_name):
    """Uses macOS Spotlight to accurately open applications."""
    pyautogui.hotkey('command', 'space', interval=0.1)
    time.sleep(2)
    pyautogui.typewrite(app_name, interval=0.5)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(5)  # Wait for the application to fully load

def main():
    # 1. Generate runtime date and time strings
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    
    # 2. Open Chrome and fetch data
    open_spotlight_and_launch('Google Chrome')
    
    # Open a new tab to ensure a clean browser state
    pyautogui.hotkey('command', 't')
    time.sleep(1)
    
    # Navigate to a plain-text weather API for reliable data copying
    pyautogui.typewrite('https://wttr.in/Bangalore?format=3')
    pyautogui.press('enter')
    time.sleep(4)  # Wait for the page to load
    
    # Select all text and copy to clipboard
    pyautogui.hotkey('command', 'a', interval=0.1)
    time.sleep(0.5)
    pyautogui.hotkey('command', 'c', interval=0.1)
    time.sleep(0.5)
    
    fetched_data = pyperclip.paste()
    comment = "Good weather for outdoor activities."
    
    # 3. Open Microsoft Excel
    open_spotlight_and_launch('Microsoft Excel')
    
    # Open a new workbook
    pyautogui.hotkey('command', 'n',interval=0.1)
    time.sleep(3)
    
    # 4. Write data to the spreadsheet
    pyautogui.typewrite(current_datetime)
    pyautogui.press('tab')
    time.sleep(0.5)
    
    pyautogui.typewrite(fetched_data)
    pyautogui.press('tab')
    time.sleep(0.5)
    
    pyautogui.typewrite(comment)
    pyautogui.press('enter')
    time.sleep(1)
    
    # 5. Save the Excel file
    filename = f"daily_report_{current_date}.xlsx"
    pyautogui.hotkey('command', 's',interval=0.1)
    time.sleep(2)
    
    # macOS shortcut to force the save location to the Desktop
    pyautogui.hotkey('command', 'shift', 'd', interval=0.1)
    time.sleep(1)
    
    pyautogui.typewrite(filename)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2)
    
    # Handle the overwrite prompt if a file with the same name already exists
    pyautogui.press('enter')
    time.sleep(1)
    
    # 6. Take and save a screenshot of the final sheet
    screenshot_filename = f"screenshot_{current_date}.png"
    pyautogui.screenshot(screenshot_filename)
    
    print(f"Report generated successfully: {filename}")
    print(f"Screenshot saved: {screenshot_filename}")

if __name__ == "__main__":
    # Give the user a moment to take their hands off the keyboard/mouse
    time.sleep(3) 
    main()