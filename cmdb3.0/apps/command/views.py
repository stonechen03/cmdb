# coding: utf-8
from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import JsonResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from utils.utils import LoginRequiredMixin

from asset.models import AssetGroup, Upload
from public.asset_api import get_host_list
from public.ansible_api import MyRunner
from public.get_menu_api import Menu
from conf import log

# Create your views here.
menu = Menu(4)


def get_asset_group():
    """
    获取资产组
    :return: 资产id，name
    """

    return AssetGroup.objects.all().only("id", "name")


class CommandView(LoginRequiredMixin, View):
    """
    命令执行
    """

    def get(self, request):
        group_all = get_asset_group()

        return render(request, 'command/command.html', {
            "group_all": group_all,
            "menu": menu.get_menu(1),
        })

    def post(self, request):
        asset_group_id = request.POST.get("asset_id", None)
        module_name = request.POST.get("module_name", None)
        module_args = request.POST.get("module_args", None)

        host_list = get_host_list(asset_group_id=int(asset_group_id), user=request.user.username)
        runner = MyRunner(host_list)
        command = runner.run(module_name=module_name, module_args=module_args)
        command_info = {'faild': {}, 'successful': {}}
        if len(command['dark']) != 0:  # 无法连接的主机
            for faild_host in command['dark']:
                command_info['faild'][faild_host] = command['dark'][faild_host]['msg']
        for succes_host in command['contacted']:
            if command['contacted'][succes_host].has_key('failed'):  # 命令执行失败的主机
                command_info['faild'][succes_host] = command['contacted'][succes_host]['msg']
            else:  # 执行成功主机
                command_info['successful'][succes_host] = command['contacted'][succes_host]['stdout']
        data = {'code': 0, 'msg': '', 'data': command_info}
        return JsonResponse(data)


class DownloadFileView(LoginRequiredMixin, View):
    """
    下载文件
    """

    def get(self, request):
        group_all = get_asset_group()
        return render(request, 'command/downloadfile.html', {
            "group_all": group_all,
            "menu": menu.get_menu(2),
        })

    def post(self, request):
        from forms import DownloadFileForm
        download_form = DownloadFileForm(request.POST)
        data = {'code': 0, 'msg': '', 'data': ''}

        if download_form.is_valid():
            asset_group_id = request.POST.get('asset_id', None)
            module_name = 'get_url'
            url = request.POST.get('module_args_url', None)
            dest = request.POST.get('module_args_dest', None)
            checksum = request.POST.get('module_args_checksum', None)
            if checksum:
                module_args = "url=%s dest=%s checksum=%s" % (url, dest, checksum)
            else:
                module_args = "url=%s dest=%s" % (url, dest)
            host_list = get_host_list(asset_group_id=int(asset_group_id), user=request.user.username)
            runner = MyRunner(host_list)
            command = runner.run(module_name=module_name, module_args=module_args)
            command_info = {'faild': {}, 'successful': {}}
            if len(command['dark']) != 0:  # 无法连接的主机
                for faild_host in command['dark']:
                    command_info['faild'][faild_host] = command['dark'][faild_host]['msg']
            for succes_host in command['contacted']:
                if command['contacted'][succes_host].has_key('failed'):  # 命令执行失败的主机
                    command_info['faild'][succes_host] = command['contacted'][succes_host]['msg']
                else:  # 执行成功主机
                    command_info['successful'][succes_host] = command['contacted'][succes_host]
            data['data'] = command_info
        else:
            data['msg'] = 'input is error'
            data['code'] = 1
        return JsonResponse(data)


