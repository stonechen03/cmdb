#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/12/14'

import psutil
import time
import redis
from multiprocessing import Pool
import netifaces
import base64
import signal
import os

config = {
	'redis': {
		'ip': '10.0.20.110',
		'port': '6379',
		'password': '',
		'db': '2'
	},
	'pid': './monitor.pid'
}


def write_file(init=False, pid=None):
	if init:
		with open(config['pid'], 'w') as f:
			f.write(pid)
			f.write('\n')
	else:
		with open(config['pid'], 'a') as f:
			f.write(pid)
			f.write('\n')


if config.get('password') != '':
	pool = redis.ConnectionPool(host=config['redis']['ip'], port=config['redis']['port'], db=config['redis']['db'], password=config['redis']['password'])
else:
	pool = redis.ConnectionPool(host=config['redis']['ip'], port=config['redis']['port'], db=config['redis']['db'])
redis_cli = redis.Redis(connection_pool=pool)


def init_worker():
	signal.signal(signal.SIGINT, signal.SIG_IGN)


def get_ip_base():
	"""
	:return: ip加密值
	"""
	ips = []
	for interface in netifaces.interfaces():
		if interface != 'lo':
			ips.append(netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr'])
	ip_hash_base = base64.encodestring(','.join(ips))
	return ip_hash_base.split('\n')[0]


def bytes2human(n):
	"""
	>>> bytes2human(10000)
	'9.8 K'
	>>> bytes2human(100001221)
	'95.4 M'
	"""
	symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
	prefix = {}
	for i, s in enumerate(symbols):
		prefix[s] = 1 << (i + 1) * 10
	for s in reversed(symbols):
		if n >= prefix[s]:
			value = float(n) / prefix[s]
			return '%.2f %s' % (value, s)
	return '%.2f B' % (n)


def subscribe():
	write_file(init=False, pid=os.getpid())
	sub = redis_cli.pubsub()
	sub.subscribe('__keyevent@2__:expired')
	while True:
		__data = sub.parse_response()
		print __data
		if __data[0] == 'message':
			redis_cli.srem(__data[2].split('=')[0] + '_list', __data[2])


def get_network_info():
	write_file(init=False, pid=os.getpid())
	while True:
		pnic_before = psutil.net_io_counters(pernic=True)
		time.sleep(10)
		pnic_after = psutil.net_io_counters(pernic=True)
		nic_names = list(pnic_after.keys())
		nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)
		nic_names.remove('lo')
		data = {}
		key = 'network_{}{}'.format(get_ip_base(), time.strftime("%y%m%d%H:%M", time.localtime()))
		key_list = 'network_{}_list'.format(get_ip_base().split('=')[0])
		date = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
		for name in nic_names:
			stats_before = pnic_before[name]
			stats_after = pnic_after[name]
			data['date'] = date
			data['dev'] = name
			data['bytes_sent'] = bytes2human(stats_after.bytes_sent - stats_before.bytes_sent) + '/s'
			data['bytes_recv'] = bytes2human(stats_after.bytes_recv - stats_before.bytes_recv) + '/s'
			data['packets_sent'] = stats_after.packets_sent - stats_before.packets_sent
			data['packets_recv'] = stats_after.packets_recv - stats_before.packets_recv
			redis_cli.rpush(key, data)
			redis_cli.sadd(key_list, key)
			redis_cli.expire(key, 60)

try:
	write_file(init=True, pid=os.getpid())
	pool = Pool(processes=2, initializer=init_worker)
	pool.apply_async(subscribe)
	pool.apply_async(get_network_info)
	pool.close()
	while True:
		pass
except KeyboardInterrupt:
	import sys
	with open(config['pid'], 'r') as f:
		pids = f.readlines()
		for pid in pids:
			os.kill(int(pid), signal.SIGKILL)
	sys.exit(0)
