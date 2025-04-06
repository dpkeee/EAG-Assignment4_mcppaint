import pyautogui
import time
import subprocess

# Step 1: Launch Paint
subprocess.Popen('mspaint')
time.sleep(2)

# Step 2: Select Rectangle Tool (adjust coordinates for your system!)
# Move to the rectangle tool in the toolbar
pyautogui.moveTo(842, 146)  # Example position of the rectangle tool
pyautogui.click()
time.sleep(0.5)

# Step 3: Draw a rectangle on canvas
# Move to the starting point of the rectangle
pyautogui.moveTo(800, 500)  # Starting point
pyautogui.mouseDown()  # Press down the mouse button to start drawing
time.sleep(0.1)  # Short delay to ensure the mouse is down

# Move to the end point of the rectangle
pyautogui.moveTo(1500, 400)  # End point
pyautogui.mouseUp()  # Release the mouse button to finish drawing

# Optional: Click again to finalize the rectangle (if needed)
# time.sleep(0.1)  # Wait a moment
# pyautogui.click()  # Click to finalize the rectangle