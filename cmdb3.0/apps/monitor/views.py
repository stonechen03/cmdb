# coding:utf-8
from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import JsonResponse
from utils.utils import LoginRequiredMixin
from models import MonitorInfo
from asset.models import Asset
from public.redis_api import redis_connect, base64_ip
from conf import log

# Create your views here.


class MonitorView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'monitor/index.html')


class MonitorDataView(LoginRequiredMixin, View):
    def get(self, request):
        ip = request.GET.get('ip', None)
        datas = MonitorInfo.objects.filter(ip='10.0.20.110')
        time_list = []
        data = {}
        if request.GET.get('type', None) == 'disk':
            io_list = []
            bi_list = []
            for da in datas:
                time_list.append(da.monitor_time)
                io_list.append(da.io_bo)
                bi_list.append(da.io_bi)
            data['categories'] = time_list
            data['bo'] = io_list
            data['bi'] = bi_list
            return JsonResponse(data)
        elif request.GET.get('type', None) == 'cpu':
            cpu_use_list = []
            cpu_sys_list = []
            cpu_idle_list = []
            for da in datas:
                time_list.append(da.monitor_time)
                cpu_sys_list.append(da.cpu_sys)
                cpu_use_list.append(da.cpu_use)
                cpu_idle_list.append(da.cpu_idle)
            data['categories'] = time_list
            data['cpu_sys'] = cpu_sys_list
            data['cpu_use'] = cpu_use_list
            data['cpu_idle'] = cpu_idle_list
            return JsonResponse(data)
        elif request.GET.get('type', None) == 'mem':
            mem_free_list = []
            mem_buff_list = []
            mem_cache_list = []
            for da in datas:
                time_list.append(da.monitor_time)
                mem_buff_list.append(da.mem_buff)
                mem_cache_list.append(da.mem_cache)
                mem_free_list.append(da.mem_free)
            data['categories'] = time_list
            data['mem_buff'] = mem_buff_list
            data['mem_cache'] = mem_cache_list
            data['mem_free'] = mem_free_list
            return JsonResponse(data)


class NetworkView(LoginRequiredMixin, View):
    def get(self, request):
        id = request.GET.get('asset_id', None)
        base_ip = base64_ip(id=id)
        if request.is_ajax():
            from public.redis_api import MonitorInfoGet
            monitor = MonitorInfoGet(id)
            data = monitor.get_network_info(net_card='ens192')
            data['categories'] = ["bytes_recv", "bytes_sent"]
            return JsonResponse(data, safe=False)

        redis_cli = redis_connect()
        net_cards = redis_cli.smembers('network_NetCard_{}'.format(base_ip))
        return render(request, 'monitor/jiankong.html', {
            'net_cards': net_cards
        })
