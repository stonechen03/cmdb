#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/11/20'

from conf import conf
from conf import log
import redis
from asset.models import Asset
import base64
import json


def redis_connect():
    cfg = conf.CACHES["monitor"]
    if cfg["password"] == "":
        pool = redis.ConnectionPool(host=cfg["host"], port=cfg["port"], db=cfg["db"])
    else:
        pool = redis.ConnectionPool(host=cfg["host"], port=cfg["port"], db=cfg["db"], password=cfg["password"])
    return redis.Redis(connection_pool=pool)


def base64_ip(id):
    try:
        asset = Asset.objects.get(id=id)
    except Exception as e:
        log.error(e)
        return False
    ip = asset.ip
    other_ip = asset.other_ip
    if other_ip == '':
        ips_list = [ip]
    else:
        ips_list = [ip, other_ip]
    return base64.encodestring(','.join(ips_list)).split('\n')[0].split('=')[0]


class MonitorInfoGet(object):
    def __init__(self, id):
        self.id = id
        self.datas = None
        self.cli = redis_connect()
        self.base_ip = base64_ip(self.id)

    def get_network_info(self, net_card):
        network_info = {'bytes_recv': [], 'bytes_sent': [], 'date': []}

        try:
            self.datas = self.cli.lrange('network_{}_list'.format(self.base_ip), 0, -1)  # 获取所有数据列表
            log.debug(self.datas)
            for key in self.datas:
                data_list = self.cli.lrange(key + net_card, 0, -1)  # 获取单条数据
                for info in data_list:
                    info = json.loads(info)
                    network_info['bytes_sent'].insert(0, info['bytes_sent'])
                    network_info['bytes_recv'].insert(0, info['bytes_recv'])
                    network_info['date'].insert(0, info['date'])
            log.debug(network_info)
        except Exception as e:
            log.error(e)
        return network_info
