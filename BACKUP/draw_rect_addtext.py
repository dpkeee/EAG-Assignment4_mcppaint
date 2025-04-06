import pyautogui
import time
import subprocess

# Step 1: Launch Paint
subprocess.Popen('mspaint')
time.sleep(2)

# Step 2: Select Rectangle Tool (adjust coordinates for your system!)
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

# Step 4: Select Text Tool
time.sleep(0.5)  # Wait for the rectangle to be drawn
pyautogui.moveTo(565, 155)  # Adjust coordinates for the text tool
pyautogui.click()  # Click to select the text tool
time.sleep(0.5)

# Step 5: Click inside the rectangle to place the text box
pyautogui.moveTo(1000, 450)  # Adjust to a position inside the rectangle
pyautogui.click()  # Click to place the text box
time.sleep(0.5)

# Step 6: Type the text "hello"
pyautogui.typewrite("hello")  # Type the text inside the rectangle
pyautogui