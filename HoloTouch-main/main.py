import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import random
from util import get_angle, get_distance
from pynput.mouse import Button, Controller
mouse = Controller()
import math
from pynput.keyboard import Controller as KeyboardController, Key
keyboard = KeyboardController()
import time


# Get screen dimensions with pyautogui
screen_width, screen_height = pyautogui.size()
print(screen_width, screen_height)

# Cam dimensions
cam_width = 640
cam_height = 480

# For bounding box
frame_red = 100 # Frame reduction

# Initializing model
mpHands = mp.solutions.hands
# Setting up model
hands = mpHands.Hands(
    static_image_mode=False, # False b/c we are capturing a video
    model_complexity=1,  #
    min_detection_confidence=0.7,# 70% confidence required
    min_tracking_confidence=0.7, # 70% confidence required
    max_num_hands=1 # Only one hand being detected
)

# Function for finding the tip of a finger
def find_finger_tip(processed):
    # if processed
    if processed.multi_hand_landmarks:
        # Take the landmarks from one of the hands
        hand_landmarks = processed.multi_hand_landmarks[0]  # Assuming only one hand is detected
        # Get the index finger tip and store (x,y coord)
        index_finger_tip = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
        # Return the index
        return index_finger_tip
    # Return none if no processed landmark action
    return None, None


# Function to move mouse
# Using pyautogui API
def move_mouse(index_finger_tip):
    # If index finger tip exists
    if index_finger_tip is not None:
        # Get x and y values related to screen width
        # Mediapipe knows these screen dimensions
        x = int(index_finger_tip.x * (screen_width))
        y = int(index_finger_tip.y * (screen_height))

        #x = int(index_finger_tip.x * 1920)
        #y = int(index_finger_tip.y * 640)
        # Move our mouse to this XY coordinate of index finger tip
        pyautogui.moveTo(x, y)

def is_move_cursor(landmark_list):
    return(
        get_distance([landmark_list[4], landmark_list[5]]) < 50 and  # Thumb condition
        get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90 and  # Index finger bent
        get_angle(landmark_list[13], landmark_list[14], landmark_list[16]) < 50 and  # Ring finger bent
        get_angle(landmark_list[17], landmark_list[18], landmark_list[20]) < 50  # Pinky finger bent
    )



# Function that check left click conditions and returns true or false
def is_left_click(landmark_list, thumb_index_dist):
    return (
        # Index finger bent
        get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
        # Middle finger straight
        get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) > 90 and
        # Ring finger bent
        get_angle(landmark_list[13], landmark_list[14], landmark_list[16]) < 50 and
        # Pinky finger bent
        get_angle(landmark_list[17], landmark_list[18], landmark_list[20]) < 50 and
        # Thumb straight based on distance
        thumb_index_dist > 50
    )

# Function that check right click conditions and returns true or false
def is_right_click(landmark_list, thumb_index_dist):
    return (
        # Middle finger bent
        get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
        # Index finger straight
        get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90 and
        # Ring finger bent
        get_angle(landmark_list[13], landmark_list[14], landmark_list[16]) < 50 and
        # Pinky finger bent
        get_angle(landmark_list[17], landmark_list[18], landmark_list[20]) < 50 and
        # Thumb straight based on distance
        thumb_index_dist > 50
    )

# Function that check double click conditions and returns true or false
def is_double_click(landmark_list, thumb_index_dist):
    return (
        # Checks if index finger is straight AND middle finger is straight AND thumb is straight
        get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 < thumb_index_dist and
        get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50
    )

# Function that check screenshot conditions and returns true or false
def is_screenshot(landmark_list, thumb_index_dist):
    return (
        # Checks if all are down (index, thumb, middle)
        get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
        get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
        thumb_index_dist < 50
    )

