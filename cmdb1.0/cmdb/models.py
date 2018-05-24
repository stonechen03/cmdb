#encoding: utf-8

import json
import datetime
import os
import time

import MySQLdb

import geoip2.database

import gconf
from utils import dbutils
from utils import crypt


SQL_MACHINE_ROOM_COLUMNS = ('id', 'name', 'addr', 'ip_ranges')
SQL_MACHINE_ROOM_LIST = 'select id, name, addr, ip_ranges from machine_room'

SQL_MACHINE_ROOM_SAVE = 'insert into machine_room(name, addr, ip_ranges) values(%s, %s, %s)'
SQL_MACHINE_ROOM_DELETE = 'delete from machine_room where id=%s'

SQL_ASSET_LIST_COLUMNS = 'id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status'.split(',')
SQL_ASSET_LIST = 'select id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status from asset where status!=2;'

SQL_ASSET_SAVE_COLUMNS = 'sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status'.split(',')
SQL_ASSET_SAVE = 'insert into asset({columns}) values({values})'.format(columns=','.join(SQL_ASSET_SAVE_COLUMNS), values=','.join(['%s'] * len(SQL_ASSET_SAVE_COLUMNS)))

SQL_ASSET_BY_ID = 'select id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status from asset where status!=2 and id=%s;'
SQL_ASSET_BY_IP = 'select id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status from asset where status!=2 and ip=%s;'

SQL_ASSET_MODIFY_COLUMNS = 'sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status'.split(',')
SQL_ASSET_MODIFY = 'update asset set {values} where id=%s and status!=2'.format(values=','.join(['{column}=%s'.format(column=column) for column in SQL_ASSET_MODIFY_COLUMNS]))

SQL_ASSET_DELETE = 'update asset set status=2 where id=%s'

SQL_MONITOR_HOST_CREATE = 'insert into monitor_host(ip, mem, cpu, disk, m_time, r_time) values(%s, %s, %s, %s, %s, %s)'
    
SQL_MONITOR_HOST_LIST = 'select m_time,cpu,mem,disk from monitor_host where ip=%s and r_time >=%s order by m_time asc'

SQL_ALERT_LIST_COLUMNS = 'id,ip,message,admin,status,type,c_time'.split(',')
SQL_ALERT_LIST = 'select id,ip,message,admin,status,type,c_time from alert where status!=2 order by c_time desc;'


SQL_ACCESSLOG_SAVE = 'insert into accesslog(a_time, ip, url, code, city_name) values(%s, %s, %s, %s, %s)'

SQL_GEOIP_CITY_NAME_EXISTS = 'select id from geoip where city_name=%s limit 1'
SQL_GEOIP_SAVE = 'insert into geoip(city_name, city_lat, city_lgt) values(%s, %s, %s)'

SQL_ACCESS_LIST = 'select ip,url,code,count(*) as cnt from accesslog group by ip, url, code order by cnt desc limit %s'

SQL_ACCESSLOG_CODE_DIST = 'select code, count(*) as cnt from accesslog where a_time >= %s group by code order by cnt desc'
SQL_ACCESSLOG_CODE_TIME_DIST = " select date_format(a_time, '%%Y-%%m-%%d %%H:00:00') as time, code, count(*) as cnt from accesslog group by time, code"

SQL_GEOIP_LIST = 'select city_name, city_lat, city_lgt from geoip'

SQL_ACCESS_IP_DIST = 'select city_name, count(*) as cnt from accesslog group by city_name'

def get_machine_rooms():
    rt_cnt, rt_list = dbutils.execute_sql(SQL_MACHINE_ROOM_LIST, (), True)
    return [dict(zip(SQL_MACHINE_ROOM_COLUMNS, rt)) for rt in rt_list]

def get_machine_rooms_index_by_id():
    rt_list = get_machine_rooms()
    rt_dict = {}
    for room in rt_list:
        rt_dict[room['id']] = room
    return rt_dict

def validate_machine_room_save(name, addr, ip_ranges):
    if name.strip() == '' or addr.strip() == '' or ip_ranges.strip() == '':
        return False, 'name, addr, ip_ranges is empty'
    return True, ''

def machine_room_save(name, addr, ip_ranges):
    dbutils.execute_sql(SQL_MACHINE_ROOM_SAVE, (name.strip(), addr.strip(), ip_ranges.strip()), False)
    return True

def machine_room_delete(mrid):
    dbutils.execute_sql(SQL_MACHINE_ROOM_DELETE, (mrid, ), False)
    return True

