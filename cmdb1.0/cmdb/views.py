#encoding: utf-8
import json
import time
import csv
from StringIO import StringIO

# 从flask包导入Flask对象
from flask import render_template
from flask import request
from flask import redirect
from flask import session


from cmdb import app
import models

from utils import decorator

@app.route('/')
def index():
    if session.get('user'): return redirect('/users/')
    return render_template('index.html')

@app.route('/login/', methods=['post', 'get'])
def login():
    if session.get('user'): return redirect('/users/')

    params = request.form if 'POST' == request.method else request.args
    username = params.get('username', '')
    password = params.get('password', '')

    user = models.User.login(username, password)
    if user:
        session['user'] = user
        return redirect('/users/')
    else:
        return render_template('index.html', username=username, password=password, error='username or password is error')

@app.route('/users/')
@decorator.login_required
def user_list():
    users = models.User.get_list()
    return render_template('user.html', users=users)


@app.route('/user/save/', methods=['POST'])
@decorator.login_required
def user_save():

    username = request.form.get('name', '')
    password = request.form.get('password', '')
    age = request.form.get('age', 0)

    user = models.User(0, username, password, age)
    ok, error = user.validate_save()
    if ok:
        user.save()
        return json.dumps({'code' : 200})
    else:
        return json.dumps({'code' : 400, 'error' : error})


@app.route('/user/view/')
@decorator.login_required
def user_view():

    user = models.User.get_by_key(request.args.get('id', 0))
    return json.dumps(user) if user else json.dumps({})

@app.route('/user/modify/', methods=['POST'])
@decorator.login_required
def user_modify():

    uid = request.form.get('id', '')
    username = request.form.get('name', '')
    age = request.form.get('age', '')

    user = models.User(uid, username, '', age)

    ok, error = user.validate_modify()
    if ok:
        user.modify()
        return json.dumps({'code' : 200})
    else:
        return json.dumps({'code' : 400, 'error' : error})

@app.route('/user/password/modify/', methods=['POST'])
@decorator.login_required
def user_password_modify():

    uid = request.form.get('id', '')
    passwrd = request.form.get('password', '')

    manager_password = request.form.get('manager-password', '')
    if models.User.validate_password(session['user']['id'], manager_password):
        user = models.User(uid, '', passwrd, 0)

        ok, error = user.validate_password_modify()
        if ok:
            user.password_modify()
            return json.dumps({'code' : 200})
        return json.dumps({'code' : 400, 'error' : error})
    else:
        return json.dumps({'code' : 400, 'error' : u'管理员密码错误'})


@app.route('/user/delete/')
@decorator.login_required
def user_delete():

    models.User.delete_by_key(request.args.get('id', 0))
    return json.dumps({'code' : 200})


@app.route('/machine_rooms/')
def machine_room_list():
    machine_rooms = models.get_machine_rooms()
    return render_template('machine_room.html', machine_rooms=machine_rooms);


@app.route('/machine_room/save/', methods=['POST'])
def machine_room_save():
    if session.get('user') is None: return json.dumps({'code' : 403, 'error' : ''})

    name = request.form.get('name', '')
    addr = request.form.get('addr', '')
    ip_ranges = request.form.get('ip_ranges', '')
    ok, error = models.validate_machine_room_save(name, addr, ip_ranges)
    if ok:
        models.machine_room_save(name, addr, ip_ranges)
        return json.dumps({'code' : 200})
    else:
        return json.dumps({'code' : 400, 'error' : error})


@app.route('/machine_room/delete/')
def machine_room_delete():
    if session.get('user') is None: return redirect('/')

    models.machine_room_delete(request.args.get('id', 0))
    return redirect('/machine_rooms/')


@app.route('/log/')
def log():
    if session.get('user') is None: return redirect('/')
    topn = request.args.get('topn', 10)
    topn = int(topn) if str(topn).isdigit() else 10
    result = models.get_topn(topn)
    return render_template('log.html', logs=result)

@app.route('/log/upload/', methods=['POST'])
def log_upload():
    if session.get('user') is None: return redirect('/')
    file = request.files.get('log')
    if file:
        filename = '/tmp/log_%s' % int(1000 * time.time())
        file.save(filename)
        #导入
        models.access_log_import(filename)
    return redirect('/log/')