# Function that check left click conditions and returns true or false
def is_press_enter(landmark_list):
    # Check angles for the pinky (bent) and other fingers (straight)
    pinky_bent = get_angle(landmark_list[17], landmark_list[18], landmark_list[20]) < 50
    index_straight = get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 160
    middle_straight = get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) > 160
    ring_straight = get_angle(landmark_list[13], landmark_list[14], landmark_list[16]) > 160
    thumb_straight = get_angle(landmark_list[1], landmark_list[2], landmark_list[4]) > 160

    return pinky_bent and index_straight and middle_straight and ring_straight and thumb_straight


# Function that check left click conditions and returns true or false
def is_open_tab(landmark_list):
    # Check angles for the pinky (bent) and other fingers (straight)
    pinky_bent = get_angle(landmark_list[17], landmark_list[18], landmark_list[20]) < 50
    index_straight = get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 160
    middle_straight = get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) > 160
    ring_straight = get_angle(landmark_list[13], landmark_list[14], landmark_list[16]) > 160
    thumb_straight = get_angle(landmark_list[1], landmark_list[2], landmark_list[4]) > 160

    return pinky_bent and index_straight and middle_straight and ring_straight and thumb_straight


# FOR GOOGLE EARTH ZOOM
def is_keyboard_open(landmark_list, threshold=50):
    pinky_tip = landmark_list[mpHands.HandLandmark.INDEX_FINGER_TIP.value]
    thumb_tip = landmark_list[mpHands.HandLandmark.THUMB_TIP.value]

    # Calculate the distance between pinky tip and thumb tip
    distance = get_distance([pinky_tip, thumb_tip])

    # Check if the distance is within the threshold
    return distance < threshold

# FOR GOOGLE EARTH ZOOM
def zoom_control_pointer_thumb(landmark_list):
    # Check if pointer and thumb are touching
    is_touching = is_keyboard_open(landmark_list)

    if is_touching:
        # Zoom out when pinky and thumb touch
        pyautogui.scroll(-2)  # Adjust scroll value for sensitivity
        print("Keyobard open")

    # Update and return the current state
    return is_touching



# FOR CHROME SCROLL and GOOGLE EARTH ZOOM ############################
def is_thumb_middle_touching(landmark_list, threshold=50):
    middle_tip = landmark_list[mpHands.HandLandmark.MIDDLE_FINGER_TIP.value]
    thumb_tip = landmark_list[mpHands.HandLandmark.THUMB_TIP.value]

    # Calculate the distance between middle finger tip and thumb tip
    distance = get_distance([middle_tip, thumb_tip])

    # Check if the distance is within the threshold
    return distance < threshold

def is_thumb_middle_apart(landmark_list, threshold=80, threshold2=150):
    middle_tip = landmark_list[mpHands.HandLandmark.MIDDLE_FINGER_TIP.value]
    thumb_tip = landmark_list[mpHands.HandLandmark.THUMB_TIP.value]

    # Calculate the distance between middle finger tip and thumb tip
    distance = get_distance([middle_tip, thumb_tip])

    # Check if the distance is within the threshold
    return threshold < distance < threshold2


def zoom_control_thumb_middle(landmark_list):
    # Check if thumb and middle finger are touching
    is_touching = is_thumb_middle_touching(landmark_list)
    is_apart = is_thumb_middle_apart(landmark_list)

    if is_touching:
        # Zoom out when thumb and middle finger touch
        pyautogui.scroll(-30)  # Adjust scroll value for sensitivity
        print("Scroll Down")
    elif is_apart:
        # Zoom in when thumb and middle finger are not touching
        pyautogui.scroll(30)  # Adjust scroll value for sensitivity
        print("Scroll Up")

    # Update and return the current state
    return is_touching


# ROTATE ######################################
def is_rotate_gesture(landmark_list):
    # Check angles for all fingers (except the ring finger) being straight (angle > 160 degrees)
    thumb_angle = get_angle(landmark_list[1], landmark_list[2], landmark_list[4])
    index_finger_angle = get_angle(landmark_list[5], landmark_list[6], landmark_list[8])
    middle_finger_angle = get_angle(landmark_list[9], landmark_list[10], landmark_list[12])
    pinky_angle = get_angle(landmark_list[17], landmark_list[18], landmark_list[20])

    # Check if the ring finger is bent (angle < 90 degrees)
    ring_finger_angle = get_angle(landmark_list[13], landmark_list[14], landmark_list[16])

    # If all other fingers are straight, and ring finger is bent, return True for rotate gesture
    return (
                thumb_angle > 160 and index_finger_angle > 160 and middle_finger_angle > 160 and pinky_angle > 160 and ring_finger_angle < 90)


