import os
import time
from PIL import ImageGrab

def take_screenshot():
    screenshot = ImageGrab.grab()
    screenshots_folder = "скриншоты"
    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)
    screenshot_path = os.path.join(screenshots_folder, f"screenshot_{int(time.time())}.png")
    screenshot.save(screenshot_path)

def read_duration_from_file(filename):
    with open(filename, 'r') as file:
        duration = int(file.read().strip())
    return duration

def main():
    duration_file = "длительность.txt"
    
    while True:
        duration = read_duration_from_file(duration_file)
        take_screenshot()
        time.sleep(duration)

if __name__ == "__main__":
    main()