@app.route('/log/download/')
@decorator.login_required
def log_download():
    topn = request.args.get('topn', 10)
    topn = int(topn) if str(topn).isdigit() else 10
    result = models.get_topn(topn)
    io = StringIO()
    csv_writer = csv.writer(io)
    csv_writer.writerow(['IP', 'URL', 'CODE', 'COUNT'])
    for line in result:
        csv_writer.writerow(line)
    text = io.getvalue()
    io.close()
    return text, 200, {'Content-Type' : 'text/csv; charset=utf-8', 'Content-disposition' : 'attachment; filename=TOP_%s_log.csv' % topn}
   


@app.route('/assets/')
def asset_index():
    if session.get('user') is None: return redirect('/')
    machine_rooms = models.get_machine_rooms()
    return render_template('asset.html', machine_rooms=machine_rooms)


@app.route('/asset/list/')
def asset_list():
    if session.get('user') is None: json.dumps({'data' : []})

    assets = models.get_assets()
    return json.dumps({'data' : assets})


@app.route('/asset/save/', methods=['POST'])
def asset_save():
    if session.get('user') is None: return json.dumps({'code' : 403, 'error' : ''})

    params = request.form
    ok, error = models.validate_asset_save(params)
    if ok:
        models.asset_save(params)
        return json.dumps({'code' : 200})
    else:
        return json.dumps({'code' : 400, 'error' : error})


@app.route('/asset/view/')
def asset_view():
    if session.get('user') is None: return json.dumps({'code' : 403, 'error' : ''})

    aid = request.args.get('id', 0)
    asset = models.get_asset_by_id(aid)
    return json.dumps(asset)


@app.route('/asset/modify/', methods=['POST'])
def asset_modify():
    if session.get('user') is None: return json.dumps({'code' : 403, 'error' : ''})

    params = request.form
    ok, error = models.validate_asset_modify(params)
    if ok:
        models.asset_modify(params)
        return json.dumps({'code' : 200})
    else:
        return json.dumps({'code' : 400, 'error' : error})


@app.route('/asset/delete/')
def asset_delete():
    if session.get('user') is None: return json.dumps({'code' : 403, 'error' : ''})

    models.asset_delete(request.args.get('id', 0))
    return json.dumps({'code' : 200})


@app.route('/logout/')
def logout():
    session.clear()
    return redirect('/')


@app.route('/monitor/host/create/', methods=['POST'])
def monitor_host_create():
    models.monitor_host_create(request.form)
    return json.dumps({'code' : 200, 'result' : ''})

@app.route('/monitor/host/list/')
def monitor_host_list():
    asset = models.get_asset_by_id(request.args.get('id', 0))
    ip = asset.get('ip', '')
    result = models.monitor_host_list(ip)
    return json.dumps({'code' : 200, 'result' : result})

@app.route('/alert/')
def alert_index():
    if session.get('user') is None: return redirect('/')
    return render_template('alert.html')


@app.route('/alert/list/')
def alert_list():
    if session.get('user') is None: json.dumps({'data' : []})

    alerts = models.get_alerts()
    return json.dumps({'data' : alerts})


@app.route('/dashboard/')
def dashboard():
    if session.get('user') is None: return redirect('/')
    return render_template('dashboard.html')

@app.route('/dashboard/data/')
def dashboard_data():
    if session.get('user') is None: json.dumps({'code' : 401, 'data' : []})
    accesslog_code_dist_legend, accesslog_code_dist_data = models.accesslog_code_dist()
    accesslog_code_dist_time_legend, accesslog_code_dist_time_xAxis, accesslog_code_dist_time_data = models.accesslog_code_time_dist()
    accesslog_ip_legend, accesslog_ip_dist_geoCoord, accesslog_ip_dist_markline_data, accesslog_ip_dist_markpoint_data = models.accesslog_ip_dist()

    return json.dumps({'code' : 200, 'data' : {
            'accesslog_code_dist_legend' : accesslog_code_dist_legend,
            'accesslog_code_dist_data' : accesslog_code_dist_data,
            'accesslog_code_dist_time_legend' : accesslog_code_dist_time_legend, 
            'accesslog_code_dist_time_xAxis' : accesslog_code_dist_time_xAxis, 
            'accesslog_code_dist_time_data' : accesslog_code_dist_time_data,
            'accesslog_ip_legend' : accesslog_ip_legend,
            'accesslog_ip_dist_geoCoord' : accesslog_ip_dist_geoCoord,
            'accesslog_ip_dist_markline_data' : accesslog_ip_dist_markline_data,
            'accesslog_ip_dist_markpoint_data' : accesslog_ip_dist_markpoint_data
        }})