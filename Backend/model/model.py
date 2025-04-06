import mediapipe as mp
import cv2
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# setup mediapipe instance 
with mp_pose.Pose(min_detection_confidence = 0.6, min_tracking_confidence = 0.6) as pose:
    # webcam activation - video FEED
    cap = cv2.VideoCapture(1)
    while cap.isOpened():
        ret, frame = cap.read()

        # start detections and render
        ## recolor the image to rgb
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # makes the detection (the results is stored in an array)
        results = pose.process(image)

        # recolor back to bgr
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # extract the landmarks (joints of the body)
        try:
            landmarks = results.pose_landmarks.landmark
        except:
            pass


        # rendering of the pose detections points
        mp_drawing.draw_landmarks(image, 
                                  results.pose_landmarks, 
                                  mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0,0,255), thickness=3, circle_radius=5),
                                  mp_drawing.DrawingSpec(color=(0,255,0), thickness=3, circle_radius=5)
                                  )


        cv2.imshow('Mediapipe feed', image)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()


"""
Calculate the angles from three joints of the body.
Parameters: a,b,c - the three joints in this format (a: start, b: middle, c: end)
Return: angle - the angle between the three joints of the body
Constraints: the angle between three joints of the body cannot be greater than 180 degrees (physical constraint)
"""
def calculate_angles(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360-angle

    return angle


shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
print(shoulder)