import mediapipe as mp
import cv2
import numpy as np
import math

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_spine_deviation(shoulder, hip):
    shoulder_x, shoulder_y = shoulder
    hip_x, hip_y = hip
    horizontal_deviation = abs(shoulder_x - hip_x)
    return horizontal_deviation

# Setup Mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6) as pose:
    cap = cv2.VideoCapture(1)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

            # Compute midpoints for shoulders and hips
            mid_shoulder = [(left_shoulder[0] + right_shoulder[0]) / 2,
                            (left_shoulder[1] + right_shoulder[1]) / 2]
            mid_hip = [(left_hip[0] + right_hip[0]) / 2,
                       (left_hip[1] + right_hip[1]) / 2]

            # Calculate the spine angle relative to vertical:
            # Vertical direction is along the y-axis.
            dx = mid_shoulder[0] - mid_hip[0]
            dy = mid_shoulder[1] - mid_hip[1]

            # compute the magnitude of the spine vector
            norm = math.sqrt(dx*dx + dy*dy)
            if norm == 0:
                norm = 1    # prevent division by zero

            # vertical_vector = [0, 1]  # vertical vector

            spine_angle = math.degrees(math.acos(-dy / norm))

            # Define a threshold angle (in degrees) for tilt
            tilt_threshold = 2  # adjust as necessary

            if abs(spine_angle) > tilt_threshold:
                spine_color = (0, 0, 255)  # Red for tilt
                status_msg = f"Tilted Spine: {spine_angle:.1f}°"
                text_color = (0, 0, 255)
            else:
                spine_color = (0, 255, 0)  # Green for good alignment
                status_msg = "Good Spine Alignment"
                text_color = (0, 255, 0)

            # Add text overlay with spine status
            cv2.putText(
                image, 
                status_msg,
                (10, 30),  # Position (x,y)
                cv2.FONT_HERSHEY_SIMPLEX,  # Font
                1,  # Font scale
                text_color,  # Text color
                2,  # Thickness
                cv2.LINE_AA  # Line type
            )

            # Draw spine line (from mid_shoulder to mid_hip) with the chosen color
            cv2.line(
                image,
                tuple(np.multiply(mid_shoulder, [image.shape[1], image.shape[0]]).astype(int)),
                tuple(np.multiply(mid_hip, [image.shape[1], image.shape[0]]).astype(int)),
                spine_color,
                4,
            )

        except AttributeError:
            # If landmarks are not detected, do nothing
            pass

        # Render pose landmarks and connections
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
        )

        cv2.imshow("Mediapipe Feed", image)

        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()