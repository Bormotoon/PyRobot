from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import json

app = Flask(__name__)
CORS(app)


class RobotSimulator:
    def __init__(self):
        self.robot_pos = {"x": 0, "y": 0}
        self.walls = set()
        self.markers = {}
        self.colored_cells = set()

    def reset(self):
        self.robot_pos = {"x": 0, "y": 0}
        self.walls.clear()
        self.markers.clear()
        self.colored_cells.clear()


simulator = RobotSimulator()


@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.json
    code = data.get('code', '')

    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(code)
            temp_name = f.name

        result = subprocess.run(
            ['python', temp_name],
            capture_output=True,
            text=True,
            timeout=5
        )

        os.unlink(temp_name)

        if result.stderr:
            return jsonify({
                'success': False,
                'message': f'Ошибка выполнения: {result.stderr}'
            })

        output = json.loads(result.stdout)
        simulator.robot_pos = output.get('robotPos', simulator.robot_pos)

        return jsonify({
            'success': True,
            'message': 'Код выполнен',
            'robotPos': simulator.robot_pos
        })

    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'Неверный формат вывода'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/reset', methods=['POST'])
def reset_simulator():
    simulator.reset()
    return jsonify({'success': True, 'message': 'Симулятор сброшен'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)