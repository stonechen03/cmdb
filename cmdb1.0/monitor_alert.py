#encoding: utf-8

import datetime
import json
import time

from utils import dbutils
from utils import mail
from cmdb import models


INTERVAL_FETCH = 5
INTERVAL_SLEEP = 60

DEFAULT_ADMIN = '786725806@qq.com'

policies = {
    'cpu' : {'count' : 3, 'ceil' : 1},
    'mem' : {'count' : 3, 'ceil' : 12.9},
    'disk' : {'count' : 3, 'ceil' : 19},
}

SQL_SELECT_MONITOR_HOST_COLUMNS = {1 : 'cpu', 2 : 'mem', 3 : 'disk'}
SQL_SELECT_MONITOR_HOST = 'select ip, cpu, mem, disk from monitor_host where r_time >= %s'

SQL_ALERT_CREATE = 'insert into alert(ip, message, admin, status, type, c_time) values(%s, %s, %s, 1, 1, %s)'



def monitor_alert():
    while True:
        c_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        r_time = (datetime.datetime.now() - datetime.timedelta(minutes=INTERVAL_FETCH)).strftime('%Y-%m-%d %H:%M:%S')
        _, rt_list = dbutils.execute_sql(SQL_SELECT_MONITOR_HOST, (r_time, ), True)
        rt_dict = {}
        #ip : {'cpu' : 0, 'mem' : 0, 'disk' : 0}
        for line in rt_list:
            rt_dict.setdefault(line[0], {'cpu' : 0, 'mem' : 0, 'disk' : 0})
            for key, value in SQL_SELECT_MONITOR_HOST_COLUMNS.items():
                if line[key] >= policies[value]['ceil']:
                    rt_dict[line[0]][value] += 1


        for key in rt_dict:
            messages = []
            for resource in SQL_SELECT_MONITOR_HOST_COLUMNS.values():
                if rt_dict[key][resource] > policies[resource]['count']:
                    messages.append(u'%s超过%s分钟内%s次超过阈值%s%%' % (resource, INTERVAL_FETCH, policies[resource]['count'], policies[resource]['ceil']))
            
            if messages:
                print json.dumps([key, messages], ensure_ascii=False)
                asset = models.get_asset_by_ip(key)
                admin = asset.get('admin', DEFAULT_ADMIN)
                if admin != DEFAULT_ADMIN:
                    admin = [admin, DEFAULT_ADMIN]

                dbutils.execute_sql(SQL_ALERT_CREATE, (key, ','.join(messages), ','.join(admin), c_time), False)
                mail.send_mail(admin, '<br/>'.join(messages), u'主机资源告警')
        
        time.sleep(INTERVAL_SLEEP)      

if __name__ == '__main__':
    monitor_alert()
    pass