#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/11/9'

from asset.models import Asset
from ansible_api import MyRunner
from paramiko.rsakey import RSAKey
import logging
import os
from django.conf import settings

log = logging.getLogger('django')


def get_host_list(host_id_list=None, asset_group_id=None, user=''):
    """
    通过ID获取主机信息, 传其一即可
    :param host_id_list: 主机ID 必须为list类型
    :param asset_group_id: 资产ID 必须为int
    :param user: 登录用户
    :return: 主机列表
    """

    host_list = []
    user_key = settings.BASE_DIR + '/upload/key/' + user + '/' + user
    if host_id_list is not None and isinstance(host_id_list, list):
        id_list = host_id_list
        for id in id_list:
            try:
                asset = Asset.objects.get(id=id)
            except Exception as e:
                log.error(e)
                return False
            host_dict = {}
            host_dict['hostname'] = asset.ip
            host_dict['port'] = asset.port
            host_dict['username'] = asset.username
            if user:
                host_dict['ssh_key'] = user_key
            else:
                host_dict['password'] = asset.password
            host_list.append(host_dict)
    elif asset_group_id is not None and isinstance(asset_group_id, int):
        host_all = Asset.objects.filter(group=asset_group_id)
        for host in host_all:
            host_dict = {}
            host_dict['hostname'] = host.ip
            host_dict['port'] = host.port
            host_dict['username'] = host.username
            if user:
                host_dict['ssh_key'] = user_key
            else:
                host_dict['password'] = host.password
            host_list.append(host_dict)

    return host_list


def get_host_info(hosts):
    """
    获取主机资产信息
    :param hosts:主机列表
    :return:
    """

    setup_info = ''

    runner = MyRunner(hosts)
    data = runner.run(module_name='setup', module_args='')

    result = {}
    for k, v in data.items():
        if k == 'dark':
            for host, info in v.items():
                result[host] = {'dark': info.get('msg')}
                log.error(result[host])
        elif k == 'contacted':
            for host, info in v.items():
                disk = {}

                try:
                    setup_info = data['contacted'][host]['ansible_facts']
                except Exception as e:
                    log.error(data['contacted'])
                    continue
                disk_indo = setup_info.get("ansible_devices")
                for disk_name, disk_info in disk_indo.iteritems():
                    if disk_name.startswith('sd') or disk_name.startswith('hd') or disk_name.startswith('vd') or disk_name.startswith('xvd'):
                        disk[disk_name] = disk_info.get('size', '')

                try:
                    cpu_type = setup_info.get("ansible_processor")[1]
                except IndexError:
                    cpu_type = ' '.join(setup_info.get("ansible_processor")[0].split(' ')[:6])
                cpu_cores = setup_info.get("ansible_processor_vcpus")
                cpu = cpu_type + ' * ' + unicode(cpu_cores)

                other_ip_list = []
                for i in setup_info.get('ansible_all_ipv4_addresses'):
                    if i != host:
                        other_ip_list.append(i)
                other_ip = ','.join(other_ip_list) if other_ip_list else ''
                mac = setup_info.get("ansible_default_ipv4").get("macaddress")
                memory = setup_info.get("ansible_memtotal_mb")
                system_type = setup_info.get("ansible_distribution")
                system_version = setup_info.get("ansible_distribution_version")
                system_arch = setup_info.get("ansible_architecture")
                kernel = setup_info.get("ansible_kernel")
                brand = setup_info.get("ansible_product_name")
                sn = setup_info.get("ansible_product_serial")
                hostname = setup_info.get("ansible_fqdn")
                try:
                    asset = Asset.objects.get(ip=host)
                    asset.disk = disk
                    asset.other_ip = other_ip
                    asset.mac = mac
                    asset.cpu = cpu
                    asset.memory = memory
                    asset.hostname = hostname
                    asset.system_type = system_type
                    asset.system_arch = system_arch
                    asset.system_version = system_version
                    asset.kernel = kernel
                    asset.brand = brand
                    asset.sn = sn
                    asset.save()
                except Exception as e:
                    log.error(e)
                    return False

    return result


def push_key(hosts, key_path):
    """
    :param hosts: 主机列表
    :param key_path: 私钥路径
    :return:
    """

    faild_host = []
    for host in hosts:
        module_args = 'user="%s" key="{{ lookup("file", "%s") }}" state=present' % (host['username'], key_path)
        runner = MyRunner([host])
        data = runner.run(module_name='authorized_key', module_args=module_args)
        if len(data['dark']) > 0:
            faild_host.append(host['hostname'])
    return faild_host


def get_host_disk(hosts):
    runner = MyRunner(hosts)
    datas = runner.run(module_name="shell", module_args="df -hP | awk 'NR>1' | awk '{print $1,$2,$3,$4,$5}'")
    for host in hosts:
        stdout = datas['contacted'][host['hostname']]['stdout'].split('\n')
        for data in stdout:
            pass

    return stdout


def get_host_monitor(hosts):
    runner = MyRunner(hosts)
    datas = runner.run(module_name="shell",
                       module_args="cat /tmp/host_info_back.info | awk 'NR>2''{print $4,$5,$6,$9,$10,$13,$14,$15,$18,$19}' | sed 's/\s\+/,/g'")
    data_lists = []
    from monitor.models import MonitorInfo

    for host in hosts:
        asset = Asset.objects.get(ip=host['hostname'])
        stdout = datas['contacted'][host['hostname']]
        data_list = stdout['stdout'].split("\n")
        for info in data_list:
            info_list = info.split(",")
            db = MonitorInfo(
                mem_free=info_list[0],
                mem_cache=info_list[1],
                mem_buff=info_list[2],
                io_bi=info_list[3],
                io_bo=info_list[4],
                cpu_use=info_list[5],
                cpu_sys=info_list[6],
                cpu_idle=info_list[7],
                ip=asset,
                monitor_time=info_list[8] + ' ' + info_list[9]
            )
            data_lists.append(db)
    try:
        dbs = MonitorInfo.objects.bulk_create(data_lists)
    except Exception as e:
        log.info(e)
        return False
    return True


def gen_keys(user):
    """
    生成秘钥
    :param user: 用户
    :return:
    """

    key_dir = settings.BASE_DIR + '/upload/key/' + user + '/'
    if not os.path.isdir(key_dir):
        os.makedirs(key_dir)

    private_key = key_dir + user
    public_key = key_dir + user + '.pub'
    if not os.path.isfile(private_key):
        key = RSAKey.generate(2048)
        key.write_private_key_file(private_key)
        os.chmod(private_key, 0600)
        with open(public_key, 'w') as content_file:
            for data in [key.get_name(),
                         " ",
                         key.get_base64(),
                         " %s@%s" % (user, os.uname()[1])]:
                content_file.write(data)
        return True
    else:
        return False


def del_keys(user):
    """
    删除秘钥
    :param user: 用户
    :return:
    """

    import os, shutil
    from django.conf import settings
    key_dir = settings.BASE_DIR + '/upload/key/' + user
    if os.path.isdir(key_dir):
        shutil.rmtree(key_dir)
    return True
