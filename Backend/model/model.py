import mediapipe as mp
import cv2
import numpy as np
import time
from enum import Enum
import json
from PIL import Image, ImageDraw, ImageFont

from balance_tracker import BalanceTracker
from step_tracker import StepTracker
from squat_tracker import SquatTracker
from helpers import calculate_spine_angle

class ExerciseState(Enum):
    WAITING = 0
    STEPPING = 1  
    SQUATTING = 2
    COMPLETED = 3


""" Helper function for modern UI text using pillow """
def add_modern_text(
        cv2_image, 
        text, position, 
        font_path="../fonts/Nunito-Bold.ttf",   
        font_size=20, 
        text_color=(255, 255, 255), 
        with_background=False
    ):
    
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    
    draw = ImageDraw.Draw(pil_image)
    
    font = ImageFont.truetype(font_path, font_size)
    if not font:
        font = ImageFont.load_default()
    
    # we get text dimensions
    if hasattr(font, "getbbox"):
        # for newer pillow versions (9.2.0+)
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    elif hasattr(font, "getsize"):
        # for pillow versions between 9.0.0 - 9.2.0
        text_width, text_height = font.getsize(text)
    else:
        # for old pillow version
        text_width, text_height = 0, 0
    
    if with_background:
        # draw rounded rectangle background around the text (optional)
        padding = 10
        x, y = position
        draw.rectangle(
            [(x - padding, y - padding), 
             (x + text_width + padding, y + text_height + padding)],
            fill=(32, 33, 36, 180),
            outline=(70, 70, 70),
            width=1
        )
    
    # draw text
    draw.text(position, text, font=font, fill=text_color)
    
    # we convert back to openCV format
    result_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return result_image


def draw_progress_bar(image, progress, position, width=200, height=20):
    x, y = position
    # draw background
    cv2.rectangle(image, (x, y), (x + width, y + height), (70, 70, 70), -1)
    # draw progress
    progress_width = int(width * progress / 100)
    cv2.rectangle(image, (x, y), (x + progress_width, y + height), (0, 184, 212), -1)
    return image


