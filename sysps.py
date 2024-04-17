# -*- coding: utf-8 -*-
'''
@name: sys info
@author: guozhenyi
@date: 2024-04-03
@version: 0.1
'''

import os
import re
import sys
import socket
import subprocess
from typing import Dict, Any

def _run(args):
    return subprocess.run(args, shell=True, stdout=subprocess.PIPE).stdout.decode()

def is_win():
    return os.name == 'nt'

def is_linux():
    return sys.platform.startswith('linux')

def byte_to_str(num: int) -> str:
    if not num:
        return ''

    kb = 1024
    mb = kb * 1024
    gb = mb * 1024
    tb = gb * 1024

    if num >= tb:
        return str(round(num / gb, 1)) + 'TB' # as TiB
    if num >= gb:
        return str(round(num / gb, 1)) + 'GB' # as GiB
    if num >= mb:
        return str(round(num / mb, 1)) + 'MB' # as MiB
    if num >= kb:
        return str(round(num / kb, 1)) + 'KB' # as KiB

    return str(num) + 'B'

def get_local_ip() -> str:
    """获取局域网 IP
    Returns:
        str: _description_
    """
    # ip = socket.gethostbyname(socket.gethostname())
    ip = _run("hostname -I |awk '{print $1}'").strip()
    return ip

def get_mac_addr() -> str:
    """获取 MAC 地址
    Returns:
        str: MAC 地址
    """
    mac = _run("cat /sys/class/net/$(ip ro |awk 'NR==1{print $5}')/address").strip()
    return mac

def get_host_name() -> str:
    """获取主机名
    Returns:
        str: _description_
    """
    # name = socket.gethostname()
    name = _run("hostname").strip()
    return name

def get_serial_num() -> str:
    """获取服务器序列号
    Returns:
        str: _description_
    """
    sn = _run("dmidecode -s system-serial-number").strip()
    return sn

def get_product_name() -> str:
    """获取服务器的型号
    Returns:
        str: _description_
    """
    pn = _run("dmidecode -s system-product-name")
    return pn

def get_linux_cpu() -> Dict[str, Any]:

    cpu = _run('top -b -n1 | fgrep "Cpu(s)"')
    cpu_ids = [a for a in cpu.split(',') if 'id' in a]
    if len(cpu_ids):
        cpu_id = cpu_ids[0]
        cpu_id_m = re.findall(r'\d*\.?\d+', cpu_id)
        if (len(cpu_id_m)):
            cpu_used = round(100 - float(cpu_id_m[0]), 2)

    # cpu_core = int(_run('grep -c "model name" /proc/cpuinfo').split('\n')[0])
    cpu_core = int(_run('cat /proc/cpuinfo |grep processor |wc -l').strip())

    return {
        "used": cpu_used, # cpu使用率
        "core": cpu_core,  # cpu内核数
        # "count": 0, # CPU数量
        # "name": "", # CPU名称
        # "threads": 0 # 线程数
    }

def get_linux_mem() -> Dict[str, Any]:

    mem_lst = _run("free -b | grep Mem | awk '{print $2,$3,$4}'").split()
    mem_lst = [int(a) for a in mem_lst]

    # print('mem_lst', mem_lst)

    m_use = round(mem_lst[1] / mem_lst[0] * 1000)
    if (m_use % 10 == 0):
        usage = int(m_use / 10)
    else:
        usage = round(m_use / 10, 1)

    return {
        "total": mem_lst[0],
        # "used": mem_lst[1],
        "free": mem_lst[2],
        "usage": usage,
        "str_total": byte_to_str(mem_lst[0]),
        "str_free": byte_to_str(mem_lst[2]),
    }

def get_linux_disk(path:str = '/') -> Dict[str, Any]:

    result = {
        "total": 0,
        # "used": 0,
        "free": 0,
        "usage": 0,
        "str_total": "",
        "str_free": "",
    }

    # disk_lst = shell_run("df -BK %s | awk 'NR==2{print $2,$3,$4}'" % path).replace('K', '').split()
    disk_s = _run("df -BK %s | awk 'NR==2{print $2,$3,$4}'" % path)
    if 'No such' in disk_s or '没有' in disk_s:
        return result

    disk_lst = disk_s.replace('K', '').split()
    disk_lst = [int(int(a) * 1024) for a in disk_lst]

    # print('disk_lst', disk_lst)

    d_use = round(disk_lst[1] / disk_lst[0] * 1000)
    if (d_use % 10 == 0):
        usage = int(d_use / 10)
    else:
        usage = round(d_use / 10, 1)

    result['total'] = disk_lst[0]
    result['free'] = disk_lst[2]
    result['usage'] = usage
    result['str_total'] = byte_to_str(disk_lst[0])
    result['str_free'] = byte_to_str(disk_lst[2])

    return result


def GetHostInfo() -> Dict[str, Any]:
    name = socket.gethostname()
    ip = socket.gethostbyname(name)
    return {
        "ip": ip,
        "name": name,
    }

def GetCpuInfo() -> Dict[str, Any]:

    result_cpu = {
        "used": 0,
        "core": 0
    }

    if is_linux():
        result_cpu = get_linux_cpu()

    return result_cpu

def GetMemInfo() -> Dict[str, Any]:

    result_mem = {
        "total": 0,
        "free": 0,
        "usage": 0,
        "str_total": "",
        "str_free": "",
    }

    if is_linux():
        result_mem = get_linux_mem()

    return result_mem

def GetDiskSysInfo() -> Dict[str, Any]:

    result_disk = {
        "total": 0,
        "free": 0,
        "usage": 0,
        "str_total": "",
        "str_free": "",
    }

    if is_linux():
        result_disk = get_linux_disk('/')

    return result_disk

def GetSystemInfo() -> Dict[str, Any]:
    result = {
        "cpu": {
            "used": 0,
            "core": 0,
        },
        "mem": {
            "total": 0,
            "free": 0,
            "usage": 0,
            "str_total": "",
            "str_free": "",
        },
        "disk": {
            "total": 0,
            "free": 0,
            "usage": 0,
            "str_total": "",
            "str_free": "",
        },
        "sys_disk": {
            "total": 0,
            "free": 0,
            "usage": 0,
            "str_total": "",
            "str_free": "",
        },
        "ip_addr": "",
    }

    if is_linux():
        result["cpu"] = get_linux_cpu()
        result["mem"] = get_linux_mem()
        result['sys_disk'] = get_linux_disk('/')
        result["ip_addr"] = get_local_ip()

    return result



# if __name__ == '__main__':
    # GetCpuInfo()
    # GetMemInfo()
    # GetDiskSysInfo()
