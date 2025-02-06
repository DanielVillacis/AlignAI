import mediapipe as mp
import cv2
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Function to calculate the deviation from vertical alignment
def calculate_spine_deviation(shoulder, hip):
    shoulder_x, shoulder_y = shoulder
    hip_x, hip_y = hip

    # Compute the horizontal distance (should ideally be zero for vertical alignment)
    horizontal_deviation = abs(shoulder_x - hip_x)
    return horizontal_deviation

#test

# Setup Mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6) as pose:
    cap = cv2.VideoCapture(1)  # Webcam feed

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Perform pose detection
        results = pose.process(image)

        # Convert the image back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates of shoulders and hips
            left_shoulder = [
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
            ]
            right_shoulder = [
                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,
            ]
            left_hip = [
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y,
            ]
            right_hip = [
                landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y,
            ]

            # Calculate deviations for left and right sides
            left_deviation = calculate_spine_deviation(left_shoulder, left_hip)
            right_deviation = calculate_spine_deviation(right_shoulder, right_hip)

            # Threshold for detecting curvature (adjust as needed)
            threshold = 0.05

            # Determine posture status
            if left_deviation < threshold and right_deviation < threshold:
                spine_color = (0, 255, 0)  # Green for good posture
                status_msg = "Good Posture"
                text_color = (0, 255, 0)
            else:
                spine_color = (0, 0, 255)  # Red for bad posture
                status_msg = "Bad Posture - Please Correct Your Position"
                text_color = (0, 0, 255)

            # Add text overlay
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

            # Draw the spine with appropriate color
            cv2.line(
                image,
                tuple(np.multiply(left_shoulder, [image.shape[1], image.shape[0]]).astype(int)),
                tuple(np.multiply(left_hip, [image.shape[1], image.shape[0]]).astype(int)),
                spine_color,
                4,
            )
            cv2.line(
                image,
                tuple(np.multiply(right_shoulder, [image.shape[1], image.shape[0]]).astype(int)),
                tuple(np.multiply(right_hip, [image.shape[1], image.shape[0]]).astype(int)),
                spine_color,
                4,
            )

        except AttributeError:
            pass

        # Render pose landmarks and connections
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
        )

        # Display the image
        cv2.imshow("Mediapipe Feed", image)

        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
