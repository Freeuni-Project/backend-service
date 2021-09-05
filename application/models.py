# application/models.py
from . import db
from datetime import datetime
from flask_login import UserMixin
from passlib.hash import sha256_crypt
import jwt


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), unique=False, nullable=True)
    last_name = db.Column(db.String(255), unique=False, nullable=True)
    password = db.Column(db.String(255), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    authenticated = db.Column(db.Boolean, default=False)
    api_key = db.Column(db.String(255), unique=True, nullable=True)

    def encode_api_key(self, key):
        self.api_key = jwt.encode(
            {"username": self.username, "is_admin": self.is_admin, "user_id": self.id, "exp": 1900000000},
            "freeuni_project_secret",
            # algorithm="HS256",
            headers={"alg": "HS256",
                     "typ": "JWT",
                     "kid": key})


    def encode_password(self):
        self.password = sha256_crypt.hash(self.password)

    def __repr__(self):
        return '<User %r>' % (self.username)

    def to_json(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'id': self.id,
            'api_key': self.api_key,
            'is_active': True,
            'is_admin': self.is_admin
        }


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True, default="")
    reporter_id = db.Column(db.Integer, unique=False, nullable=False)
    assignee_id = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.String(25), unique=False, nullable=False, default="In progress")
    project_id = db.Column(db.Integer, unique=False, nullable=False)
    # comments = db.relationship('TicketComment', backref='ticketComment')

    def __repr__(self):
        return '<Ticket %r>' % (self.title)

    def create(self, title, reporter_id, assignee_id, project_id):
        self.title = title
        self.reporter_id = reporter_id
        self.assignee_id = assignee_id
        self.project_id = project_id

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'reporter_id': self.reporter_id,
            'project_id': self.project_id,
            'status': self.status,
            'assignee_id': self.assignee_id,
            'description': self.description,
        }


class TicketComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    comment = db.Column(db.String(255), unique=False, nullable=True, default="")

    def create(self, ticket_id, user_id, comment):
        self.ticket_id = ticket_id
        self.user_id = user_id
        self.comment = comment

    def to_json(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'comment': self.comment
        }


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=False, default='')
    users = db.relationship('ProjectUser', backref='projectUser')
    tickets = db.relationship('ProjectTicket', backref='projectTicket')
    status = db.Column(db.String(255), unique=False, nullable=False, default='Ongoing')

    def create(self, project_name, description):
        self.project_name = project_name
        self.description = description
        return self

    def to_json(self):
        users = []
        tickets = []

        for i in self.tickets:
            tickets.append(i.to_json())

        for i in self.users:
            users.append(i.to_json())

        return {
            'id': self.id,
            'project_name': self.project_name,
            'description': self.description,
            'users': users,
            'tickets': tickets,
            'status': self.status
        }


class ProjectUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    user_id = db.Column(db.Integer)

    def __init__(self, user_id):
        self.user_id = user_id

    def to_json(self):
        return {
            'user_id': self.user_id,
            'project_id': self.project_id,
        }


class ProjectTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    ticket_id = db.Column(db.Integer)

    def __init__(self, ticket_id):
        self.ticket_id = ticket_id

    def to_json(self):
        return {
            'ticked_id': self.ticket_id,
            'project_id': self.project_id,
        }
