# application/project_api/routes.py
from . import project_api_blueprint
from ..models import Project, ProjectUser, User
from .. import db
from flask import make_response, request, jsonify
import requests
from producer import publish


@project_api_blueprint.route('/api/projects', methods=['GET'])
def get_projects():
    data = []
    for row in Project.query.all():
        data.append(row.to_json())

    response = jsonify(data)

    return response


@project_api_blueprint.route('/api/project/<project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.filter_by(id=project_id).first()

    response = jsonify(project.to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@project_api_blueprint.route('/api/project/<project_id>/add-users', methods=['POST'])
def post_add_users(project_id):
    users_ids = request.json['users_ids']
    project_users = []
    for user_id in users_ids:
        project_user = ProjectUser(user_id)
        project_user.project_id = project_id
        project_users.append(project_user)
        db.session.add(project_user)
        publish('add_user_to_project', {"title": get_project_name(project_id), "email": get_user_email(user_id)}, 'mail_queue')

    db.session.commit()

    response = jsonify(json_list=[project_user.to_json() for project_user in project_users])
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@project_api_blueprint.route('/api/project/<project_id>/get-users-ids', methods=['GET'])
def get_users_ids(project_id):
    project_users = ProjectUser.query.filter_by(project_id=project_id)
    response = jsonify(json_list=[i.to_json() for i in project_users])
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@project_api_blueprint.route('/api/project/<project_id>/get-users', methods=['GET'])
def get_users(project_id):
    project_users = ProjectUser.query.filter_by(project_id=project_id)
    users_ids = [project_user.to_json()['user_id'] for project_user in project_users]

    data = []
    for row in User.query.filter(User.id.in_(users_ids)).all():
        data.append(row.to_json())

    response = jsonify(json_list=data)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@project_api_blueprint.route('/api/<user_id>/get-projects-by-user-id', methods=['POST'])
def get_projects_by_user_id(user_id):
    user_projects = ProjectUser.query.filter_by(user_id=user_id)
    project_ids = [project_user.to_json()['project_id'] for project_user in user_projects]

    data = []
    for row in Project.query.filter(Project.id.in_(project_ids)).all():
        data.append(row.to_json())

    response = jsonify(json_list=data)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@project_api_blueprint.route('/api/project/<project_id>/get-users-not-added', methods=['GET'])
def get_users_not_added(project_id):
    project_users = ProjectUser.query.filter_by(project_id=project_id)
    users_ids = [project_user.to_json()['user_id'] for project_user in project_users]

    data = []
    for row in User.query.filter(User.id.notin_(users_ids)).all():
        data.append(row.to_json())

    response = jsonify(json_list=data)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@project_api_blueprint.route('/api/project/create', methods=['POST'])
def post_create_project():
    project_name = request.json['project_name']
    description = request.json['description']
    status = request.json['status']

    project = Project()
    project.project_name = project_name
    project.description = description
    project.status = status

    db.session.add(project)
    db.session.commit()

    response = jsonify({'message': 'Project added', 'result': project.to_json()})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@project_api_blueprint.route('/api/project/<project_id>', methods=['PUT'])
def put_project(project_id):
    project = Project.query.filter_by(id=project_id).first()
    project.project_name = request.json['project_name']
    project.description = request.json['description']
    project.status = request.json['status']

    db.session.commit()

    response = jsonify({'message': 'Project updated', 'result': project.to_json()})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@project_api_blueprint.route('/api/project/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.filter_by(id=project_id).first()
    db.session.delete(project)
    db.session.commit()

    response = jsonify({'project.project_nam': 'project deleted'})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@project_api_blueprint.route('/api/project/<project_id>/remove-user', methods=['DELETE'])
def delete_project_user(project_id):
    user_id = request.json["user_id"]
    project_user = ProjectUser.query.filter_by(project_id=project_id, user_id=user_id).first()
    db.session.delete(project_user)
    db.session.commit()
    publish('remove_user_from_project', {"title": get_project_name(project_id), "email": get_user_email(user_id)}, 'mail_queue')

    response = jsonify({"user removed from project": user_id})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


def get_user_email(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.email

def get_project_name(project_id):
    project = Project.query.filter_by(id=project_id).first()
    return project.project_name