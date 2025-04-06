import subprocess
import os

class AIService:
    @staticmethod
    def run_model():

        base_directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        model_path = os.path.join(base_directory, 'model', 'model.py')

        process = subprocess.Popen(
            ['python3', model_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return process