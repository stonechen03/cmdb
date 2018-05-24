#encoding: utf-8

from flask import render_template
from flask import request

from restapi import bp

@bp.route('/help/')
def help():
    return render_template('restapi/help.html')

@bp.route('/users/', methods=['GET', 'PUT', 'POST', 'DELETE'])
@bp.route('/users/<pkey>/', methods=['GET', 'PUT', 'POST', 'DELETE'])
def users(pkey=None):
    print '*' * 20
    print pkey
    print request.args
    print request.json
    print request.form
    print '*' * 20
    if request.method == 'GET':
        if pkey is None:
            print 'GET: all'
        else:
            print 'GET: %s' % pkey
    elif request.method == 'PUT':
        print 'PUT'
        print request.form
    elif request.method == 'POST':
        print 'POST'
        print pkey
        print request.form
    elif request.method == 'DELETE':
        print 'DELETE'
        print pkey

    return ''