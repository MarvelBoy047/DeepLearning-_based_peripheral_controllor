# DeepLearning-_based_peripheral_controllor

## Virtual Keyboard with Hand Tracking
## Use python-v3.8
This project implements a virtual keyboard controlled by hand gestures using a webcam. Users can interact with the virtual keyboard by hovering their index finger over the keys and performing various actions such as typing, deleting, and pressing special keys.

### Setup Instructions

1. Install the required libraries:
   ```bash
   pip install opencv-python mediapipe pyautogui autopy
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repository.git
   ```

3. Navigate to the project directory:
   ```bash
   cd your-repository
   ```

4. Run the main script:
   ```bash
   python main_script.py
   ```

### Features

- **Virtual Keyboard**: The virtual keyboard is displayed on the screen.
- **Hand Tracking**: Hand gestures are detected using the MediaPipe library.
- **Typing**: Users can type by hovering their index finger over the keys.
- **Deleting**: The backspace key allows users to delete characters.
- **Special Keys**: Special keys such as Caps Lock, Enter, Space, and Delete are supported.
- **Caps Lock**: Users can toggle Caps Lock on and off.
- **Mouse Control**: Hand gestures can also control the mouse cursor on the screen.

### Files

1. **main_script.py**: Contains the main functionality of the virtual keyboard and hand tracking.
2. **HandTrackingModule.py**: Provides a class for hand detection and tracking using MediaPipe.
3. **profile_memory.py**: Profiles memory usage of the main script and displays memory usage over time.

### Usage

1. Run the `main_script.py` file to start the virtual keyboard.
2. Use your index finger to hover over the keys and perform actions.
3. Press the 'ESC' key to exit the program.

### Memory Profiling

The `profile_memory.py` script profiles memory usage of the main script over time and displays memory usage graphs segmented into three segments.

### Notes

- Ensure proper lighting conditions for optimal hand tracking.
- Adjust the webcam position to capture hand movements accurately.