'''
[
(ip, url, code) : count
]
'''
def get_topn(topn=10):
    _, rt_list = dbutils.execute_sql(SQL_ACCESS_LIST, (topn, ), True)
    return rt_list

def get_assets():
    rt_cnt, rt_list = dbutils.execute_sql(SQL_ASSET_LIST, (), True)
    assets = []
    rooms = get_machine_rooms_index_by_id()
    for rt in rt_list:
        asset = dict(zip(SQL_ASSET_LIST_COLUMNS, rt))
        for key in 'time_on_shelves,over_guaranteed_date'.split(','):
            if asset[key]:
                asset[key] = asset[key].strftime('%Y-%m-%d')
        asset['machine_room_name'] = rooms.get(asset['machine_room_id'], {}).get('name', '')
        assets.append(asset)
    return assets

def validate_asset_save(req):
    return True, ''

def asset_save(req):
    values = []
    for column in SQL_ASSET_SAVE_COLUMNS:
        values.append(req.get(column, ''))

    rt_cnt, _ = dbutils.execute_sql(SQL_ASSET_SAVE, values, False)
    return rt_cnt != 0

def get_asset_by_id(aid):
    rt_cnt, rt_list = dbutils.execute_sql(SQL_ASSET_BY_ID, (aid,), True)
    assets = []
    for rt in rt_list:
        asset = dict(zip(SQL_ASSET_LIST_COLUMNS, rt))
        for key in 'time_on_shelves,over_guaranteed_date'.split(','):
            if asset[key]:
                asset[key] = asset[key].strftime('%Y-%m-%d')
        assets.append(asset)
    return assets[0] if assets else {}

def get_asset_by_ip(ip):
    rt_cnt, rt_list = dbutils.execute_sql(SQL_ASSET_BY_IP, (ip,), True)
    assets = []
    for rt in rt_list:
        asset = dict(zip(SQL_ASSET_LIST_COLUMNS, rt))
        for key in 'time_on_shelves,over_guaranteed_date'.split(','):
            if asset[key]:
                asset[key] = asset[key].strftime('%Y-%m-%d')
        assets.append(asset)
    return assets[0] if assets else {}

def validate_asset_modify(req):
    return True, ''

def asset_modify(req):
    values = []
    for column in SQL_ASSET_MODIFY_COLUMNS:
        values.append(req.get(column, ''))
    values.append(req.get('id', 0))
    rt_cnt, _ = dbutils.execute_sql(SQL_ASSET_MODIFY, values, False)
    return True

def asset_delete(aid):
    dbutils.execute_sql(SQL_ASSET_DELETE, (aid, ), False)
    return True

def monitor_host_create(req):
    values = []
    for key in ['ip', 'mem', 'cpu', 'disk', 'm_time']:
        values.append(req.get(key, ''))

    values.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    dbutils.execute_sql(SQL_MONITOR_HOST_CREATE, values, False)
    return True

def monitor_host_list(ip):
    start_time = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    rt_cnt, rt_list = dbutils.execute_sql(SQL_MONITOR_HOST_LIST, (ip, start_time), True)
    
    categoy_list, cpu_list, disk_list, mem_list = [], [], [], []

    for line in rt_list:
        categoy_list.append(line[0].strftime('%H:%M'))
        cpu_list.append(line[1])
        mem_list.append(line[2])
        disk_list.append(line[3])
    return {
      'categories' : categoy_list,
      'series' : [{
          'name': 'CPU',
          'data': cpu_list
      }, {
          'name': u'内存',
          'data': mem_list
      }, {
          'name': u'磁盘',
          'data': disk_list
      }]
    }

def get_alerts():
    rt_cnt, rt_list = dbutils.execute_sql(SQL_ALERT_LIST, (), True)
    alerts = []
    for rt in rt_list:
        alert = dict(zip(SQL_ALERT_LIST_COLUMNS, rt))
        for key in 'c_time'.split(','):
            if alert[key]:
                alert[key] = alert[key].strftime('%Y-%m-%d %H:%M:%S')
        alerts.append(alert)
    return alerts


