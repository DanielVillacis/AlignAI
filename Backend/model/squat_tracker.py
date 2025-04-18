import numpy as np
from helpers import calculate_angles

class SquatTracker:
    def __init__(self):
        self.squat_count = 0
        self.in_squat = False # flag to indicate if currently in a squat
        self.last_squat_time = 0
        
        self.hip_positions = []
        self.knee_angles = [] 
        self.spine_angles = [] 
        self.knee_tracking = { 
            'left': [],
            'right': []
        }
        self.arm_angles = [] 
        self.squat_qualities = []
     
       
    def add_frame_data(self, landmarks, mp_pose):
        """ Adds data of a frame to the respective lists for analysis """
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        left_foot = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
        
        # track left hip position
        self.hip_positions.append(left_hip.y)
        
        # track knee angle (left) for depth during the squat
        left_knee_angle = calculate_angles(
            [left_hip.x, left_hip.y], 
            [left_knee.x, left_knee.y], 
            [left_ankle.x, left_ankle.y]
        )
        self.knee_angles.append(left_knee_angle)
        
        # track spine angle
        spine_angle = calculate_angles(
            [left_shoulder.x, left_shoulder.y],
            [left_hip.x, left_hip.y],
            [0, left_hip.y]  # Vertical reference point
        )
        self.spine_angles.append(spine_angle)
        
        # track knee alignment
        knee_forward_position = left_knee.x - left_ankle.x
        self.knee_tracking['left'].append(knee_forward_position)
        
        # track arm & shoulder stability
        shoulder_height = (left_shoulder.y)
        self.arm_angles.append(shoulder_height)
        

    def detect_squat(self, landmarks, mp_pose, current_time):
        """ Detects squat based on knee angle and tracks squat count """
        self.add_frame_data(landmarks, mp_pose)
        
        # body key points for squat detection
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        
        # calculate the average knee angle for squat detection
        left_knee_angle = calculate_angles(
            [left_hip.x, left_hip.y], 
            [left_knee.x, left_knee.y], 
            [left_ankle.x, left_ankle.y]
        )
        right_knee_angle = calculate_angles(
            [right_hip.x, right_hip.y], 
            [right_knee.x, right_knee.y], 
            [right_ankle.x, right_ankle.y]
        )

        avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
        
        # we detect squat based on knee angle (can be tweaked based on squat depth and professional feedback)
        if avg_knee_angle < 130 and not self.in_squat and current_time - self.last_squat_time > 1.0:
            self.in_squat = True
        elif avg_knee_angle > 160 and self.in_squat:
            self.squat_count += 1
            self.in_squat = False
            self.last_squat_time = current_time
            
            # calculate the quality of the present squat
            if len(self.knee_angles) > 10:
                squat_quality = self.calculate_squat_quality()
                self.squat_qualities.append(squat_quality)
                
            return True
            
        return False
        

    def get_squat_count(self):
        return self.squat_count
        

    def calculate_squat_quality(self):
        """ 
        Calculates the quality score for a completed squat based on four factors :
        - depth score (0-30 points): based on knee angle
        - back angle score (0-25 points): based on spine angle
        - knee tracking score (0-25 points): based on knee alignment
        - movement consistency score (0-20 points): based on angle variance
        """
        # use data during the squat phase (when knee angle was decreasing and at its minimum)
        if len(self.knee_angles) < 10:
            return 50  # Default if not enough data
            
        # identify the lowest knee angle (deepest point of squat)
        min_knee_angle_index = np.argmin(self.knee_angles[-30:])
        min_knee_angle = self.knee_angles[-30:][min_knee_angle_index]
        
        # 1. depth Score (0-30 points): based on knee angle
        # ideal: 70-90 degrees, Poor: >110 degrees
        if min_knee_angle < 90:
            depth_score = 30  # perfect squat depth
        elif min_knee_angle < 110:
            depth_score = 25  # good squat depth
        elif min_knee_angle < 130:
            depth_score = 20  # fair squat depth
        else:
            depth_score = 15  # poor squat depth
            
        # 2. back Angle Score (0-25 points): based on the spine angle
        # get spine angle at the deepest point of the squat
        spine_angle = self.spine_angles[-30:][min_knee_angle_index]

        # Ideal: 25-45 degrees of forward lean for side view
        if 65 <= spine_angle <= 75:
            spine_score = 25  # perfect spine angle
        elif 55 <= spine_angle < 65 or 75 < spine_angle <= 85:
            spine_score = 20  # good spine angle
        elif 45 <= spine_angle < 55 or 85 < spine_angle <= 95:
            spine_score = 15  # fair spine angle
        else:
            spine_score = 5  # poor spine angle
            
        # 3. Knee Position Score (0-25 points) - replace knee valgus with knee-over-toe
        if len(self.knee_tracking['left']) > 10:
            # Get knee position at deepest squat 
            knee_position = self.knee_tracking['left'][-30:][min_knee_angle_index]
            
            # Assess if knees are too far forward or not enough
            # Slight forward position is good, too much or too little is bad
            if -0.1 < knee_position < 0.3:  # Ideal: knees slightly ahead of ankles
                knee_position_score = 25
            elif 0.3 <= knee_position < 0.5:  # A bit too forward
                knee_position_score = 20
            elif -0.2 <= knee_position <= -0.1 or 0.5 <= knee_position < 0.6:  # Either too back or forward
                knee_position_score = 15
            else:  # Way too far forward or back
                knee_position_score = 10
        else:
            knee_position_score = 15  # default
            
        # 4. movement consistency score (0-20 points)
        # check if the movement was smooth based on angle variance
        angle_diffs = np.diff(self.knee_angles[-30:])
        movement_smoothness = np.sqrt(np.mean(np.square(angle_diffs)))
        
        # lower variance = smoother movement = higher score
        consistency_score = 20 - min(20, movement_smoothness * 3)
        
        # calculate total score
        total_quality_score = depth_score + spine_score + knee_position_score + consistency_score
        
        print(f"Min Knee Angle: {min_knee_angle}, Depth Score: {depth_score}")
        print(f"Spine Angle: {spine_angle}, Spine Score: {spine_score}")
        print(f"Knee Position: {knee_position}, Knee Position Score: {knee_position_score}")
        print(f"Movement Smoothness: {movement_smoothness}, Consistency Score: {consistency_score}")

        return total_quality_score
    

    def get_squat_score(self):
        """ Get the overall squat score based on completed squats """
        if self.squat_count == 0:
            return 0
            
        # ff we have quality scores on the three squats, we use their average
        if len(self.squat_qualities) > 0:
            return sum(self.squat_qualities) / len(self.squat_qualities)
        else:
            return 60  # default middle score if no quality available