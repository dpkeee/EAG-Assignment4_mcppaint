import win32gui
import win32con
import win32api
import subprocess
import time

def activate_paint():
    """Open and activate MS Paint window."""
    try:
        paint_hwnd = win32gui.FindWindow("MSPaintApp", None)
        if not paint_hwnd:
            subprocess.Popen('mspaint')
            time.sleep(2)  # Wait for Paint to open
            paint_hwnd = win32gui.FindWindow("MSPaintApp", None)
        
        if not paint_hwnd:
            raise Exception("Paint window not found")
            
        win32gui.ShowWindow(paint_hwnd, win32con.SW_MAXIMIZE)
        win32gui.SetForegroundWindow(paint_hwnd)
        time.sleep(0.5)
        return paint_hwnd
        
    except Exception as e:
        print(f"Paint activation failed: {e}")
        return None

def select_rectangle_tool():
    """Select rectangle tool using specific coordinates."""
    try:
        # Coordinates for the rectangle tool
        rectangle_tool_x = 3719
        rectangle_tool_y = 222

        # Move to the rectangle tool position
        win32api.SetCursorPos((rectangle_tool_x, rectangle_tool_y))
        time.sleep(0.2)

        print("clicked")

        return True

    except Exception as e:
        print(f"Tool selection failed: {e}")
        return False

def draw_rectangle(start_x, start_y, end_x, end_y):
    """Simulate mouse drawing of rectangle."""
    try:
        # Move to start position
        win32api.SetCursorPos((start_x, start_y))
        time.sleep(0.2)
        
        # Left mouse down
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, start_x, start_y, 0, 0)
        time.sleep(0.2)
        
        # Drag to end position
        win32api.SetCursorPos((end_x, end_y))
        time.sleep(0.2)
        
        # Left mouse up
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, end_x, end_y, 0, 0)
        time.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"Drawing failed: {e}")
        return False

if __name__ == "__main__":
    # 1. Open and activate Paint
    paint_hwnd = activate_paint()
    if not paint_hwnd:
        exit(1)
    
    # 2. Get canvas area (approximate coordinates)
    canvas_rect = win32gui.GetWindowRect(paint_hwnd)
    canvas_x = canvas_rect[0] + 50  # Offset for UI elements
    canvas_y = canvas_rect[1] + 100
    
    # 3. Select rectangle tool using specified coordinates
    if not select_rectangle_tool():
        exit(1)
    
    # 4. Draw rectangle (200x150 pixels)
    start_x = canvas_x + 100
    start_y = canvas_y + 100
    end_x = start_x + 200
    end_y = start_y + 150
    
    # draw_rectangle(start_x, start_y, end_x, end_y)
    # print(f"Rectangle drawn from ({start_x},{start_y}) to ({end_x},{end_y})")
    draw_rectest()
    
    def draw_rectest():
        #async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    #print("CALLED: draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:")
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
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(1)  # Allow time for the window to focus
        
        print(f"Drawing rectangle from ({600}, {500}) to ({1000}, {700})")
        x1 = 600
        y1 = 500
        x2 = 1000
        y2 = 700
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        canvas.click_input(coords=(3719, 222))
        # Draw rectangles
        print("Pressing mouse input")
        canvas.press_mouse_input(coords=(x1 + 100, y1))
        time.sleep(1)  # Allow time for the action to complete
        
        print("Moving mouse input")
        canvas.move_mouse_input(coords=(x2 + 100, y2))
        time.sleep(1)  # Allow time for the action to complete
        
        print("Releasing mouse input")
        canvas.release_mouse_input(coords=(x2 + 1000, y2))
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }


