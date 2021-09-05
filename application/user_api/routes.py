# application/user_api/routes.py
# from flask_cors import cross_origin

from . import user_api_blueprint
from .. import db, login_manager
from ..models import User
from flask import make_response, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
import requests
from passlib.hash import sha256_crypt


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    return None


@user_api_blueprint.route('/api/users', methods=['GET'])
def get_users():
    data = []
    for row in User.query.all():
        data.append(row.to_json())

    response = jsonify(data)
    return response


# @cross_origin()
@user_api_blueprint.route('/api/users-by-ids', methods=['GET'])
def get_users_by_id():
    users_ids = request.args.getlist("users_ids")
    data = []
    for row in User.query.filter(User.id.in_(users_ids)).all():
        data.append(row.to_json())

    response = jsonify(json_list=data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@user_api_blueprint.route('/auth/user/create', methods=['POST'])
def post_register():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    username = request.json['username']
    is_admin = request.json['is_admin']

    password = sha256_crypt.hash((str(request.json['password'])))

    user = User()
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.password = password
    user.username = username
    user.is_admin = is_admin
    user.authenticated = True

    db.session.add(user)
    db.session.commit()

    response = jsonify({'message': 'User added', 'result': user.to_json()})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@user_api_blueprint.route('/auth/user/login', methods=['POST'])
def post_login():
    username = request.json['username']
    user = User.query.filter_by(username=username).first()
    if user:
        if sha256_crypt.verify(str(request.json['password']), user.password):
            key = requests.get('http://ckong-api-gateway:8001/consumers/loginserverissuer/jwt').json()["data"][0]["key"]
            user.encode_api_key(key)
            db.session.commit()
            login_user(user)

            return make_response(jsonify({'message': 'Logged in', 'data': user.to_json()}))
    response = make_response(jsonify({'message': 'Not logged in'}), 401)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response



@user_api_blueprint.route('/api/user/logout', methods=['POST'])
def post_logout():
    if current_user.is_authenticated:
        logout_user()
        return make_response(jsonify({'message': 'You are logged out'}))

    response = make_response(jsonify({'message': 'You are not logged in'}))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@user_api_blueprint.route('/api/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()

    response = jsonify({"User deleted": user.username})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@user_api_blueprint.route('/api/user/<username>/exists', methods=['GET'])
def get_username(username):
    item = User.query.filter_by(username=username).first()
    if item is not None:
        response = jsonify({'result': True})
    else:
        response = jsonify({'message': 'Cannot find username'}), 404

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@login_required
@user_api_blueprint.route('/api/user', methods=['GET'])
def get_user():
    if current_user.is_authenticated:
        response = make_response(jsonify({'result': current_user.to_json()}))
    else:
        response = make_response(jsonify({'message': 'Not logged in'}))

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 401
