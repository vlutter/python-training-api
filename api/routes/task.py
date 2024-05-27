import json

from flask import jsonify, request
from api import app, db
from api.decorators import token_required, admin_required
from api.models import Task, TaskGroup, Solution, User


def get_groups_with_tasks(user, include_solution):
    groups = TaskGroup.query.all()
    groups_with_tasks = []
    for group in groups:
        tasks = Task.query.filter_by(group_id=group.id).all()

        tasks_data = []

        are_no_solutions = True
        is_group_done = True
        is_group_in_process = False

        for task in tasks:
            solution = Solution.query.filter_by(user_id=user.id, task_id=task.id).first()

            status = None
            if solution:
                are_no_solutions = False
                status = solution.status

            if status and status != 'not_started':
                is_group_in_process = True

            if status != 'done':
                is_group_done = False

            if include_solution:
                tasks_data.append({
                    "id": task.id,
                    "name": task.name,
                    "status": status,
                    "solution": None if not solution or not solution.last_solution else solution.last_solution,
                    "output": None if not solution or not solution.last_output else json.loads(solution.last_output)
                })
            else:
                tasks_data.append({"id": task.id, "name": task.name, "status": status})

        group_status = None

        if not are_no_solutions:
            group_status = 'not_started'

            if is_group_in_process:
                group_status = 'in_progress'

            if is_group_done:
                group_status = 'done'

        groups_with_tasks.append({"id": group.id, "name": group.name, "status": group_status, "tasks": tasks_data})

    return groups_with_tasks


@app.route('/tasks', methods=['GET'])
@token_required
def get_tasks(user):
    try:
        groups_with_tasks = get_groups_with_tasks(user, False)
    except Exception as err:
        return jsonify({"error": str(err)}), 500

    return jsonify(groups_with_tasks)


@app.route('/tasks/export', methods=['GET'])
@token_required
def export_tasks(_):
    groups = TaskGroup.query.all()
    groups_with_tasks = []
    for group in groups:
        tasks = Task.query.filter_by(group_id=group.id).all()
        tasks_data = []

        for task in tasks:
            tasks_data.append({
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "tests": task.tests,
            })

        groups_with_tasks.append({"id": group.id, "name": group.name, "tasks": tasks_data})

    return jsonify(groups_with_tasks)


@app.route('/tasks/import', methods=['POST'])
@token_required
@admin_required
def import_tasks(_):
    data = request.json

    for group in data:
        new_group = TaskGroup(id=group['id'], name=group['name'])
        db.session.add(new_group)
        db.session.commit()

        for task in group['tasks']:
            new_task = Task(id=task['id'], name=task['name'], description=task['description'], group_id=group['id'],
                            tests=task['tests'])
            db.session.add(new_task)
            db.session.commit()

    return jsonify({"message": "Tasks imported successfully"}), 201


@app.route('/tasks/user/<user_id>', methods=['GET'])
@token_required
@admin_required
def get_user_solutions(_, user_id):
    user = User.query.filter_by(id=user_id).first()

    try:
        groups_with_tasks = get_groups_with_tasks(user, True)
    except Exception as err:
        return jsonify({"error": str(err)}), 500

    return jsonify(groups_with_tasks)


@app.route('/tasks/<task_id>', methods=['GET'])
@token_required
def get_task(user, task_id):
    task = Task.query.get(task_id)
    if task:
        task_tests = json.loads(task.tests)
        solution = Solution.query.filter_by(user_id=user.id, task_id=task_id).first()

        status = 'not_started'
        last_solution = None

        if solution:
            status = solution.status
            last_solution = solution.last_solution

        response = {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "group_id": task.group_id,
            "tests": task_tests,
            "status": status,
            "last_solution": last_solution
        }
        return jsonify(response)
    return jsonify({"error": "Task not found"}), 404


@app.route('/tasks/<task_id>/solutions', methods=['GET'])
@token_required
@admin_required
def get_task_solutions(_, task_id):
    solutions = Solution.query.filter_by(task_id=task_id).all()

    output = []

    for solution in solutions:
        user = User.query.filter_by(id=solution.user_id).first()

        output.append({
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'status': solution.status,
            'solution': solution.last_solution,
            'output': None if not solution.last_output else json.loads(solution.last_output)
        })

    return jsonify(output)


@app.route('/tasks/group', methods=['POST'])
@token_required
@admin_required
def create_group(_):
    data = request.json
    name = data.get('name')
    if name:
        new_group = TaskGroup(name=name)
        db.session.add(new_group)
        db.session.commit()
        return jsonify({"message": "Group created successfully"}), 201
    return jsonify({"error": "Name is required"}), 400


@app.route('/tasks', methods=['POST'])
@token_required
@admin_required
def create_task(_):
    data = request.json
    task_id = data.get('id')
    name = data.get('name')
    description = data.get('description')
    tests = data.get('tests')
    group_id = data.get('group_id')

    if not tests:
        tests = []

    print(tests)

    if name and group_id:
        group = TaskGroup.query.get(group_id)
        if group:
            task_tests = json.dumps(tests)
            print(task_tests)
            new_task = Task(id=task_id, name=name, description=description, group_id=group_id, tests=task_tests)
            db.session.add(new_task)
            db.session.commit()
            return jsonify({"message": "Task created successfully"}), 201
        return jsonify({"error": "Group not found"}), 404
    return jsonify({"error": "Name and group_id are required"}), 400


@app.route('/tasks/group/<int:group_id>', methods=['PUT'])
@token_required
@admin_required
def update_group(_, group_id):
    group = TaskGroup.query.get(group_id)
    if group:
        data = request.json
        name = data.get('name')
        if name:
            group.name = name
            db.session.commit()
            return jsonify({"message": "Group updated successfully"})
        return jsonify({"error": "Name is required"}), 400
    return jsonify({"error": "Group not found"}), 404


@app.route('/tasks/<task_id>', methods=['PUT'])
@token_required
@admin_required
def update_task(_, task_id):
    task = Task.query.get(task_id)
    if task:
        data = request.json
        name = data.get('name')
        description = data.get('description')
        group_id = data.get('group_id')
        tests = data.get('tests')
        if name:
            task.name = name
        if description:
            task.description = description
        if group_id:
            task.group_id = group_id

        if tests:
            task.tests = json.dumps(tests)
        else:
            task.tests = json.dumps([])

        db.session.commit()
        return jsonify({"message": "Task updated successfully"})
    return jsonify({"error": "Task not found"}), 404


@app.route('/tasks/group/<int:group_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_group(_, group_id):
    group = TaskGroup.query.get(group_id)
    if group:
        db.session.delete(group)
        db.session.commit()
        return jsonify({"message": "Group deleted successfully"})
    return jsonify({"error": "Group not found"}), 404


@app.route('/tasks/<task_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_task(_, task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully"})
    return jsonify({"error": "Task not found"}), 404