class User(object):
    TABLE = 'user'
    KEY = 'id'
    SQL_LOGIN_COLUMNS = ('id', 'name')
    SQL_LOGIN = 'select id, name from user where name = %s and password = %s'

    SQL_LIST_COLUMNS = ('id', 'name', 'age')
    SQL_LIST = 'select id, name, age from user'

    SQL_SAVE = 'insert into user(name, age, password) values(%s, %s, %s)'


    SQL_GET_BY_KEY_COLUMNS = ('id', 'name', 'age')
    SQL_GET_BY_KEY = 'select id, name, age from user where {key}=%s'

    SQL_MODIFY = 'update user set name=%s, age=%s where id=%s'

    SQL_VALIDATE_PASSWORD = 'select id from user where id = %s and password = %s'

    SQL_PASSWORD_MODIFY = 'update user set password=%s where id=%s'

    SQL_DELETE_BY_KEY = 'delete from user where {key} = %s'

    def __init__(self, id, name, password, age):
        self.id = id
        self.name = name.strip()
        self.password = password.strip()
        self.age = age


    @classmethod
    def login(cls, username, password):
        _, rt_list = dbutils.execute_sql(cls.SQL_LOGIN, (username, crypt.md5_str(password)), True)
        return  dict(zip(cls.SQL_LOGIN_COLUMNS, rt_list[0])) if rt_list else None

    @classmethod
    def validate_password(cls, uid, password):
        rt_cnt, _ = dbutils.execute_sql(cls.SQL_VALIDATE_PASSWORD, (uid, crypt.md5_str(password)), True)
        return rt_cnt > 0

    @classmethod
    def get_list(cls):
        _, rt_list = dbutils.execute_sql(cls.SQL_LIST, (), True)
        return [dict(zip(cls.SQL_LIST_COLUMNS, line)) for line in rt_list]

    def validate_save(self):
        if self.name.strip() == '':
            return False, u'用户名不能为空'
        if len(self.name) > 25:
            return False, u'用户名长度不能大于25'
        if self.password == '':
            return False, u'密码不能为空'
        if len(self.password) < 6 or len(self.password) > 25:
            return False, u'密码长度必须在6到25之间'

        if not str(self.age).isdigit() or int(self.age) < 1 or int(self.age) > 100:
            return False, u'年龄必须在1到100之间'
        
        user = self.get_by_key(self.name, 'name')
        if user:
            return False, u'用户名不能重复'

        return True, ''

    def save(self):
        rt_cnt, _ = dbutils.execute_sql(self.SQL_SAVE, (self.name,
                                                        self.age,
                                                        crypt.md5_str(self.password),), False)
        return rt_cnt != 0

    @classmethod
    def get_by_key(cls, value, key=None):
        sql = cls.SQL_GET_BY_KEY.format(key=cls.KEY if key is None else key)

        _, rt_list = dbutils.execute_sql(sql, (value, ), True)
        return dict(zip(cls.SQL_GET_BY_KEY_COLUMNS, rt_list[0])) if rt_list else None

    def validate_modify(self):
        if not self.get_by_key(self.id):
            return False, u'用户不存在'

        if self.name == '':
            return False, u'用户名不能为空'
        if len(self.name) > 25:
            return False, u'用户名长度不能大于25'
    
        if not str(self.age).isdigit() or int(self.age) < 1 or int(self.age) > 100:
            return False, u'年龄必须在1到100之间'

        user = self.get_by_key(self.name, 'name')
        if user and str(user['id']) != str(self.id):
            return False, u'用户名不能重复'

        return True, ''

    def modify(self):
        dbutils.execute_sql(self.SQL_MODIFY, (self.name, self.age, self.id), False)
        return True

    def validate_password_modify(self):
        if not self.get_by_key(self.id):
            return False, u'用户不存在'
        
        if self.password == '':
            return False, u'密码不能为空'

        if len(self.password) < 6 or len(self.password) > 25:
            return False, u'密码长度必须在6到25之间'
        return True, ''

    def password_modify(self):
        dbutils.execute_sql(self.SQL_PASSWORD_MODIFY, (crypt.md5_str(self.password), self.id), False)
        return True

    @classmethod
    def delete_by_key(cls, value, key=None):
        sql = cls.SQL_DELETE_BY_KEY.format(key=cls.KEY if key is None else key)

        dbutils.execute_sql(sql, (value, ), False)
        return True


