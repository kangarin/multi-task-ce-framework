from flask import Blueprint

application_management_blue = Blueprint('application_management', __name__, url_prefix='/applications')
from . import views