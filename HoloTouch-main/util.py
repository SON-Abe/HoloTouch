import numpy as np

# Angle is bending at point b
# Pass in 3 point to find angle between
def get_angle(a, b, c):
    # Taking the difference between the angle created by AB and x-axis and BC and x-axis
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    # Convert to degrees
    angle = np.abs(np.degrees(radians))
    # Return the angle
    return angle


def get_distance(landmark_ist):
    # If the length of landmark list is less than 2 (2 landmarks), return
    if len(landmark_ist) < 2:
        return
    # If there is at least 2 landmarks
    # Calculate the Euclidean distance
    (x1, y1), (x2, y2) = landmark_ist[0], landmark_ist[1]
    L = np.hypot(x2 - x1, y2 - y1)
    return np.interp(L, [0, 1], [0, 1000])