import subprocess
import os
import json
import sys
import threading
import datetime

class AIService:
    @staticmethod
    def run_model(client_id, scan_reason="Consult"):
        """ Run the assessment model as a detached process"""
        base_directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        model_path = os.path.join(base_directory, 'model', 'model.py')
        log_file = os.path.join(base_directory, 'logs', 'model_output.log')

        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        def run_detached_process():
            try:
                if client_id:
                    args = {
                        "client_id": int(client_id),
                        "scan_reason": scan_reason
                    }
                    args_json = json.dumps(args)
                    
                    # we use nohup on macOS to keep process running after parent terminates -> else we have a race condition
                    with open(log_file, 'a') as log:
                        log.write(f"\n--- Starting new scan at {datetime.datetime.now()} ---\n")
                        log.write(f"Client ID: {client_id}, Reason: {scan_reason}\n")
                        
                        python_exe = sys.executable  
                        
                        if sys.platform == 'darwin':  # macOS
                            cmd = f'nohup {python_exe} "{model_path}" \'{args_json}\' > "{log_file}" 2>&1 &'
                            os.system(cmd)
                        else:  # windows or other
                            # use subprocess from python
                            CREATE_NEW_PROCESS_GROUP = 0x00000200
                            DETACHED_PROCESS = 0x00000008
                            cmd = [python_exe, model_path, args_json]
                            subprocess.Popen(
                                cmd,
                                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0,
                                stdout=open(log_file, 'a'),
                                stderr=subprocess.STDOUT,
                                shell=False,
                                close_fds=True
                            )
            except Exception as e:
                with open(log_file, 'a') as log:
                    log.write(f"Error starting scan process: {str(e)}\n")

        # run in a separate thread to avoid blocking the flask request
        thread = threading.Thread(target=run_detached_process)
        thread.daemon = False  # keep running even if main thread ends
        thread.start()

            
        return {"status": "started", "client_id": client_id, "log_file": log_file}