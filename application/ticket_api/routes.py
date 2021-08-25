# application/ticket_api/routes.py
from . import ticket_api_blueprint
from ..models import Ticket
from flask import make_response, request, jsonify
from .. import db


@ticket_api_blueprint.route('/api/tickets', methods=['GET'])
def get_tickets():
    data = []
    for row in Ticket.query.all():
        data.append(row.to_json())

    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@ticket_api_blueprint.route('/api/ticket/create', methods=['POST'])
def post_create():
    project_id = request.json['project_id']
    assignee_id = request.json['assignee_id']
    title = request.json['title']
    reporter_id = request.json['reporter_id']
    description = request.json['description']
    status = request.json['status']

    ticket = Ticket()
    ticket.project_id = project_id
    ticket.assignee_id = assignee_id
    ticket.title = title
    ticket.reporter_id = reporter_id
    ticket.description = description
    ticket.status = status

    db.session.add(ticket)
    db.session.commit()

    response = jsonify({'message': 'Ticket added', 'result': ticket.to_json()})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@ticket_api_blueprint.route('/api/ticket/<ticket_id>/exists', methods=['GET'])
def get_ticket(ticket_id):
    item = Ticket.query.filter_by(id=ticket_id).first()
    if item is not None:
        response = jsonify({'result': True})
    else:
        response = jsonify({'message': 'Cannot find ticket'}), 404
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@ticket_api_blueprint.route('/api/ticket/<ticket_id>', methods=['PUT'])
def put_ticket(ticket_id):
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    ticket.assignee_id = request.json["assignee_id"]
    ticket.description = request.json["description"]
    ticket.title = request.json["title"]
    ticket.status = request.json["status"]
    db.session.commit()

    response = jsonify(ticket.to_json())
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@ticket_api_blueprint.route('/api/ticket/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    db.session.delete(ticket)
    db.session.commit()

    response = jsonify({"ticket deleted": ticket.title})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@ticket_api_blueprint.route('/api/tickets/projects/<project_id>', methods=['GET'])
def get_project_tickets(project_id):
    tickets = Ticket.query.filter_by(project_id=project_id)

    response = jsonify(json_list=[i.to_json() for i in tickets])
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@ticket_api_blueprint.route('/api/tickets/assignee/projects/<project_id>', methods=['GET'])
def get_user_tickets_by_user(project_id):
    assignee_id = request.json['assignee_id']
    tickets = Ticket.query.filter_by(project_id=project_id, assignee_id=assignee_id)

    response = jsonify(json_list=[i.to_json() for i in tickets])
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@ticket_api_blueprint.route('/api/tickets/status/projects/<project_id>', methods=['GET'])
def get_user_tickets_by_status(project_id):
    status = request.json['status']
    tickets = Ticket.query.filter_by(project_id=project_id, status=status)

    response = jsonify(json_list=[i.to_json() for i in tickets])
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@ticket_api_blueprint.route('/api/tickets/reporter/projects/<project_id>', methods=['GET'])
def get_user_tickets_by_reporter(project_id):
    reporter_id = request.json['reporter_id']
    tickets = Ticket.query.filter_by(project_id=project_id, reporter_id=reporter_id)

    response = jsonify(json_list=[i.to_json() for i in tickets])
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@ticket_api_blueprint.route('/api/tickets/users/projects/<project_id>', methods=['GET'])
def get_users_tickets(project_id):
    assignee_ids = request.json['assignee_ids']
    tickets = []
    for assignee_id in assignee_ids:
        tickets += Ticket.query.filter_by(project_id=project_id, assignee_id=assignee_id)

    response = jsonify(json_list=[i.to_json() for i in tickets])
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
