import json

from flask import jsonify, request
from api.decorators import token_required
import io
import sys

from api import app, db
from api.models import Task, Solution


def run(code, input_data):
    input_lines = iter(input_data.split('\n'))

    def safe_input():
        try:
            return next(input_lines)
        except StopIteration:
            return ''

    temp_dict = {'input': safe_input}
    output_capture = io.StringIO()
    original_stdout = sys.stdout

    try:
        sys.stdout = output_capture

        exec(code, temp_dict)

        output = output_capture.getvalue()
    finally:
        sys.stdout = original_stdout

    return output


def apply_solution(task_id, user_id, code, status, output):
    solution = Solution.query.filter_by(user_id=user_id, task_id=task_id).first()

    if not solution:
        new_solution = Solution(user_id=user_id, task_id=task_id, status=status, last_solution=code, last_output=output)
        db.session.add(new_solution)
    else:
        solution.last_solution = code
        solution.status = status
        solution.last_output = output

    db.session.commit()


@app.route('/run/<task_id>', methods=['POST'])
@token_required
def run_code(user, task_id):
    data = request.json
    code = data.get('code')
    input_data = data.get('input_data')

    try:
        output = run(code, input_data)
    except Exception as err:
        apply_solution(task_id, user.id, code, 'in_progress', json.dumps({'error': str(err)}))
        return jsonify({"error": str(err)}), 500

    apply_solution(task_id, user.id, code, 'in_progress', json.dumps({"output_data": output}))
    return jsonify({"output_data": output}), 200


@app.route('/test/<task_id>', methods=['POST'])
@token_required
def test_code(user, task_id):
    data = request.json
    code = data.get('code')

    task = Task.query.get(task_id)
    tests = json.loads(task.tests)

    for test in tests:
        try:
            input_data = test['input_data']
            output = run(code, input_data)

            actual_data = output.strip()
            expected_data = test['output_data'].strip()

            if actual_data != expected_data:
                error = {
                    "error": "Тесты не пройдены",
                    "data": {
                        "input_data": input_data,
                        "expected_data": expected_data,
                        "actual_data": actual_data
                    }
                }

                apply_solution(task_id, user.id, code, 'in_progress', json.dumps(error))

                return jsonify(error), 500
        except Exception as err:
            apply_solution(task_id, user.id, code, 'in_progress', json.dumps({'error': str(err)}))
            return jsonify({"error": str(err)}), 500

    apply_solution(task_id, user.id, code, 'done', json.dumps({"status": "success"}))
    return jsonify({"status": "success"}), 200