class DispenseFileView(LoginRequiredMixin, View):
    """
    分发文件
    """

    def get(self, request):
        id = request.GET.get('id', None)
        file = ''
        if id:
            try:
                file = Upload.objects.get(id=id)
            except Exception as e:
                log.error(e)
        group_all = get_asset_group()
        return render(request, 'command/dispensefile.html', {
            "group_all": group_all,
            "file": file,
            "menu": menu.get_menu(3),
        })

    def post(self, request):
        from forms import DispenseFileForm
        dispense_form = DispenseFileForm(request.POST)
        data = {'code': 0, 'msg': '', 'data': ''}
        if dispense_form.is_valid():
            module_name = 'copy'
            asset_group_id = request.POST.get('asset_id', None)
            src = request.POST.get('module_args_src', None)
            dest = request.POST.get('module_args_dest', None)
            permission = request.POST.get('module_args_permission', None)
            force = request.POST.get('module_args_force', None)
            from django.conf import settings
            src = settings.BASE_DIR + src

            if force:
                module_args = "src=%s dest=%s mode=%s force=%s" % (src, dest, permission, force)
            else:
                module_args = "src=%s dest=%s mode=%s" % (src, dest, permission)
            host_list = get_host_list(asset_group_id=int(asset_group_id), user=request.user.username)
            runner = MyRunner(host_list)
            command = runner.run(module_name=module_name, module_args=module_args)
            command_info = {'faild': {}, 'successful': {}}
            if len(command['dark']) != 0:  # 无法连接的主机
                for faild_host in command['dark']:
                    command_info['faild'][faild_host] = command['dark'][faild_host]['msg']
            for succes_host in command['contacted']:
                if command['contacted'][succes_host].has_key('failed'):  # 命令执行失败的主机
                    command_info['faild'][succes_host] = command['contacted'][succes_host]['msg']
                else:  # 执行成功主机
                    command_info['successful'][succes_host] = command['contacted'][succes_host]
            data['data'] = command_info
        else:
            data['msg'] = dispense_form.errors[dispense_form.errors.keys()[0]][0]
            data['code'] = 1
        return JsonResponse(data)


class CronView(LoginRequiredMixin, View):
    """
    计划任务
    """

    def get(self, request):
        group_all = get_asset_group()
        return render(request, 'command/cron.html', {
            "group_all": group_all,
            "menu": menu.get_menu(4),
        })

    def post(self, request):
        from forms import CronForm
        cron_form = CronForm(request.POST)
        data = {'code': 0, 'msg': '', 'data': ''}
        if cron_form.is_valid():
            module_name = 'cron'
            asset_group_id = request.POST.get('asset_id', None)
            state = request.POST.get('state', None)
            name = request.POST.get('name', None)
            minute = request.POST.get('minute', None)
            hour = request.POST.get('hour', None)
            day = request.POST.get('day', None)
            month = request.POST.get('month', None)
            weekday = request.POST.get('weekday', None)
            job = request.POST.get('job', None)
            module_args = "state=%s name=%s minute=%s hour=%s day=%s month=%s weekday=%s job='%s'" % (
            state, name, minute,
            hour, day, month,
            weekday, job)
            host_list = get_host_list(asset_group_id=int(asset_group_id), user=request.user.username)
            runner = MyRunner(host_list)
            command = runner.run(module_name=module_name, module_args=module_args)
            command_info = {'faild': {}, 'successful': {}}
            if len(command['dark']) != 0:  # 无法连接的主机
                for faild_host in command['dark']:
                    command_info['faild'][faild_host] = command['dark'][faild_host]['msg']
            for succes_host in command['contacted']:
                if command['contacted'][succes_host].has_key('failed'):  # 命令执行失败的主机
                    command_info['faild'][succes_host] = command['contacted'][succes_host]['msg']
                else:  # 执行成功主机
                    command_info['successful'][succes_host] = command['contacted'][succes_host]
            data['data'] = command_info
        else:
            data['msg'] = cron_form.errors[cron_form.errors.keys()[0]][0]
            data['code'] = 1
        return JsonResponse(data)


class PushMonitorScriptView(LoginRequiredMixin, View):
    def get(self, request):
        group_all = get_asset_group()
        return render(request, 'command/push_monitor_script.html', {
            "group_all": group_all,
            "menu": menu.get_menu(),
        })

    def post(self, request):
        data = {'faild': {}, 'successful': {}}
        asset_group_id = request.POST.get("asset_id", None)
        module_name = request.POST.get("module_name", None)
        module_args = request.POST.get("module_args", None)

        host_list = get_host_list(asset_group_id=int(asset_group_id), user=request.user.username)
        runner = MyRunner(host_list)
        command = runner.run(module_name=module_name, module_args=module_args)

        return JsonResponse(data)
