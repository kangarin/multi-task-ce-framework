from flask import Blueprint

module2_blue = Blueprint('module2', __name__, url_prefix='/module2')
from . import views