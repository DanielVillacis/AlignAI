from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run-script', methods=['GET'])
def run_script():
    try:
        # Start the model script as a separate process
        subprocess.Popen(['python3', 'model.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return jsonify({'message': 'Model script launched successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)