from flask import jsonify
from api import app
from api.decorators import token_required


@app.route('/userInfo', methods=['GET'])
@token_required
def get_user_info(user):
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})