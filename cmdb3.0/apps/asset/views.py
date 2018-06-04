# coding:utf-8
from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import JsonResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from utils.utils import LoginRequiredMixin
from models import AssetGroup, Asset, Upload
from django.db.models import Q
import json
import os
import logging
# from public.ansible_api import MyRunner
from public.get_menu_api import Menu


log = logging.getLogger('django')


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        # fs = os.path.join(settings.BASE_DIR, 'upload/2018/01/04/nginx.conf')
        # with open(fs) as f:
        #     data = f.read()

        return render(request, 'index.html', {})

    def post(self, request):
        fs = os.path.join(settings.BASE_DIR, 'upload/2018/01/04/nginx.conf')
        with open(fs, 'w+') as f:
            f.write(request.POST.get('desc', None))
        return JsonResponse(data={'status': 'ok'})


class WebSshView(View):
    """
    web ssh console
    """
    def get(self, request):
        id = request.GET.get('id', None)
        data = {}

        if request.GET.get('type', None) == 'json':
            try:
                asset = Asset.objects.get(id=id)
                data['hostname'] = asset.ip
                data['port'] = asset.port
                data['username'] = asset.username
                data['password'] = asset.password
                return JsonResponse(data)

            except Exception as e:
                log.error(e)

        return JsonResponse({'code': 1, 'msg': '403'})


class AssetGroupView(LoginRequiredMixin, View):
    """
    组列表
    """
    def get(self, request):
        menu = Menu(2)
        if request.GET.get('type', None) == 'all':
            groups = AssetGroup.objects.all()
            group_list = []
            for group in groups:
                group_dict = {}
                group_dict['id'] = group.id
                group_dict['name'] = group.name
                group_dict['comment'] = group.comment
                group_list.append(group_dict)
            data = {'code': 0, 'msg': '', 'data': group_list}
            return JsonResponse(data)

        return render(request, 'asset/list.html', {
            "menu": menu.get_menu(1)
        })


class EditGroupView(LoginRequiredMixin, View):
    """
    编辑组
    """
    def get(self, request):
        menu.code = 2
        id = request.GET.get('id', None)
        group = AssetGroup.objects.get(id=id)

        return render(request, 'asset/edit.html', {
            'data': group,
            "menu": menu.get_menu(),
        })

    def post(self, request):
        id = request.GET.get('id', None)
        name = request.POST.get('name', None)
        desc = request.POST.get('desc', None)
        try:
            group = AssetGroup.objects.get(id=id)
            group.name = name
            if desc:
                group.comment = desc
            group.save()

            return HttpResponseRedirect(reverse("asset:group"))

        except Exception as e:
            menu.code = 2
            return render(request, 'asset/edit.html', {
                'data': group,
                'error': e,
                "menu": menu.get_menu(),
            })


class DelGroupView(LoginRequiredMixin, View):
    """
    删除组
    """
    def post(self, request):
        id = request.POST.get('id', None)
        data = {'code': 0, 'msg': '删除成功', 'data': ''}
        try:
            group = AssetGroup.objects.get(id=id)
            group.delete()
        except Exception as e:
            data = {'code': 1, 'msg': '删除失败', 'data': ''}

        return JsonResponse(data)


class AddGroupView(LoginRequiredMixin, View):
    """
    添加组
    """
    def get(self, request):
        menu.code = 2
        return render(request, 'asset/add.html', {
            "menu": menu.get_menu(),
        })

    def post(self, request):
        name = request.POST.get('name', None)
        comment = request.POST.get('comment', '')
        if name:
            try:
                if comment:
                    group = AssetGroup(
                        name=name,
                        comment=comment,
                    )
                else:
                    group = AssetGroup(
                        name=name,
                    )
                group.save()

                return HttpResponseRedirect(reverse("asset:group"))
            except Exception as e:
                log.error(e)
                menu.code = 2
                return render(request, 'asset/add.html', {
                    'name': name,
                    'comment': comment,
                    'error': e,
                    "menu": menu.get_menu(),
                })


