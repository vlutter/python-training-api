from flask import request, jsonify
import datetime
import jwt
from api import app, bcrypt, db
from api.models import User


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(email=data['email'], name=data['name'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully!'})


@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'error': 'Необходимы email и пароль'}), 401

    user = User.query.filter_by(email=auth.username).first()

    if not user:
        return jsonify({'error': 'Пользователь с таким email не найден'}), 401

    if bcrypt.check_password_hash(user.password, auth.password):
        token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token, 'user': {'id': user.id, 'name': user.name, 'email': user.email}})

    return jsonify({'error': 'Пароль неверный'}), 401
