# coding: utf-8
from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import JsonResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from utils.utils import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from public.get_menu_api import Menu
from alarm.models import Alarm

# Create your views here.
import logging

log = logging.getLogger('django')


class AlarmInterfaceView(View):
    """报警接口"""

    def post(self, request):
        data = {'code': 0, 'msg': 'success', 'data': ''}
        level = request.POST.get('level', None)
        item = request.POST.get('item', None)
        value = request.POST.get('value', None)
        ip = request.POST.get('ip', None)
        mail_list = request.POST.get('mails', None)
        mails = mail_list.split(',')

        try:
            db = Alarm.objects.create(
                level=level,
                item=item,
                value=value,
                ip=ip,
                resolve=False,
            )
            from public.mail import Mail
            send_mail = Mail(subject=u"报警信息", text=u'报警主机：{}\n报警项目: {}\n报警信息: {}'.format(ip, item, value),
                             receivers=mails)
            if not send_mail.send_mail():
                raise Exception('邮件发送失败')
            db.save()
        except Exception as e:
            log.error(e)
            data['code'] = 1
            data['msg'] = 'faild'
        return JsonResponse(data)

    @method_decorator(csrf_exempt)  # 不使用csrf_token
    def dispatch(self, *args, **kwargs):
        return super(AlarmInterfaceView, self).dispatch(*args, **kwargs)


class AlarmListView(LoginRequiredMixin, View):
    """报警列表"""

    def get(self, request):
        if request.is_ajax():
            page = request.GET.get('page')
            limit = request.GET.get('limit')
            stop_num = int(page) * int(limit)
            start_num = stop_num - int(limit)
            search = request.GET.get('key[id]', None)
            if search:  # 搜索值
                alarm_data = Alarm.objects.filter(Q(item__icontains=search) | Q(ip__icontains=search))[
                             start_num:stop_num]
                alarm_count = Alarm.objects.filter(Q(item__icontains=search) | Q(ip__icontains=search)).count()
            else:  # 分页全部值
                alarm_data = Alarm.objects.all().order_by('-id')[start_num:stop_num]
                alarm_count = Alarm.objects.all().count()
            data = {'code': 0, 'msg': '', 'count': alarm_count, 'data': ''}
            alarm_list = []

            for alarm_info in alarm_data:
                alarm_dict = {}
                alarm_dict['id'] = alarm_info.id
                alarm_dict['level'] = alarm_info.level
                alarm_dict['item'] = alarm_info.item
                alarm_dict['value'] = alarm_info.value
                alarm_dict['ip'] = alarm_info.ip
                alarm_dict['resolve'] = alarm_info.resolve
                alarm_dict['add_time'] = alarm_info.add_time
                alarm_list.append(alarm_dict)
            data['data'] = alarm_list
            return JsonResponse(data)
        menu = Menu(5)
        return render(request, 'alarm/alarm_list.html', {
            "menu": menu.get_menu(1)
        })

    def post(self, request):
        data = {'code': 0, 'msg': ''}
        # 修改报警是否解决
        if request.is_ajax() and request.GET.get('type', None) == 'edit':
            edit_id = int(request.POST.get('id', None))
            edit_resolve = request.POST.get('resolve', None).encode("utf-8")
            try:
                alarm_db = Alarm.objects.get(id=edit_id)
                if edit_resolve == 'true':
                    alarm_db.resolve = True
                elif edit_resolve == 'false':
                    alarm_db.resolve = False
                else:
                    raise KeyError
                alarm_db.save()
                data['msg'] = '修改成功'
            except Exception as e:
                log.error(e)
                data['code'] = 1
                data['msg'] = '修改失败'
            return JsonResponse(data)

        # 删除报警
        elif request.is_ajax() and request.GET.get('type', None) == 'del':
            data['msg'] = '删除成功'
            if request.GET.get('data', None) == 'check':  # 删除选择数据
                ids = request.POST.get('data', None).split(",")
                for id in ids:
                    try:
                        Alarm.objects.get(id=id).delete()
                    except Exception as e:
                        log.error(e)
                        data['msg'] = '删除失败'

            else:  # 删除单条数据
                del_id = int(request.POST.get('id', None))
                try:
                    Alarm.objects.get(id=del_id).delete()
                except Exception as e:
                    log.error(e)
                    data['msg'] = '删除失败'

            return JsonResponse(data)
