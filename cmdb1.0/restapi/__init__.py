#encoding: utf-8

from flask import Blueprint

bp = Blueprint('restapi', __name__, static_folder='static', template_folder='templates', url_prefix='/restapi')

import views