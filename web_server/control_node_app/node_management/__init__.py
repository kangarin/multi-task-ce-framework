from flask import Blueprint

node_management_blue = Blueprint('node_management_blue', __name__, url_prefix='/nodes')
from . import views