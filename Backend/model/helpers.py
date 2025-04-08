import numpy as np
from mediapipe import solutions as mp_pose

def calculate_angles(a, b, c):
    """ Helper function to calculate angles between three points """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360-angle

    return angle


def calculate_spine_angle(landmarks, mp_pose):
    """ Calculates the spine angle based on shoulder, hip and knee positions """
    # Get points for spine calculation
    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    
    # Calculate angle between shoulder, hip and knee
    spine_angle = calculate_angles(shoulder, hip, knee)
    return spine_angle