def run_assessment():
    # initialize the trackers
    balance_tracker = BalanceTracker()
    step_tracker = StepTracker()
    squat_tracker = SquatTracker()
    
    # exercise state
    current_state = ExerciseState.WAITING
    state_start_time = time.time()
    instructions = "Get ready for stepping exercise"

    
    # assessment results dictionary
    assessment_results = {
        "balance_score": 0,
        "stepping_score": 0,
        "squat_score": 0,
        "posture_score": 0,
        "overall_score": 0
    }

    # display dimensions
    display_width = 1920
    display_height = 1080

    # font sizes
    FONT_TITLE = 34
    FONT_HEADING = 32
    FONT_SUBHEADING = 30
    FONT_TEXT = 28
    FONT_SIDEBAR = 14
    
    
    # setup mediapipe poselandmark model
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    
    window_name = 'AlignAI Assessment'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6) as pose:
        # webcam activation
        cap = cv2.VideoCapture(1)  # use 1 for built-in webcam, 0 for usb or external
        
        start_time = time.time()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # resize frame to fit the display
            frame = cv2.resize(frame, (display_width, display_height))
            
            current_time = time.time()
            
            # process image for pose detection
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # extract landmarks from the body
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # update trackers based on current state
                if current_state == ExerciseState.STEPPING:
                    step_detected = step_tracker.detect_step(landmarks, mp_pose, current_time)
                    balance_tracker.add_frame_data(landmarks, mp_pose)
                    
                    # check if stepping is complete
                    if step_tracker.get_step_count() >= 10:
                        current_state = ExerciseState.SQUATTING
                        state_start_time = current_time
                        instructions = "Now perform 3 squats"
                        
                elif current_state == ExerciseState.SQUATTING:
                    squat_detected = squat_tracker.detect_squat(landmarks, mp_pose, current_time)
                    balance_tracker.add_frame_data(landmarks, mp_pose)
                    
                    # check if squatting is complete
                    if squat_tracker.get_squat_count() >= 3:
                        current_state = ExerciseState.COMPLETED
                        state_start_time = current_time
                        instructions = "Assessment complete!"
                        
                        # calculate final scores
                        assessment_results["balance_score"] = balance_tracker.calculate_balance_score()
                        assessment_results["stepping_score"] = step_tracker.get_stepping_score()
                        assessment_results["squat_score"] = squat_tracker.get_squat_score()
                        
                        # calculate spine deviation
                        spine_angle = calculate_spine_angle(landmarks, mp_pose)
                        posture_score = 100 - min(100, abs(spine_angle - 180) * 2)
                        assessment_results["posture_score"] = posture_score
                        
                        # calculate overall score
                        assessment_results["overall_score"] = np.mean([
                            assessment_results["balance_score"],
                            assessment_results["stepping_score"],
                            assessment_results["squat_score"],
                            assessment_results["posture_score"]
                        ])
                        
                # start stepping after 5 seconds of preparation
                elif current_state == ExerciseState.WAITING and current_time - state_start_time > 5:
                    current_state = ExerciseState.STEPPING
                    state_start_time = current_time
                    instructions = "Perform 10 steps in place"
            
            # draw skeleton first from mediapipe
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0,0,255), thickness=3, circle_radius=5),
                    mp_drawing.DrawingSpec(color=(0,255,0), thickness=3, circle_radius=5)
                )
            
            # current scores will be displayed on the right side
            h, w = image.shape[:2]
            sidebar_width = 300  # wider sidebar
            
            # add title to sidebar with modern text
            image = add_modern_text(
                image, 
                "AlignAI", 
                (w-sidebar_width+20, 50),
                font_size=FONT_TITLE,
                text_color=(200, 200, 255),
                with_background=False
            )
            
            # add scores to sidebar
            if current_state == ExerciseState.COMPLETED:
                # show all final scores in sidebar
                y_pos = 120
                for label, value in assessment_results.items():
                    score_text = f"{label.replace('_', ' ').title()}: {value:.1f}%"
                    image = add_modern_text(
                        image,
                        score_text, 
                        (w-sidebar_width+20, y_pos), 
                        font_size=FONT_SUBHEADING,
                        text_color=(255, 255, 255),
                        with_background=False
                    )
                    y_pos += 50
            else:
                # we show live progress
                
                # add phase info
                image = add_modern_text(
                    image,
                    f"Phase: {current_state.name}", 
                    (w-sidebar_width+20, 120),
                    font_size=FONT_TEXT,
                    text_color=(255, 255, 255),
                    with_background=False
                )
                
                # add live balance score if we have enough frames
                if len(balance_tracker.hip_positions) > 10:
                    bal_score = balance_tracker.calculate_balance_score()
                    image = add_modern_text(
                        image,
                        f"Balance: {bal_score:.1f}%", 
                        (w-sidebar_width+20, 170),
                        font_size=FONT_TEXT,
                        text_color=(255, 255, 255),
                        with_background=False
                    )
                
                # add step quality if steps have been detected
                if current_state == ExerciseState.STEPPING and step_tracker.get_step_count() > 0:
                    if len(step_tracker.step_qualities) > 0:
                        step_quality = sum(step_tracker.step_qualities) / len(step_tracker.step_qualities)
                        image = add_modern_text(
                            image,
                            f"Step Quality: {step_quality:.1f}", 
                            (w-sidebar_width+20, 220),
                            font_size=FONT_TEXT,
                            text_color=(255, 255, 255),
                            with_background=False
                        )
                
                # add squat quality if squats have been detected
                if current_state == ExerciseState.SQUATTING and squat_tracker.get_squat_count() > 0:
                    if len(squat_tracker.squat_qualities) > 0:
                        squat_quality = sum(squat_tracker.squat_qualities) / len(squat_tracker.squat_qualities)
                        image = add_modern_text(
                            image,
                            f"Squat Quality: {squat_quality:.1f}", 
                            (w-sidebar_width+20, 220),
                            font_size=FONT_TEXT,
                            text_color=(255, 255, 255),
                            with_background=False
                        )
                
            # display exercise instructions with modern text
            image = add_modern_text(
                image, 
                instructions, 
                (30, 50),
                font_size=FONT_HEADING,
                text_color=(200, 200, 255)
            )
            
            # display current progress
            if current_state == ExerciseState.STEPPING:
                steps_text = f"Steps: {step_tracker.get_step_count()}/10"
                image = add_modern_text(
                    image,
                    steps_text, 
                    (30, 120),
                    font_size=FONT_SUBHEADING,
                    text_color=(255, 255, 255)
                )
                
                # add progress bar for steps
                step_progress = (step_tracker.get_step_count() / 10) * 100
                image = draw_progress_bar(image, step_progress, (30, 160), width=500, height=20)
                
            elif current_state == ExerciseState.SQUATTING:
                squats_text = f"Squats: {squat_tracker.get_squat_count()}/3"
                image = add_modern_text(
                    image,
                    squats_text, 
                    (30, 120),
                    font_size=FONT_SUBHEADING,
                    text_color=(255, 255, 255)
                )
                
                # add progress bar for squats
                squat_progress = (squat_tracker.get_squat_count() / 3) * 100
                image = draw_progress_bar(image, squat_progress, (30, 160), width=500, height=20)
                
            elif current_state == ExerciseState.COMPLETED:
                time_in_completed = current_time - state_start_time
                if time_in_completed < 1.0:
                    completion_overlay = image.copy()
                    cv2.circle(completion_overlay, (w//2, 120), 80, (76, 175, 80), -1)
                    cv2.addWeighted(completion_overlay, 0.3, image, 0.7, 0, image)
                    
                    image = add_modern_text(
                        image,
                        "ASSESSMENT COMPLETE", 
                        (w//2 - 220, 130),
                        font_size=FONT_TEXT,
                        text_color=(76, 175, 80)
                    )
                
                # show overall score
                score_text = f"Overall Score: {assessment_results['overall_score']:.1f}%"
                image = add_modern_text(
                    image,
                    score_text, 
                    (30, 120),
                    font_size=FONT_TEXT,
                    text_color=(76, 175, 80)
                )
                
                # add individual scores
                y_position = 180
                for key, value in assessment_results.items():
                    if key != "overall_score":
                        metric_text = f"{key.replace('_', ' ').title()}: {value:.1f}%"
                        image = add_modern_text(
                            image,
                            metric_text, 
                            (50, y_position),
                            font_size=FONT_TEXT,
                            text_color=(255, 255, 255),
                            with_background=False
                        )
                        y_position += 50
            
            # display the image
            cv2.imshow(window_name, image)
            
            # check for exit ('q' for exiting the application)
            if cv2.waitKey(10) & 0xFF == ord('q') or (current_state == ExerciseState.COMPLETED and current_time - state_start_time > 5):
                break
                
        # clean up the opencv resources
        cap.release()
        cv2.destroyAllWindows()
        
        return assessment_results

if __name__ == "__main__":
    results = run_assessment()
    print(json.dumps(results, indent=4))