class AssetView(LoginRequiredMixin, View):
    """
    资产列表
    """
    def get(self, request):
        menu = Menu(2)

        if request.GET.get('type') == 'all':
            limit = request.GET.get('limit', None)
            page = request.GET.get('page', None)
            stop_num = int(page) * int(limit)
            start_num = stop_num - int(limit)
            assets_count = Asset.objects.all().count()
            assets = Asset.objects.all()[start_num:stop_num]

            asset_list = []
            for asset in assets:
                asset_dict = {}
                asset_dict['id'] = asset.id
                asset_dict['ip'] = asset.ip
                asset_dict['port'] = asset.port
                asset_dict['username'] = asset.username
                asset_dict['group'] = AssetGroup.objects.get(id=asset.group).name
                asset_dict['hostname'] = asset.hostname
                asset_dict['cpu'] = asset.cpu
                asset_dict['memory'] = asset.memory
                asset_dict['disk'] = asset.disk
                asset_dict['system_type'] = asset.system_type
                asset_dict['system_version'] = asset.system_version
                asset_list.append(asset_dict)

            data = {'code': 0, 'msg': '', 'count': assets_count, 'data': asset_list}
            return JsonResponse(data)

        return render(request, 'asset/asset_list.html', {
            "menu": menu.get_menu(2),
        })


