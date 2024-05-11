from flask import jsonify, request
from api import app, db
from api.decorators import token_required
from api.models import Task, TaskGroup


@app.route('/tasks', methods=['GET'])
@token_required
def get_tasks(_):
    groups = TaskGroup.query.all()
    groups_with_tasks = []
    for group in groups:
        tasks = Task.query.filter_by(group_id=group.id).all()
        tasks_data = [{"id": task.id, "name": task.name} for task in tasks]
        groups_with_tasks.append({"id": group.id, "name": group.name, "tasks": tasks_data})
    return jsonify(groups_with_tasks)


@app.route('/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(_, task_id):
    task = Task.query.get(task_id)
    if task:
        response = {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "group_id": task.group_id,
            "example_data": task.example_data
        }
        return jsonify(response)
    return jsonify({"error": "Task not found"}), 404


@app.route('/tasks/group', methods=['POST'])
@token_required
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
def create_task(_):
    data = request.json
    name = data.get('name')
    description = data.get('description')
    example_data = data.get('example_data')
    group_id = data.get('group_id')
    if name and group_id:
        group = TaskGroup.query.get(group_id)
        if group:
            new_task = Task(name=name, description=description, group_id=group_id, example_data=example_data)
            db.session.add(new_task)
            db.session.commit()
            return jsonify({"message": "Task created successfully"}), 201
        return jsonify({"error": "Group not found"}), 404
    return jsonify({"error": "Name and group_id are required"}), 400


@app.route('/tasks/group/<int:group_id>', methods=['PUT'])
@token_required
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


@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(_, task_id):
    task = Task.query.get(task_id)
    if task:
        data = request.json
        name = data.get('name')
        description = data.get('description')
        group_id = data.get('group_id')
        example_data = data.get('example_data')
        if name:
            task.name = name
        if description:
            task.description = description
        if group_id:
            task.group_id = group_id
        if example_data:
            task.example_data = example_data
        db.session.commit()
        return jsonify({"message": "Task updated successfully"})
    return jsonify({"error": "Task not found"}), 404


@app.route('/tasks/group/<int:group_id>', methods=['DELETE'])
@token_required
def delete_group(_, group_id):
    group = TaskGroup.query.get(group_id)
    if group:
        db.session.delete(group)
        db.session.commit()
        return jsonify({"message": "Group deleted successfully"})
    return jsonify({"error": "Group not found"}), 404


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(_, task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully"})
    return jsonify({"error": "Task not found"}), 404
