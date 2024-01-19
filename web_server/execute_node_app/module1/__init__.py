from flask import Blueprint

module1_blue = Blueprint('module1', __name__, url_prefix='/module1')
from . import views