def access_log_import(filename):
    if os.path.exists(filename):
        fhandler = None
        geo_reader = None
        db_connection = None
        db_cursor = None
        try:
            fhandler = open(filename, 'rb')
            geo_reader = geoip2.database.Reader(gconf.GEOLITE)
            # db_connection = MySQLdb.connect(host=gconf.MYSQL_HOST, \
            #                                 port=gconf.MYSQL_PORT, \
            #                                 user=gconf.MYSQL_USER, \
            #                                 passwd=gconf.MYSQL_PASSWD, \
            #                                 db=gconf.MYSQL_DB, \
            #                                 charset=gconf.MYSQL_CHARSET)
            # db_cursor = db_connection.cursor()
            db_connection = dbutils.MySQLConnection(host=gconf.MYSQL_HOST, \
                                            port=gconf.MYSQL_PORT, \
                                            user=gconf.MYSQL_USER, \
                                            passwd=gconf.MYSQL_PASSWD, \
                                            db=gconf.MYSQL_DB)
            line_count = 0
            for line in fhandler:
                try:
                    elements = line.split()
                    #time, ip, url, code
                    
                    a_time = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(elements[3], '[%d/%b/%Y:%H:%M:%S'))
                    ip = elements[0]
                    url = elements[6]
                    code = elements[8]
                    response = geo_reader.city(ip)
                    
                    if response.country.names.get('en', '').lower() == 'china':
                        city_name = response.city.names.get('zh-CN', '')
                        if city_name:
                            city_lat = response.location.latitude
                            city_lgt = response.location.longitude
                            print ip, url, code, city_name, city_lat, city_lgt
                            # db_cursor.execute(SQL_ACCESSLOG_SAVE, (a_time, ip, url, code, city_name))
                            db_connection.execute_sql(SQL_ACCESSLOG_SAVE, (a_time, ip, url, code, city_name), False)

                            if 0 == db_connection.execute_sql(SQL_GEOIP_CITY_NAME_EXISTS, (city_name, ))[0]:
                                db_connection.execute_sql(SQL_GEOIP_SAVE, (city_name, city_lat, city_lgt))
                            line_count += 1

                            if line_count == 1000:
                                db_connection.commit()
                                line_count = 0

                except BaseException as e:
                    print e
        except BaseException as e:
            print e 
        finally:
            db_connection.close()
            if geo_reader:
                geo_reader.close()
            if fhandler:
                fhandler.close()
                os.unlink(filename)

def accesslog_code_dist():
    start_time = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d %H:%M:%S')
    _, rt_list = dbutils.execute_sql(SQL_ACCESSLOG_CODE_DIST, (start_time, ), True)
    legend = []
    data = []

    for line in rt_list:
        legend.append(line[0])
        data.append({'value' : line[1], 'name' : line[0]})
    
    return legend, data

def accesslog_code_time_dist():
    legend = []
    xAxis = []
    data = []

    temp_data = {}

    _, rt_list = dbutils.execute_sql(SQL_ACCESSLOG_CODE_TIME_DIST, (), True)
    for line in rt_list:

        if line[0] not in xAxis:
            xAxis.append(line[0]) # time
        if line[1] not in legend:
            legend.append(line[1]) # code

        #line[2] # count
        temp_data.setdefault(line[1], {})
        temp_data[line[1]][line[0]] = line[2]

    xAxis.sort()

    for code in temp_data:
        code_time_data = []
        for time in xAxis:
            code_time_data.append(temp_data[code].get(time, 0))
        data.append({'name' : code, 'type' : 'bar', 'stack' : 'code', 'data' : code_time_data})        

    return legend, xAxis, data

def accesslog_ip_dist():
    legend =[] 
    geoCoord = {}
    markline_data = []
    markpoint_data = []


    server_ip = '1.202.78.231'

    geo_reader = geoip2.database.Reader(gconf.GEOLITE)
    server_response = geo_reader.city(server_ip)
    geo_reader.close()
    
    server_city_name = server_response.city.names.get('zh-CN', u'北京')
    legend.append(server_city_name)

    geoCoord[server_city_name] = [server_response.location.longitude, server_response.location.latitude]
    
    _, rt_list = dbutils.execute_sql(SQL_GEOIP_LIST, (), True)

    for line in rt_list:
        geoCoord[line[0]] = [line[2], line[1]]
    
    _, rt_list = dbutils.execute_sql(SQL_ACCESS_IP_DIST, (), True)
    for line in rt_list:
        markline_data.append([{'name' : line[0]}, {'name' : server_city_name, 'value' : line[1]}])
        markpoint_data.append({'name': line[0], 'value' : line[1]})

    return legend, geoCoord, markline_data, markpoint_data

if __name__ == '__main__':
    for i in xrange(100):
        user_save('name-%s' % i, '123456', 29)
