import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import time
from utils.hand_tracking import find_distance, fingers_up

wCam, hCam = 640, 480
frameR = 100
smoothening = 7
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0
screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

click_down = False
zoom_threshold_in = 100
zoom_threshold_out = 40
last_zoom_time = 0
prev_hand_y = 0
last_click_time = 0
double_click_interval = 0.4
click_threshold = 30

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_img)

    lm_list = []
    if result.multi_hand_landmarks:
        handLms = result.multi_hand_landmarks[0]
        for id, lm in enumerate(handLms.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append((cx, cy))

        mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

        if lm_list:
            x1, y1 = lm_list[8]
            x2, y2 = lm_list[4]
            x3, y3 = lm_list[12]
            y_hand_center = lm_list[9][1]

            cv2.rectangle(img, (frameR, frameR), (w - frameR, h - frameR), (255, 0, 255), 2)

            x = np.interp(x1, (frameR, w - frameR), (0, screen_w))
            y = np.interp(y1, (frameR, h - frameR), (0, screen_h))

            curr_x = prev_x + (x - prev_x) / smoothening
            curr_y = prev_y + (y - prev_y) / smoothening

            pyautogui.moveTo(screen_w - curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            finger_status = fingers_up(lm_list)
            total_fingers = sum(finger_status)
            current_time = time.time()

            distance = find_distance((x1, y1), (x2, y2))
            # Reliable single/double click detection
            if distance < click_threshold:
                if not click_down:
                    if current_time - last_click_time < double_click_interval:
                        pyautogui.doubleClick()
                        print("Double Click Triggered")
                    else:
                        pyautogui.click()
                        print("Single Click Triggered")

                    last_click_time = current_time
                    click_down = True
            else:
                click_down = False

            # Right Click - Thumb & Middle Finger pinch
            right_click_distance = find_distance((x1, y1), (x3, y3))
            if right_click_distance < 25:
                pyautogui.click(button='right')
                time.sleep(0.3)

            # Controlled Zoom In/Out with thumb & index only
            zoom_distance = find_distance((x1, y1), (x2, y2))
            if finger_status[0] == 1 and sum(finger_status[1:]) == 0:
                if zoom_distance > zoom_threshold_in and current_time - last_zoom_time > 0.5:
                    pyautogui.hotkey('ctrl', '+')
                    print("Zoom In Triggered")
                    last_zoom_time = current_time
                elif zoom_distance < zoom_threshold_out and current_time - last_zoom_time > 0.5:
                    pyautogui.hotkey('ctrl', '-')
                    print("Zoom Out Triggered")
                    last_zoom_time = current_time

            # Scroll Logic with all fingers open
            if total_fingers == 5:
                if prev_hand_y != 0:
                    if y_hand_center < prev_hand_y - 15:
                        pyautogui.scroll(300)
                        print("Scroll Up")
                    elif y_hand_center > prev_hand_y + 15:
                        pyautogui.scroll(-300)
                        print("Scroll Down")
                prev_hand_y = y_hand_center
            else:
                prev_hand_y = 0

    cv2.imshow("Virtual Mouse", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
