import time
import pyautogui
import pickle
from pynput import mouse, keyboard
from threading import Thread

# Variables to store recorded actions
recorded_actions = []
is_recording = False
is_replaying = False

# Remove all delays between actions
pyautogui.PAUSE = 0

# Function to record mouse movements and clicks
def on_move(x, y):
    if is_recording:
        recorded_actions.append(('move', x, y, time.time()))

def on_click(x, y, button, pressed):
    if is_recording and pressed:
        recorded_actions.append(('click', x, y, button, time.time()))

# Function to replay recorded actions (with accurate timing and endless loop)
def replay_actions():
    global is_replaying
    is_replaying = True

    if not recorded_actions:
        return

    while is_replaying:  # Loop endlessly until is_replaying is False
        start_time = time.time()
        first_action_time = recorded_actions[0][-1]
        initial_delay = max(0, first_action_time - start_time)  # Ensure non-negative delay

        time.sleep(initial_delay)  # Wait for the first action

        for i in range(len(recorded_actions)):
            if not is_replaying:
                break

            action = recorded_actions[i]
            action_type = action[0]

            # Calculate the time difference between this action and the next
            if i < len(recorded_actions) - 1:
                next_action_time = recorded_actions[i + 1][-1]
                time_difference = next_action_time - action[-1]
            else:
                time_difference = 0  # No delay after the last action

            # Perform the action
            if action_type == 'move':
                pyautogui.moveTo(action[1], action[2])
            elif action_type == 'click':
                pyautogui.click(x=action[1], y=action[2], button=str(action[3]).split('.')[-1])

            # Wait for the correct time before the next action
            time.sleep(time_difference)

# Function to handle hotkeys
def on_press(key):
    global is_recording, is_replaying, recorded_actions

    try:
        if key.char == 'r':  # Start recording
            recorded_actions.clear()
            is_recording = True
            print("Recording started...")
        elif key.char == 's':  # Stop recording
            is_recording = False
            print("Recording stopped.")
        elif key.char == 'p':  # Start replaying
            if recorded_actions:
                print("Replaying...")
                replay_thread = Thread(target=replay_actions)
                replay_thread.start()
            else:
                print("No actions recorded.")
        elif key.char == 'l':  # Load recording from file
            try:
                with open("mouse_recording.pkl", "rb") as file:
                    recorded_actions = pickle.load(file)
                print("Recording loaded.")
            except FileNotFoundError:
                print("No recording found. Record something first!")
        elif key.char == 'w':  # Save recording to file
            with open("mouse_recording.pkl", "wb") as file:
                pickle.dump(recorded_actions, file)
            print("Recording saved.")
    except AttributeError:
        if key == keyboard.Key.esc:  # Stop replay without exiting
            is_replaying = False
            print("Replay stopped.")

# Start the program
print("Press 'R' to start recording, 'S' to stop recording, 'P' to replay, 'L' to load, 'W' to save, and 'Esc' to stop replay.")

# Start mouse listener
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
mouse_listener.start()

# Start keyboard listener
with keyboard.Listener(on_press=on_press) as keyboard_listener:
    keyboard_listener.join()

mouse_listener.stop()