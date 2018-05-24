#encoding: utf-8

from flask import Flask

app = Flask(__name__)
app.secret_key = 'F\xbb\xfa<\xf3h\xcaL\xbd\xcb~s\xbf\xe2;P\x025\x83\xa8\x05\x12.NM@<w\x0c*\xd2?'

from restapi import bp as restapi_bp
app.register_blueprint(restapi_bp)

import views