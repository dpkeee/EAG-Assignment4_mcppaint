import win32gui
import win32api
import win32con
import subprocess
import time

def open_paint():
    """Launch Microsoft Paint"""
    try:
        subprocess.Popen(['mspaint'])
        time.sleep(2)  # Wait for Paint to open
        return True
    except Exception as e:
        print(f"Failed to open Paint: {e}")
        return False

def find_paint_window():
    """Find Paint window handle"""
    hwnd = win32gui.FindWindow("MSPaintApp", None)
    if not hwnd:
        print("Paint window not found")
        return None
    return hwnd

def draw_rectangle(hwnd, x1, y1, x2, y2):
    """Draw rectangle on Paint canvas"""
    # Get device context
    hdc = win32gui.GetDC(hwnd)
    
    # Create pen (color: red, thickness: 2)
    pen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(255, 0, 0))
    old_pen = win32gui.SelectObject(hdc, pen)
    
    # Draw rectangle
    win32gui.Rectangle(hdc, x1, y1, x2, y2)
    
    # Clean up
    win32gui.SelectObject(hdc, old_pen)
    win32gui.DeleteObject(pen)
    win32gui.ReleaseDC(hwnd, hdc)

if __name__ == "__main__":
    # Open Paint
    if not open_paint():
        exit(1)
    
    # Find window
    paint_hwnd = find_paint_window()
    if not paint_hwnd:
        exit(1)
    
    # Bring to foreground
    win32gui.SetForegroundWindow(paint_hwnd)
    time.sleep(0.5)
    
    # Draw rectangle (coordinates relative to Paint canvas)
    draw_rectangle(paint_hwnd, 600, 500, 1000, 700)
    print("Rectangle drawn in Paint")
