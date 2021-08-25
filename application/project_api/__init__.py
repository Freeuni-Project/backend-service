# application/project_api/__init__.py
from flask import Blueprint

project_api_blueprint = Blueprint('project_api', __name__)

from . import routes
