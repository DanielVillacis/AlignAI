import subprocess

class AIService:
    @staticmethod
    def run_model():
        process = subprocess.Popen(
            ['python3', 'model.py'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return process