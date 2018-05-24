#encoding: utf-8

import paramiko
import traceback

def exec_cmds(host, port, username, password, cmds=[]):
    client = paramiko.SSHClient()
    rt_list = []
    error = ''
    try:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port, username, password)

        for cmd in cmds:
            stdin, stdout, stderr = client.exec_command(cmd)
            output = stdout.readlines()
            error = stderr.readlines()
            rt_list.append([cmd, output, error])
    except paramiko.AuthenticationException as e:
        print u'用户名密码错误'
        print e
        error = '用户名密码错误'
    except BaseException as e:
        print u'未知错误'
        print e
        error = '未知错误'

    client.close()
    return error, rt_list

'''
[
(local, remote),
]
'''
def upload_files(host, port, username, password, files=[]):
    t = paramiko.Transport((host, port))
    rt_list = []
    try:
        t.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        for local, remote in files:
            sftp.put(local, remote)
            rt_list.append([local, remote])
    except paramiko.AuthenticationException as e:
        print u'用户名密码错误'
        print e
    except BaseException as e:
        print u'未知错误'
        print e
        print traceback.format_exc()
    
    t.close()
    return rt_list

if __name__ == '__main__':
  
    files = [('/home/kk/class11/kk/11/agent/agent.py', '/tmp/kk/agent.py')]
    print upload_files('139.198.9.46', 22010, 'root', 'Reboot11.xuezm', files)
    cmds = [
        # 'yum install -y python-devel',
        # 'yum install -y python-pip',
        # 'pip install psutil',
        # 'pip install requests',
        "ps aux | grep python| grep agent.py | grep -v grep | awk '{print $2}' | xargs kill -9",
        'nohup python /tmp/kk/agent.py 59.110.12.72 10000 >/dev/null 2>&1 &',
    ]
    print exec_cmds('139.198.9.46', 22010, 'root', 'Reboot11.xuezm', cmds)