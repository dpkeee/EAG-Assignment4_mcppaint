import pyautogui
import time

print("Move your mouse over the Rectangle tool...")

try:
    while True:
        x, y = pyautogui.position()
        print(f"Mouse position: ({x}, {y})", end='\r')  # Overwrites the same line
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nDone.") 