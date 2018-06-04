#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/11/29'

# debug
DEBUG = True

LOG_LEVEL = 'INFO'

# database
DATABASES = {
    "default": {
        "name": "ops",
        "user": "root",
        "password": "root",
        "host": "127.0.0.1",
        "port": "3306",
    },
}

# redis
CACHES = {
    "default": {
        "host": "127.0.0.1",
        "port": 6379,
        "db": 1,
        "password": "",
    },
    "monitor": {
        "host": "10.0.20.110",
        "port": 6379,
        "db": 2,
        "password": "",
    }
}

# email
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'test@test.com'
EMAIL_HOST_PASSWORD = '123456'
EMAIL_USE_SSL = True
EMAIL_TIMEOUT = 5
EMAIL_FORM_USER = EMAIL_HOST_USER

# web ssh
port = 8888
address = "127.0.0.1"
log_file_prefix = "../../log/webssh.log"
logging = "error"
log_to_stderr = False
log_file_max_size = 2 * 1024 * 1024
log_file_num_backups = 7
