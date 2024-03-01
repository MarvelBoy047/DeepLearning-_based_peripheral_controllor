import cv2
import mediapipe as mp
import time
import numpy as np
import pyautogui
import HandTrackingModule as htm
import autopy

# Color choice variables
keyboard_color = (0, 0, 0)  # Keyboard color (default: black)
rectangle_color = (128, 0, 128)  # Rectangle box color (default: purple)
clicked_key_color = (0, 255, 0)  # Clicked (interacted) key color (default: green)

# parameters
cam = cv2.VideoCapture(0)


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

# Define the virtual keyboard
ctime = time.time()  # Define ctime here

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

    def drawKey(self, img, text_color=(255, 255, 255), bg_color=keyboard_color, pressed_color=clicked_key_color,
                alpha=0.5, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, thickness=2):
        # Draw the key box
        bg_rec = img[self.y: self.y + self.h, self.x: self.x + self.w]
        if bg_rec.shape[0] == 0 or bg_rec.shape[1] == 0:
            return  # Skip if the region is empty

        if self.pressed:
            color = pressed_color
        else:
            color = bg_color

        white_rect = np.ones(bg_rec.shape, dtype=np.uint8)
        white_rect[:] = color
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
keys.append(Key(startX+150, startY+260, 440, h, "Space"))
keys.append(Key(startX+9*w + 50, startY+2*h+10, w, h, ","))
keys.append(Key(startX+600, startY+260, 2*w, h, "<--"))
keys.append(Key(startX+600, startY+ 195, 2*w, h, "Enter"))
keys.append(Key(startX+770, startY+260, w, h, "DEL"))

showKey = Key(300,5,80,50, 'Show')
exitKey = Key(300,65,80,50, 'Exit')
textBox = Key(startX, startY-h-5, 10*w+9*5, h, '')

# Define the rectangle box parameters
rectangle_x, rectangle_y, rectangle_width, rectangle_height = 970, 40, 950, 1030

# Open camera
cap = cam

caps_lock_on = False

# Main loop
def main():
    caps_lock_on = False  # Move this line inside the main function

    while cap.isOpened():
        success, image = cap.read()
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
            k.drawKey(image)

        # Draw text box
        textBox.drawKey(image)

        # Draw Caps Lock status
        caps_status = "ON" if caps_lock_on else "OFF"
        cv2.putText(image, f"Caps Lock: {caps_status}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Draw the rectangle box
        cv2.rectangle(image, (rectangle_x, rectangle_y),
                      (rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                      rectangle_color, 2)

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

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()