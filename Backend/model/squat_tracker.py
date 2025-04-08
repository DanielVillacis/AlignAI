import numpy as np
from helpers import calculate_angles

class SquatTracker:
    def __init__(self):
        self.squat_count = 0
        self.in_squat = False # flag to indicate if currently in a squat
        self.last_squat_time = 0
        
        # store data for squats
        self.hip_positions = []
        self.knee_angles = [] 
        self.spine_angles = [] 
        self.knee_tracking = { 
            'left': [],
            'right': []
        }
        self.arm_angles = []  # for arm stability tracking during squats
        self.squat_qualities = []
     
       
    def add_frame_data(self, landmarks, mp_pose):
        """ Adds data of a frame to the respective lists for analysis """
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        left_foot = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
        right_foot = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]
        
        # track hip position
        hip_center = [(left_hip.y + right_hip.y)/2]
        self.hip_positions.append(hip_center[0])
        
        # track knee angle (left & right) for depth during the squat
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
        self.knee_angles.append(avg_knee_angle)
        
        # track spine angle
        left_spine_angle = calculate_angles(
            [left_shoulder.x, left_shoulder.y],
            [left_hip.x, left_hip.y],
            [left_knee.x, left_knee.y]
        )
        right_spine_angle = calculate_angles(
            [right_shoulder.x, right_shoulder.y],
            [right_hip.x, right_hip.y],
            [right_knee.x, right_knee.y]
        )
        avg_spine_angle = (left_spine_angle + right_spine_angle) / 2
        self.spine_angles.append(avg_spine_angle)
        
        # track knee alignment
        ankle_width = abs(right_ankle.x - left_ankle.x)
        if ankle_width > 0:
            # left knee tracking (negative = inward collapse, positive = outward)
            left_knee_align = (left_knee.x - left_ankle.x) / ankle_width
            # right knee tracking (negative = outward, positive = inward collapse)
            right_knee_align = (right_ankle.x - right_knee.x) / ankle_width
            
            self.knee_tracking['left'].append(left_knee_align)
            self.knee_tracking['right'].append(right_knee_align)
        
        # track arm & shoulder stability
        shoulder_height = (left_shoulder.y + right_shoulder.y) / 2
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
        if min_knee_angle < 70:
            depth_score = 25  # very deep squat (might be too deep for some)
        elif min_knee_angle < 90:
            depth_score = 30  # perfect squat depth
        elif min_knee_angle < 110:
            depth_score = 20  # good squat depth
        elif min_knee_angle < 130:
            depth_score = 15  # fair squat depth
        else:
            depth_score = 10  # poor squat depth
            
        # 2. back Angle Score (0-25 points): based on the spine angle
        # get spine angle at the deepest point of the squat
        spine_angle = self.spine_angles[-30:][min_knee_angle_index]
        
        # ideal: 10-20 degrees (forward lean)
        if 10 <= spine_angle <= 20:
            spine_score = 25  # perfect spine position
        elif 5 <= spine_angle < 10 or 20 < spine_angle <= 25:
            spine_score = 20  # good spine position
        elif 0 <= spine_angle < 5 or 25 < spine_angle <= 35:
            spine_score = 15  # fair spine position
        else:
            spine_score = 10  # poor spine position (too vertical or too much forward lean)
            
        # 3. knee Tracking Score (0-25 points): based on knee alignment
        if len(self.knee_tracking['left']) > 10 and len(self.knee_tracking['right']) > 10:
            # get knee tracking at deepest squat
            left_align = self.knee_tracking['left'][-30:][min_knee_angle_index]
            right_align = self.knee_tracking['right'][-30:][min_knee_angle_index]
            
            # check for knees caving in
            # for left knee: negative value means inward collapse
            # for right knee: positive value means inward collapse
            left_valgus = min(0, left_align)  # only negative values (inward collapse)
            right_valgus = max(0, right_align)  # only positive values (inward collapse)
            
            # calculate knee tracking score
            # lower is better
            knee_tracking_score = 25 - min(25, (abs(left_valgus) + abs(right_valgus)) * 50)
        else:
            knee_tracking_score = 15  # default 
            
        # 4. movement consistency score (0-20 points)
        # check if the movement was smooth based on angle variance
        angle_diffs = np.diff(self.knee_angles[-30:])
        movement_smoothness = np.var(angle_diffs)
        
        # lower variance = smoother movement = higher score
        consistency_score = 20 - min(20, movement_smoothness * 10)
        
        # calculate total score
        total_quality_score = depth_score + spine_score + knee_tracking_score + consistency_score
        
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