def detect_hand_rotation(landmark_list):
    # Get the angle between thumb and index finger
    thumb_tip = landmark_list[4]  # Thumb tip
    index_tip = landmark_list[8]  # Index finger tip
    thumb_base = landmark_list[2]  # Thumb base for better rotation detection

    # Calculate angle of rotation
    delta_x = index_tip[0] - thumb_base[0]
    delta_y = index_tip[1] - thumb_base[1]
    rotation_angle = math.degrees(math.atan2(delta_y, delta_x))

    # Return the angle
    return rotation_angle


def is_pinky_on_left(landmark_list):
    # Get the coordinates for the pinky tip and index tip
    pinky_tip = landmark_list[mpHands.HandLandmark.PINKY_TIP.value]
    index_tip = landmark_list[mpHands.HandLandmark.INDEX_FINGER_TIP.value]

    # Compare x-coordinates to determine the side of the pinky
    return pinky_tip[0] < index_tip[0]  # Returns True if pinky is on the left


def smooth_rotate_with_keys(rotation_angle, hold_time=0.1):
    if rotation_angle < -30:
        keyboard.press(Key.left)
        time.sleep(hold_time)
        keyboard.release(Key.left)
        print("Rotating Left")
    elif rotation_angle > 30:
        keyboard.press(Key.right)
        time.sleep(hold_time)
        keyboard.release(Key.right)
        print("Rotating Right")
    elif -30 <= rotation_angle <= 30:
        keyboard.press(Key.up)
        time.sleep(hold_time)
        keyboard.release(Key.up)
        print("Rotating Up")

# Function to check if thumb and pinky are touching
def is_switch_window(landmark_list):
    # Checks if thumb and pinky are touching
    thumb_tip = landmark_list[mp.solutions.hands.HandLandmark.THUMB_TIP]
    pinky_tip = landmark_list[mp.solutions.hands.HandLandmark.PINKY_TIP]
    distance = get_distance([thumb_tip, pinky_tip])
    return distance < 30


# Function to check if thumb and pinky are touching
def is_switch_tab(landmark_list):
    # Checks if thumb and pinky are touching
    thumb_tip = landmark_list[mp.solutions.hands.HandLandmark.THUMB_TIP]
    ring_tip = landmark_list[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
    distance = get_distance([thumb_tip, ring_tip])
    return distance < 30


### COPY AND PASTE
def is_copy(landmark_list, threshold=50):
    # Get coordinates for index and middle finger tips
    index_tip = landmark_list[mpHands.HandLandmark.INDEX_FINGER_TIP.value]
    middle_tip = landmark_list[mpHands.HandLandmark.MIDDLE_FINGER_TIP.value]

    # Calculate the distance between index and middle finger tips
    distance = get_distance([index_tip, middle_tip])

    # Check if the distance is less than the threshold, meaning they are touching
    return distance < threshold


def are_cut_fingers_down(landmark_list):
    # Check if thumb, ring, and pinky are down (bent)
    thumb_angle = get_angle(landmark_list[4], landmark_list[3], landmark_list[2])  # Thumb bend angle
    ring_angle = get_angle(landmark_list[13], landmark_list[14], landmark_list[16])  # Ring finger bend angle
    pinky_angle = get_angle(landmark_list[17], landmark_list[18], landmark_list[20])  # Pinky finger bend angle

    # Define a threshold for bent fingers (e.g., less than 50° for bent)
    return thumb_angle > 90 and ring_angle < 50 and pinky_angle < 50



def is_fullscreen(landmark_list):
    # Check angles for the pinky (bent) and other fingers (straight)
    pinky_bent = get_angle(landmark_list[17], landmark_list[18], landmark_list[20]) >160
    index_straight = get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) <50
    middle_straight = get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) > 160
    ring_straight = get_angle(landmark_list[13], landmark_list[14], landmark_list[16]) > 160
    thumb_straight = get_angle(landmark_list[1], landmark_list[2], landmark_list[4]) > 160

    return pinky_bent and index_straight and middle_straight and ring_straight and thumb_straight



