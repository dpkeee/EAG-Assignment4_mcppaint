# example2-3.py

# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
from pywinauto.application import Application
import win32gui
import win32con
import time
from win32api import GetSystemMetrics
import pyautogui
import smtplib
import json
import subprocess

# Instantiate an MCP server client
mcp = FastMCP("Calculator")

# Global variable for Paint application
paint_app = None

# DEFINE TOOLS

# Addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

# Subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# Multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

# Division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# Power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# Square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# Cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# Factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """Factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# Log tool
@mcp.tool()
def log(a: int) -> float:
    """Log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# Remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """Remainder of two numbers division"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# Trigonometric tools
@mcp.tool()
def sin(a: int) -> float:
    """Sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

@mcp.tool()
def cos(a: int) -> float:
    """Cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

@mcp.tool()
def tan(a: int) -> float:
    """Tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint maximized on my monitor"""
    global paint_app
    try:
        paint_app = Application().start('mspaint.exe')
        time.sleep(2)
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get primary monitor width
        primary_width = GetSystemMetrics(0)
        
        # First move to secondary monitor without specifying size
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_TOP,
            primary_width + 1, 0,  # Position it on secondary monitor
            0, 0,  # Let Windows handle the size
            win32con.SWP_NOSIZE  # Don't change the size
        )
        
        # Now maximize the window
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(0.2)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Paint opened successfully and maximized"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }
# DEFINE RESOURCES

# Draw rectangle tool
@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }

        # Get the Paint window
        paint_window = win32gui.FindWindow(None, "Untitled - Paint")
        if paint_window:
            win32gui.ShowWindow(paint_window, win32con.SW_MAXIMIZE)
            win32gui.SetForegroundWindow(paint_window)
        else:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint window not found."
                    )
                ]
            }

        time.sleep(1)  # Wait for the window to be ready

        # Move to the rectangle tool in the toolbar
        pyautogui.moveTo(842, 146)
        pyautogui.click()
        time.sleep(0.5)

        # Draw the rectangle
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        time.sleep(0.1)
        pyautogui.moveTo(x2, y2)
        pyautogui.mouseUp()

        return {
            "content": [
                TextContent(
                    type="text",
                    text="Rectangle drawn successfully."
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }

# Email sending tool
@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email"""
    print("CALLED: send_email(to: str, subject: str, body: str) -> dict:")
    
    # Load email configuration from JSON file
    with open('config.json') as config_file:
        config = json.load(config_file)
    
    email = config['email']
    password = config['password']
    
    # Create the email headers
    message = f"Subject: {subject}\n\n{body}"  # Format the email with subject and body
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, to, message)  # Send the email with the formatted message
    server.quit()
    
    return {
        "content": [
            TextContent(
                type="text",
                text="Email sent successfully"
            )
        ]
    }

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"

# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
