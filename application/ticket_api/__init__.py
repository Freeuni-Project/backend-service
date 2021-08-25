# application/user_api/__init__.py
from flask import Blueprint

ticket_api_blueprint = Blueprint('ticket_api', __name__)

from . import routes
