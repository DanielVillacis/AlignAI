import numpy as np
from helpers import calculate_spine_angle

class StepTracker:
    def __init__(self):
        self.steps = 0
        self.last_step_time = 0
        self.is_stepping = False
        self.step_threshold = 0.05
        
        self.ankle_positions = []
        self.hip_positions = []
        self.knee_positions = []
        self.shoulder_positions = []
        self.spine_angles = []
        self.knee_heights = {
            'left': [],
            'right': []
        }
        self.step_qualities = []
        
    def add_frame_data(self, landmarks, mp_pose):
        """ Adds data of a frame to the respective lists for analysis """
        # hip tracking
        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        hip_center = [(left_hip[0] + right_hip[0])/2, (left_hip[1] + right_hip[1])/2]
        self.hip_positions.append(hip_center)
        
        # shoulder tracking
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        shoulder_center = [(left_shoulder[0] + right_shoulder[0])/2, (left_shoulder[1] + right_shoulder[1])/2]
        self.shoulder_positions.append(shoulder_center)
        
        # knee tracking for height and symmetry
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        self.knee_heights['left'].append(left_knee.y)
        self.knee_heights['right'].append(right_knee.y)
        
        # spine angle tracking
        spine_angle = calculate_spine_angle(landmarks, mp_pose)
        self.spine_angles.append(spine_angle)
        

    def detect_step(self, landmarks, mp_pose, current_time):
        """ Detects a step based on ankle positions and time """
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        
        # track ankle vertical positions
        left_y = left_ankle.y
        right_y = right_ankle.y
        
        # calculate difference between ankle heights
        ankle_diff = abs(left_y - right_y)
        
        self.add_frame_data(landmarks, mp_pose)
        
        # if ankles are significantly apart vertically and we haven't recently counted a step, count a step
        if ankle_diff > self.step_threshold and not self.is_stepping and current_time - self.last_step_time > 0.5:
            self.steps += 1
            self.is_stepping = True
            self.last_step_time = current_time
            
            # calculate quality of this step
            if len(self.hip_positions) > 10:
                step_quality = self.calculate_step_quality()
                self.step_qualities.append(step_quality)
            
            return True
        
        # we reset step detection when ankles return close together
        elif ankle_diff < self.step_threshold/2:
            self.is_stepping = False
            
        return False
    
    def calculate_step_quality(self):
        """ 
        Calculate quality score for the most recent step based on four factors : 
        - 1. hip displacement & stability (0-25 points)
        - 2. spine angle consistency (0-25 points)
        - 3. knee lift symmetry (0-25 points)
        - 4. shoulder stability (0-25 points)
        """
        # use recent frames (last 2-3 seconds of data)
        frames_to_analyze = min(30, len(self.hip_positions))
        
        # 1. hip displacement & stability (0-25 points)
        recent_hip_y = [pos[1] for pos in self.hip_positions[-frames_to_analyze:]]
        hip_vertical_variance = np.var(recent_hip_y)
        recent_hip_x = [pos[0] for pos in self.hip_positions[-frames_to_analyze:]]
        hip_lateral_variance = np.var(recent_hip_x)
        
        # Lower variance = better stability
        hip_stability_score = 25 - min(25, (hip_vertical_variance + hip_lateral_variance) * 1000)
        
        # 2. spine angle consistency (0-25 points)
        recent_spine_angles = self.spine_angles[-frames_to_analyze:]
        spine_variance = np.var(recent_spine_angles)
        
        # lower variance = more consistent spine angle
        spine_consistency_score = 25 - min(25, spine_variance * 0.5)
        
        # 3. knee lift symmetry (0-25 points)
        # if we have anough data, we calculate the knee lift symmetry
        if len(self.knee_heights['left']) > frames_to_analyze and len(self.knee_heights['right']) > frames_to_analyze:
            left_knee_range = max(self.knee_heights['left'][-frames_to_analyze:]) - min(self.knee_heights['left'][-frames_to_analyze:])
            right_knee_range = max(self.knee_heights['right'][-frames_to_analyze:]) - min(self.knee_heights['right'][-frames_to_analyze:])
            
            # difference between left and right knee movement range
            knee_symmetry_diff = abs(left_knee_range - right_knee_range)
            
            # lower difference = better symmetry
            knee_symmetry_score = 25 - min(25, knee_symmetry_diff * 500)
        else:
            knee_symmetry_score = 12.5  # default score (half) 
            
        # 4. shoulder stability (0-25 points)
        recent_shoulder_x = [pos[0] for pos in self.shoulder_positions[-frames_to_analyze:]]
        shoulder_lateral_variance = np.var(recent_shoulder_x)
        
        # lower variance = better stability
        shoulder_stability_score = 25 - min(25, shoulder_lateral_variance * 1000)
        
        # combine all scores
        total_quality_score = hip_stability_score + spine_consistency_score + knee_symmetry_score + shoulder_stability_score
        
        return total_quality_score
    

    def get_step_count(self):
        return self.steps
    

    def get_stepping_score(self):
        """ Calculate overall stepping score based on quantity and quality """
        if self.steps == 0:
            return 0
            
        # calculate average quality score from all steps
        if len(self.step_qualities) > 0:
            avg_quality = sum(self.step_qualities) / len(self.step_qualities)
        else:
            avg_quality = 50  # default score (half) if no data
            
        # combine quantity (number of steps completed) with quality
        # 40% of score is from completing steps, 60% from quality
        quantity_score = min(40, self.steps * 4)  # max 40 points for 10 steps
        quality_score = avg_quality * 0.6  # max 60 points for quality
        
        return min(100, quantity_score + quality_score)