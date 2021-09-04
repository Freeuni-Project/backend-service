# application/ticket_api/routes.py
import json

from . import ticket_api_blueprint
from ..models import Ticket, TicketComment, User
from flask import make_response, request, jsonify
from .. import db
from producer import publish


@ticket_api_blueprint.route('/api/tickets', methods=['GET'])
def get_tickets():
    data = []
    for row in Ticket.query.all():
        data.append(row.to_json())

    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@ticket_api_blueprint.route('/api/ticket/<ticket_id>/add-comment', methods=['POST'])
def post_comment(ticket_id):
    user_id = request.json['user_id']
    comment = request.json['comment']

    ticket_comment = TicketComment()
    ticket_comment.user_id = user_id
    ticket_comment.comment = comment
    ticket_comment.ticket_id = ticket_id
    db.session.add(ticket_comment)
    db.session.commit()
    response = jsonify({'message': 'Comment added', 'result': ticket_comment.to_json()})
    return response


@ticket_api_blueprint.route('/api/ticket/<ticket_id>/get-comments', methods=['GET'])
def get_comments(ticket_id):
    comments = TicketComment.query.filter_by(ticket_id=ticket_id)
    response = jsonify(json_list=[i.to_json() for i in comments])
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

    publish('assign_to_ticket', {"title" : title, "email" : get_user_email(ticket.assignee_id)}, 'mail_queue')
    db.session.add(ticket)
    db.session.commit()

    response = jsonify({'message': 'Ticket added', 'result': ticket.to_json()})
    response.headers.add('Access-Control-Allow-Origin', '*')

    publish("new_ticket", ticket.to_json(), 'stat_queue')
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

    publish('update_ticket_assignee', {"title" : ticket.title, "email" : get_user_email(ticket.assignee_id)}, 'mail_queue')
    publish('update_ticket_reporter', {"title" : ticket.title, "email" : get_user_email(ticket.reporter_id)}, 'mail_queue')
    if ticket.status == 'Done':
        publish("done_ticket", ticket.to_json(), 'stat_queue')
    return response


@ticket_api_blueprint.route('/api/ticket/<comment_id>/update-comment', methods=['PUT'])
def put_comment(comment_id):
    comment = TicketComment.query.filter_by(id=comment_id).first()
    comment.comment = request.json["comment"]
    db.session.commit()
    response = jsonify(comment.to_json())
    return response


@ticket_api_blueprint.route('/api/ticket/<comment_id>/delete-comment', methods=['DELETE'])
def delete_comment(comment_id):
    comment = TicketComment.query.filter_by(id=comment_id).first()
    db.session.delete(comment)
    db.session.commit()

    response = jsonify({"comment deleted": comment.comment})
    return response


@ticket_api_blueprint.route('/api/ticket/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    db.session.delete(ticket)

    db.session.commit()

    response = jsonify({"ticket deleted": ticket_id})
    response.headers.add('Access-Control-Allow-Origin', '*')

    params = {'ticket_id': ticket_id}
    publish("delete_ticket", params, 'stat_queue')
    publish('delete_ticket_assignee', {"title" : ticket.title, "email" : get_user_email(ticket.assignee_id)}, 'mail_queue')
    publish('delete_ticket_reporter', {"title" : ticket.title, "email" : get_user_email(ticket.reporter_id)}, 'mail_queue')
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


def get_user_email(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.email