last_angle = None  # Initialize for tracking the pointer movement
last_pinch_distance = None
# Initialize the last state for zoom control
# Initialize the last action time
last_action_time = 0
debounce_delay = 0.5  # Minimum time (in seconds) between consecutive triggers


# Function to detect gestures
# Passing in original frame, the landmark list, and the processed frame
def detect_gesture(frame, landmark_list, processed):
    # variables
    global last_pinch_distance
    global last_angle
    global last_action_time
    current_time = time.time()


    last_zoom_state = False
    # Initialize the state of Alt key press
    alt_pressed = False

    # If the length of the landmark list is greater than 21 (there is only 21)
    if len(landmark_list) >= 21:
        # 1st action: Move the mouse
        # Need the media pipe to move a point
        # index finger is position of mouse
        # Find the index of finger tip in processed frame
        index_finger_tip = find_finger_tip(processed)
        # Find the distance between landmarks 4 and 5 (thumb closed)
        # 4 and 5 are tips of index and thumb
        thumb_index_dist = get_distance([landmark_list[4], landmark_list[5]])

        # Check for the Alt-Tab gesture
        #alt_pressed = alt_tab_gesture(landmark_list, alt_pressed)
        # MOVE MOUSE
        # If the thumb and index finger distance is close, and the index finger is upright...
        if is_move_cursor(landmark_list):
            # Move the mouse according to the index finger tip
            move_mouse(index_finger_tip)

        # if get_distance([landmark_list[4], landmark_list[5]]) < 50  and get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90:
        #     # Move the mouse according to the index finger tip
        #     move_mouse(index_finger_tip)

        # LEFT CLICK
        elif is_left_click(landmark_list,  thumb_index_dist) and (current_time - last_action_time > debounce_delay):
            # Mouse press right
            mouse.press(Button.left)
            # And release
            mouse.release(Button.left)
            # Put text on screen
            cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            last_action_time = current_time

        # RIGHT CLICK
        elif is_right_click(landmark_list, thumb_index_dist) and (current_time - last_action_time > debounce_delay):
            # Mouse press left
            mouse.press(Button.right)
            # And release
            mouse.release(Button.right)
            # Put text on screen
            cv2.putText(frame, "Right Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            last_action_time = current_time

        # # DOUBLE CLICK
        # elif is_double_click(landmark_list, thumb_index_dist) and (current_time - last_action_time > debounce_delay):
        #     pyautogui.doubleClick()
        #     cv2.putText(frame, "Double Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        #     last_action_time = current_time

        # SCREENSHOT
        elif is_screenshot(landmark_list,thumb_index_dist ):
            im1 = pyautogui.screenshot()
            label = random.randint(1, 1000)
            im1.save(f'my_screenshot_{label}.png')
            cv2.putText(frame, "Screenshot Taken", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            last_action_time = current_time

        # SWITCH WINDOW
        elif is_switch_window(landmark_list) and (current_time - last_action_time > debounce_delay):
            # Press and release Ctrl + Alt + Tab
            pyautogui.hotkey('ctrl', 'alt', 'tab')
            last_action_time = current_time

        # SWITCH TAB
        elif is_switch_tab(landmark_list) and (current_time - last_action_time > debounce_delay):
            # Press and release Ctrl + Alt + Tab
            pyautogui.hotkey('ctrl', 'tab')
            last_action_time = current_time


        # PRESS ENTER
        elif is_press_enter(landmark_list) and (current_time - last_action_time > debounce_delay):
            print("Pinky bent - enter pressed!")
            pyautogui.hotkey("enter")
            cv2.putText(frame, "Enter pressed", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            last_action_time = current_time


        # KEYBOARD
        elif is_keyboard_open(landmark_list) and (current_time - last_action_time > debounce_delay):
            # Zoom out when pinky and thumb touch
            # Simulate pressing Windows Key, Ctrl, and O
            #pyautogui.hotkey('win', 'ctrl', 'o')  # Opens OSK
            pyautogui.moveTo(1527, 1027)

            pyautogui.click()
            print("Keyboard open")
            last_action_time = current_time

        # FULLSCREEN
        elif is_fullscreen(landmark_list) and (current_time - last_action_time > debounce_delay):
        # Simulate pressing the F11 key
            pyautogui.press('f11')
            print("fullscreen")
            last_action_time = current_time


        # # COPY
        # # If both conditions are true, perform the desired action
        # if are_cut_fingers_down(landmark_list) and is_copy(landmark_list):
        #     print("Peace sign detected! Performing action...")
        #     # Example action (e.g., copy something with Ctrl+C)
        #     pyautogui.hotkey('ctrl', 'c')  # This simulates pressing Ctrl+C to copy


        # ZOOM IN/OUT
        #last_pinch_distance = zoom_slider_control(landmark_list, last_pinch_distance)

        zoom_control_thumb_middle(landmark_list)

        # ROTATE
        # Check for rotation gesture (all fingers out except the ring finger)
        if len(landmark_list) >= 21:
            # Check if the gesture for rotation is detected
            if is_rotate_gesture(landmark_list):
                # Get the current hand rotation angle
                rotation_angle = detect_hand_rotation(landmark_list)

                # Determine pinky's position
                if is_pinky_on_left(landmark_list):
                    # Modify rotation logic based on pinky position
                    smooth_rotate_with_keys(-rotation_angle, hold_time=0.1)  # Rotate left if pinky is left
                else:
                    smooth_rotate_with_keys(rotation_angle, hold_time=0.1)  # Rotate right if pinky is right

# Main function
def main():
    # Helps draw the landmarks
    draw = mp.solutions.drawing_utils
    # Capture camera 1 with openCV
    cap = cv2.VideoCapture(0)
    cap.set(3, cam_width)
    cap.set(4, cam_height)

    # try catch block so errors are caught
    try:
        # Checking if the capture is running successfully
        while cap.isOpened():
            # Read the video frame by frame
            # If you can read the frame, success bool is true, else false
            success, frame = cap.read()
            # if frame us not read, break out of the loop
            if not success:
                break
            # Else flip the frame (makes it so that it looks like a mirror)
            frame = cv2.flip(frame, 1)

            # Bounding box
            #cv2.rectangle(frame, (frame_red, frame_red), (cam_width - frame_red, cam_height - frame_red), (255, 0, 255), 2)

            # Processing
            # Frame is passed as RGB format as mediapipe requires it (CV captures in BGR)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Pass in frame to model created and stores the processed output
            processed = hands.process(frameRGB)

            # Array to receive all the landmarks from hands
            landmark_list = []
            # If there was detection
            if processed.multi_hand_landmarks:
                # Take the landmarks from one of the hands
                hand_landmarks = processed.multi_hand_landmarks[0]  # Assuming only one hand is detected
                # Use drawing utility to see the landmarks
                # Pass in actual frame (where), hand landmark (what), and what type we need to draw
                draw.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)
                # Loop through all landmarks detected and push in landmark list
                for lm in hand_landmarks.landmark:
                    landmark_list.append((lm.x, lm.y))

            # Function to detect gestures (passing in original fame, the landmark list, nand the processed frame!!
            detect_gesture(frame, landmark_list, processed)

            # Show the captured frame
            # Name the window that is showing the frame as "Frame" and pass in frame var
            cv2.imshow('Frame', frame)
            # Wait for 1 ms after each frame is read.
            #  If keyboard q is pressed, break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Release the capture and destroy all windows
        cap.release()
        cv2.destroyAllWindows()


# If you import this to any other python file, this function will run
if __name__ == '__main__':
    main()