#encoding: utf-8
import os

MYSQL_HOST = os.environ.get('MYSQL_ADDR', '192.168.11.61')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_USER = os.environ.get('MYSQL_USERNAME', 'jmyd')
MYSQL_PASSWD = os.environ.get('MYSQL_PASSWORD', 'dba@123456')
MYSQL_DB =os.environ.get('MYSQL_DB', 'cmdb_test')
MYSQL_CHARSET = 'utf8'

GEOLITE = 'GeoLite2-City.mmdb'
