from flask import jsonify
from api import app
from api.decorators import token_required, admin_required
from api.models import User


@app.route('/userInfo', methods=['GET'])
@token_required
def get_user_info(user):
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role})


@app.route('/users/<user_id>', methods=['GET'])
@token_required
@admin_required
def get_user_info_by_id(_, user_id):
    user = User.query.filter_by(id=user_id).first()

    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role})


@app.route('/users', methods=['GET'])
@token_required
@admin_required
def get_users(_):
    users = User.query.all()

    output = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
    return jsonify(output)
