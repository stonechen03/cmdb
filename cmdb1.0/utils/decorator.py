#encoding: utf-8

from functools import wraps

from flask import session 
from flask import redirect
from flask import request
import json

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user') is None:
            print 'not login, before:%s, is_xhr:%s' % (func.__name__, request.is_xhr)
            if request.is_xhr:
                return json.dumps({'code' : 403, 'error' : ''})
            return redirect('/')
        print 'before:%s' % func.__name__
        rt = func(*args, **kwargs)
        print 'after:%s' % func.__name__
        return rt

    return wrapper