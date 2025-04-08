import numpy as np

class BalanceTracker:
    def __init__(self):
        self.hip_positions = []
        self.shoulder_positions = []
        self.ankle_positions = []
        
    def add_frame_data(self, landmarks, mp_pose):
        """ Adds data of a frame to the respective lists for analysis """
        # Tracks the hip positions
        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        hip_center = [(left_hip[0] + right_hip[0])/2, (left_hip[1] + right_hip[1])/2]
        self.hip_positions.append(hip_center)
        
        # Tracks the shoulder positions
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        shoulder_center = [(left_shoulder[0] + right_shoulder[0])/2, (left_shoulder[1] + right_shoulder[1])/2]
        self.shoulder_positions.append(shoulder_center)
        
        # Tracks the ankle positions for the stepping analysis
        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
        self.ankle_positions.append([left_ankle, right_ankle])
        
        
    def calculate_balance_score(self):
        """ Calculates the balance score based on hip position variance """
        if len(self.hip_positions) < 10:   
            return 0
            
        hip_x_positions = [pos[0] for pos in self.hip_positions]
        hip_y_positions = [pos[1] for pos in self.hip_positions]
        
        # Lower variance = better balance (stability)
        x_variance = np.var(hip_x_positions)
        y_variance = np.var(hip_y_positions)
        
        # Convertion of the variance to a score (0-100%)
        balance_score = 100 - min(100, (x_variance + y_variance) * 300)
        return max(0, balance_score)