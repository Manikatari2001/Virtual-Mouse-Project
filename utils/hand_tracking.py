import math

def find_distance(p1, p2):
    """
    Calculate Euclidean distance between two points
    """
    x1, y1 = p1
    x2, y2 = p2
    return math.hypot(x2 - x1, y2 - y1)

def fingers_up(lm_list):
    """
    Detect which fingers are up
    """
    fingers = []

    # Index
    fingers.append(1 if lm_list[8][1] < lm_list[6][1] else 0)
    # Middle
    fingers.append(1 if lm_list[12][1] < lm_list[10][1] else 0)
    # Ring
    fingers.append(1 if lm_list[16][1] < lm_list[14][1] else 0)
    # Pinky
    fingers.append(1 if lm_list[20][1] < lm_list[18][1] else 0)
    # Thumb (Horizontal for right hand assumption)
    fingers.append(1 if lm_list[4][0] < lm_list[3][0] else 0)

    return fingers
