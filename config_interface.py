import cv2
import mediapipe as mp
import time
import numpy as np
import pyautogui
import HandTrackingModule as htm
import autopy
import tkinter as tk
from tkinter import colorchooser

# Initialize MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Initialize hand tracker from HandTrackingModule
detector = htm.handDetector(maxHands=2, detectionCon=0.85, trackCon=0.8)

# Initialize hand tracker
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7)

# Function to calculate distance between two points
def calculateIntDistance(pt1, pt2):
    return int(((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5)

# Creating keys
class Key:
    def __init__(self, x, y, w, h, text, special_characters=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.special_characters = special_characters
        self.start_time = 0
        self.pressed = False

    def drawKey(self, img, text_color=(255, 255, 255), bg_color=(0, 0, 0), pressed_color=(0, 255, 0),
                alpha=0.5, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, thickness=2):
        # Draw the key box
        bg_rec = img[self.y: self.y + self.h, self.x: self.x + self.w]
        if bg_rec.shape[0] == 0 or bg_rec.shape[1] == 0:
            return  # Skip if the region is empty

        if self.pressed:
            color = pressed_color
        else:
            color = bg_color

        # Convert color string to integers
        try:
            color_int = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5) if color[i:i + 2].isalnum())
        except ValueError:
            print(f"Invalid color format: {color}")
            return

        white_rect = np.ones(bg_rec.shape, dtype=np.uint8)
        white_rect[:] = color_int
        res = cv2.addWeighted(bg_rec, alpha, white_rect, 1 - alpha, 1.0)

        # Putting the image back to its position
        img[self.y: self.y + self.h, self.x: self.x + self.w] = res

        # Put the letter
        text_size = cv2.getTextSize(self.text, fontFace, fontScale, thickness)
        text_pos = (int(self.x + self.w // 2 - text_size[0][0] // 2),
                    int(self.y + self.h // 2 + text_size[0][1] // 2))
        cv2.putText(img, self.text, text_pos, fontFace, fontScale, text_color, thickness)

        # Put special characters
        if self.special_characters:
            char_size = cv2.getTextSize(self.special_characters, fontFace, fontScale / 2, thickness)
            char_pos = (int(self.x + self.w // 2 - char_size[0][0] // 2),
                        int(self.y + self.h // 2 - text_size[0][1] // 2 - 5))
            cv2.putText(img, self.special_characters, char_pos, fontFace, fontScale / 2, text_color, thickness)

        # Put special characters
        if self.special_characters:
            char_size = cv2.getTextSize(self.special_characters, fontFace, fontScale / 2, thickness)
            char_pos = (int(self.x + self.w // 2 - char_size[0][0] // 2),
                        int(self.y + self.h // 2 - text_size[0][1] // 2 - 5))
            cv2.putText(img, self.special_characters, char_pos, fontFace, fontScale / 2, text_color, thickness)

        # Put special characters
        if self.special_characters:
            char_size = cv2.getTextSize(self.special_characters, fontFace, fontScale / 2, thickness)
            char_pos = (int(self.x + self.w // 2 - char_size[0][0] // 2),
                        int(self.y + self.h // 2 - text_size[0][1] // 2 - 5))
            cv2.putText(img, self.special_characters, char_pos, fontFace, fontScale / 2, text_color, thickness)

    def isOver(self, x, y):
        if (self.x + self.w > x > self.x) and (self.y + self.h > y > self.y):
            return True
        return False

# Create keys
w, h = 80, 60
startX, startY = 100, 100  # Adjusted for starting placement

# Rows of keys
rows = [
    "1234567890",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm"
]

keys = []

for i, row in enumerate(rows):
    row_len = len(row)
    for j, char in enumerate(row):
        x = startX + (w + 5) * j
        y = startY + (h + 5) * i
        special_characters = None
        if i == 0 and j < 10:
            special_characters = "!@#$%^&*()"[j]
        keys.append(Key(x, y, w, h, char, special_characters))

keys.append(Key(startX + 770, startY + 195, w, h, "Caps"))
keys.append(Key(startX + 0, startY + 260, 140, h, "Win"))
keys.append(Key(startX + 150, startY + 260, 440, h, "Space"))
keys.append(Key(startX + 9 * w + 50, startY + 2 * h + 10, w, h, ","))
keys.append(Key(startX + 600, startY + 260, 2 * w, h, "<--"))
keys.append(Key(startX + 600, startY + 195, 2 * w, h, "Enter"))
keys.append(Key(startX + 770, startY + 260, w, h, "DEL"))

showKey = Key(300, 5, 80, 50, 'Show')
exitKey = Key(300, 65, 80, 50, 'Exit')
textBox = Key(startX, startY - h - 5, 10 * w + 9 * 5, h, '')

# Define the rectangle box parameters
rectangle_x, rectangle_y, rectangle_width, rectangle_height = 970, 40, 950, 1030

# Create a simple GUI
class VirtualPeripheralGUI:
    def __init__(self, root, cap):
        self.root = root
        self.cap = cap  # Pass the cap variable
        self.keyboard_color_str = "#000000"  # Initialize with default color

        self.root.title("Virtual Peripherals")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Default colors
        self.keyboard_color = (0, 0, 0)  # Default keyboard color
        self.rectangle_color = (255, 255, 255)  # Default rectangle color

        # Keyboard color
        self.keyboard_color_label = tk.Label(root, text="Choose Keyboard Color:")
        self.keyboard_color_label.pack(pady=10)

        self.keyboard_color_button = tk.Button(root, text="Choose Color", command=self.choose_keyboard_color)
        self.keyboard_color_button.pack(pady=5)

        # Rectangle box (mouse) color
        self.rectangle_color_label = tk.Label(root, text="Choose Rectangle Box (Mouse) Color:")
        self.rectangle_color_label.pack(pady=10)

        self.rectangle_color_button = tk.Button(root, text="Choose Color", command=self.choose_rectangle_color)
        self.rectangle_color_button.pack(pady=5)

        # Camera selection
        self.camera_label = tk.Label(root, text="Select Camera:")
        self.camera_label.pack(pady=10)

        self.camera_var = tk.StringVar()
        self.camera_var.set("Default Camera")  # Default camera option
        self.camera_dropdown = tk.OptionMenu(root, self.camera_var, "Default Camera", "Camera 1", "Camera 2")
        self.camera_dropdown.pack(pady=5)

        # Start button
        self.start_button = tk.Button(root, text="Start", command=self.start_camera)
        self.start_button.pack(pady=20)

        # Loading bar
        self.loading_var = tk.DoubleVar()
        self.loading_bar = tk.Scale(root, from_=0, to=100, variable=self.loading_var, orient="horizontal", length=300)
        self.loading_bar.pack(pady=20)

    def choose_keyboard_color(self):
        color = colorchooser.askcolor(title="Choose Keyboard Color")[0]
        if color:
            self.keyboard_color = tuple(map(int, color))
            for k in keys:
                k.drawKey(image, bg_color=self.keyboard_color)
            self.root.update()

    def choose_rectangle_color(self):
        color = colorchooser.askcolor(title="Choose Rectangle Box (Mouse) Color")[0]
        self.rectangle_color = tuple(map(int, color))
        cv2.rectangle(image, (rectangle_x, rectangle_y),
                      (rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                      self.rectangle_color, 2)
        self.root.update()

    def start_camera(self):
        self.root.destroy()  # Close the GUI
        self.initialize_camera()

    def initialize_camera(self):
        # Main loop
        while self.cap.isOpened():  # Use self.cap instead of cap
            success, image = self.cap.read()  # Use self.cap instead of cap
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

                    # Get the index fingertip location
                    index_tip = (
                        int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image.shape[1]),
                        int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image.shape[0]))

                    # Check if index is over a key
                    for k in keys:
                        if k.isOver(index_tip[0], index_tip[1]):
                            k.pressed = True
                            if k.start_time == 0:
                                k.start_time = time.time()
                            elif time.time() - k.start_time > 1:
                                print(f"Pressed key: {k.text}")
                                if k.text == '<--':
                                    # Backspace functionality
                                    pyautogui.press('backspace')
                                    if len(textBox.text) > 0:
                                        textBox.text = textBox.text[:-1]
                                elif k.text == 'Space':
                                    # Space functionality
                                    pyautogui.press('space')
                                    textBox.text += " "
                                elif k.text == ',':
                                    # Comma functionality
                                    pyautogui.press(',')
                                    textBox.text += ","
                                elif k.text == 'Caps':
                                    # Caps Lock functionality
                                    caps_lock_on = not caps_lock_on
                                elif k.text == 'Win':
                                    # Windows key functionality (for example, open the Start menu)
                                    pyautogui.hotkey('winleft')
                                elif k.text == 'Enter':
                                    # Enter key functionality
                                    pyautogui.press('enter')
                                    textBox.text += "\n"  # Add a new line to the text box
                                elif k.text == 'DEL':
                                    # Delete key functionality
                                    pyautogui.press('delete')
                                    if len(textBox.text) > 0:
                                        textBox.text = textBox.text[:-1]
                                else:
                                    if caps_lock_on and (k.text.isalpha() or k.special_characters):
                                        # When Caps Lock is ON and the key is alphabetic or has special characters, print in uppercase
                                        pyautogui.press(k.special_characters if k.special_characters else k.text.upper())
                                        textBox.text += k.special_characters if k.special_characters else k.text.upper()
                                    elif not caps_lock_on and k.text.isalpha():
                                        # When Caps Lock is OFF and the key is alphabetic, print in lowercase
                                        pyautogui.press(k.text.lower())
                                        textBox.text += k.text.lower()
                                    elif not caps_lock_on and k.text.isnumeric():
                                        # When Caps Lock is OFF and the key is numeric, print as it is
                                        pyautogui.write(k.text)
                                        textBox.text += k.text

                                k.start_time = 0
                        else:
                            k.pressed = False
                            k.start_time = 0

                # Draw virtual keyboard
                for k in keys:
                    k.drawKey(image, bg_color=self.keyboard_color)

                # Draw text box
                textBox.drawKey(image)

                # Draw Caps Lock status
                caps_status = "ON" if caps_lock_on else "OFF"
                cv2.putText(image, f"Caps Lock: {caps_status}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),
                            2)

                # Draw the rectangle box
                cv2.rectangle(image, (rectangle_x, rectangle_y),
                              (rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                              self.rectangle_color, 2)

                # Hand tracking for mouse control
                img = detector.findHands(image)
                lmList = detector.findPosition(img, draw=False)

                if lmList:
                    # Get the tip of the index finger
                    x, y = lmList[8][1], lmList[8][2]

                    # Get screen dimensions
                    screen_width, screen_height = autopy.screen.size()

                    # Set bounds for x and y coordinates
                    x = max(0, min(x, screen_width - 1))
                    y = max(0, min(y, screen_height - 1))

                    # Move the mouse
                    autopy.mouse.move(x, y)

                # Show the image with both virtual keyboard and hand tracking
                image = cv2.resize(image, (1920, 1080))
                cv2.imshow('Virtual Keyboard', image)

                # Check for key press to exit
                pressed_key = cv2.waitKey(1)
                if pressed_key == 27:  # 27 corresponds to the ESC key
                    break

                # Update the loading bar
                self.loading_var.set(self.loading_var.get() + 1)
                self.root.update()

# Open camera
cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Set width
cap.set(4, 1080)  # Set height

# Create the GUI window
root = tk.Tk()
app = VirtualPeripheralGUI(root, cap)
root.mainloop()