class AddAssetView(LoginRequiredMixin, View):
    """
    添加资产
    """
    def get(self, request):
        group = AssetGroup.objects.all()

        return render(request, 'asset/asset_add.html', {
            'group': group,
        })

    def post(self, request):

        ip = request.POST.get('ip', None)
        other_ip = request.POST.get('other_ip', None)
        hostname = request.POST.get('hostname', None)
        port = request.POST.get('port', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        group = request.POST.get('group', None)
        comment = request.POST.get('comment', None)
        try:
            asset = Asset(
                ip=ip,
                other_ip=other_ip,
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                group=group,
                comment=comment,
            )
            asset.save()
        except Exception as e:
            log.error(e)
            return HttpResponseRedirect(reverse("asset:asset_add"))

        return HttpResponseRedirect(reverse("asset:asset_list"))


class SeeAssetView(LoginRequiredMixin, View):
    """
    查看资产
    """
    def get(self, request):
        id = request.GET.get('id', None)
        try:
            asset = Asset.objects.get(id=id)
            if asset.group:
                group = AssetGroup.objects.get(id=asset.group)
                asset.group = group.name
            return render(request, 'asset/asset_see.html', {
                'asset': asset,
            })
        except Exception as e:

            return render(request, 'asset/asset_see.html', {
                'error': e,
            })


class EditAssetView(LoginRequiredMixin, View):
    """
    编辑资产
    """
    def get(self, request):
        id = request.GET.get('id', None)
        try:
            group = AssetGroup.objects.all()
            asset = Asset.objects.get(id=id)
            asset.group = int(asset.group)
        except Exception as e:
            log.error(e)

        return render(request, 'asset/asset_edit.html', {
            'asset': asset,
            'group': group,
        })

    def post(self, request):
        id = request.GET.get('id', None)
        ip = request.POST.get('ip', None)
        other_ip = request.POST.get('other_ip', None)
        hostname = request.POST.get('hostname', None)
        port = request.POST.get('port', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        group = request.POST.get('group', None)
        comment = request.POST.get('comment', None)
        try:
            asset = Asset.objects.get(id=id)
            asset.ip = ip
            asset.other_ip = other_ip
            asset.hostname = hostname
            asset.port = port
            asset.username = username
            asset.group = group
            asset.comment = comment
            if password:
                asset.password = password
            asset.save()
        except Exception as e:
            log.error(e)

            return HttpResponseRedirect(reverse("asset:asset_add"))

        return HttpResponseRedirect(reverse("asset:asset_list"))


class DelAssetView(LoginRequiredMixin, View):
    """
    删除资产
    """
    def post(self, request):
        id = request.POST.get('id', None)
        try:
            asset = Asset.objects.get(id=id).delete()
            data = {"code": 0, "msg": "删除成功", "data": ""}
        except Exception as e:
            log.error(e)
            data = {"code": 1, "msg": "删除失败, 请联系管理员！", "data": ""}

        return JsonResponse(data)


class UpdateAssetView(LoginRequiredMixin, View):
    """
    更新资产信息
    """
    def post(self, request):
        datas = request.POST.get('data', None)
        json_datas = json.loads(datas)
        id_list = []
        for i in json_datas:
            id_list.append(i['id'])
        from public.asset_api import get_host_info, get_host_list
        hosts = get_host_list(host_id_list=id_list)
        status = get_host_info(hosts)
        if len(status) == 0:
            data = {"code": 0, "msg": u"更新成功", "data": ""}
        else:
            data = {"code": 1, "msg": status, "data": ""}

        return JsonResponse(data)


class SendKeyView(LoginRequiredMixin, View):
    """
    推送秘钥
    """
    def post(self, request):
        data = {'code': 0, 'msg': 'success', 'data': ''}
        datas = request.POST.get('data', None)
        json_data = json.loads(datas)
        id_list = []
        for i in json_data:
            id_list.append(i['id'])
        from public.asset_api import get_host_list, push_key
        hosts = get_host_list(host_id_list=id_list)
        from django.conf import settings
        key_file = settings.BASE_DIR + '/upload/key/' + request.user.username + '/' + request.user.username + '.pub'
        if os.path.isfile(key_file):
            faild_host = push_key(hosts, key_path=key_file)
            if len(faild_host) > 0:
                data['msg'] = faild_host
                data['code'] = 1
        else:
            data['code'] = 1
            data['msg'] = u'秘钥文件不存在'
        return JsonResponse(data)


class UploadFileView(LoginRequiredMixin, View):
    """
    文件上传
    """
    def get(self, request):
        menu = Menu(3)
        return render(request, 'asset/upload_list.html', {
            "menu": menu.get_menu(2)
        })

    def post(self, request):
        data = {"code": 0, "msg": "ok", "data": ""}
        file = request.FILES.get("file")
        from utils.file_upload import upload_file
        upload_file(file)
        return JsonResponse(data)


class FileListView(LoginRequiredMixin, View):
    """
    文件列表
    """
    def get(self, request):
        menu = Menu(3)
        if request.is_ajax():
            info = {'code': 0, 'msg': '', 'data': ''}
            limit = request.GET.get('limit', None)
            page = request.GET.get('page', None)
            stop_num = int(page) * int(limit)
            start_num = stop_num - int(limit)
            search = request.GET.get("key[id]", None)
            if search:
                file_all = Upload.objects.filter(Q(url__icontains=search) | Q(name__icontains=search)).only("id", "name", "suffix", "url").order_by("id")[start_num:stop_num]
                file_count = Upload.objects.filter(Q(url__icontains=search) | Q(name__icontains=search)).only("id", "name", "suffix", "url").count()
            else:
                file_all = Upload.objects.all().only("id", "name", "suffix", "url")[start_num:stop_num]
                file_count = Upload.objects.count()
            data = []
            for files in file_all:
                file_dict = {}
                file_dict["id"] = files.id
                file_dict["name"] = files.name
                file_dict["suffix"] = files.suffix
                file_dict["url"] = files.url
                data.append(file_dict)
            info['data'] = data
            info['count'] = file_count
            return JsonResponse(info)
        return render(request, "asset/file_list.html", {
            "menu": menu.get_menu(1)
        })

    def post(self, request):
        if request.is_ajax():
            data = {'code': 0, 'msg': '删除成功', 'data': ''}

            if request.GET.get("type", None):
                ids = request.POST.get("data", None).split(",")
            else:
                ids = request.POST.get("id", None).split(",")

            for id in ids:
                try:
                    files = Upload.objects.get(id=id)
                    url = files.url.encode("utf-8")
                    import os
                    from django.conf import settings
                    file_dir = settings.BASE_DIR + url
                    if os.path.isfile(file_dir):
                        os.remove(file_dir)
                        files.delete()
                    else:
                        data['msg'] = '文件不存在'
                        data['code'] = 1

                except Exception as e:
                    log.error(e)
                    data['msg'] = '删除失败，请联系管理员'
                    data['code'] = 1
                    return JsonResponse(data)
            return JsonResponse(data)


class FileEditView(LoginRequiredMixin, View):
    """
    文件编辑
    """

    def get(self, request):
        base_dir = settings.BASE_DIR
        id = request.GET.get("id", None)
        url = ''
        try:
            url = Upload.objects.get(id=id).url
        except Exception as e:
            log.error(e)

        file_dir = base_dir + url
        if os.path.isfile(file_dir):
            with open(file_dir) as f:
                data = f.read()
        else:
            data = "no such file"
        return render(request, "asset/file_edit.html", {
            "data": data,
            "file_dir": file_dir,
        })

    def post(self, request):
        data = {'code': 0, 'msg': u'修改成功', 'data': ''}
        file_dir = request.POST.get("file_dir", None)
        desc = request.POST.get("desc", None)
        if os.path.isfile(file_dir):
            with open(file_dir, 'w+') as f:
                f.write(desc)
        else:
            log.error('no such file: {}'.format(file_dir))
            data["code"] = 1
            data["msg"] = u"文件不存在"
        return JsonResponse(data)


class NewWebSshView(LoginRequiredMixin, View):
    """
    webssh
    """
    def get(self, request):
        return JsonResponse({'code': 1, 'msg': 403, 'data': ''})