# encoding:utf-8
from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import DctUserManger, AuthGroupManage
from asset.models import AssetGroup
from .forms import LoginForms
from utils.utils import LoginRequiredMixin
from public.get_menu_api import Menu
from django.http.response import JsonResponse
import json
import logging

menu = Menu(1)
log = logging.getLogger('django')


# Create your views here.


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = DctUserManger.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LogoutView(View):
    """
    用户登出
    """

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("user:login"))


class LoginView(View):
    """
    用户登陆
    """

    def get(self, request):
        return render(request, 'user/login.html', {})

    def post(self, request):
        login_form = LoginForms(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    next_url = request.GET.get("next", None)
                    if next_url:
                        return HttpResponseRedirect(next_url)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "user/login.html", {"msg": u"用户未激活"})
            else:
                return render(request, "user/login.html", {"msg": u"用户名或密码错误！"})
        return render(request, "user/login.html", {'msg': 'error'})


class SeeView(LoginRequiredMixin, View):
    """
    用户列表
    """

    def get(self, request):
        if request.GET.get('type') == 'all':
            page = request.GET.get('page')
            limit = request.GET.get('limit')
            stop_num = int(page) * int(limit)
            start_num = stop_num - int(limit)
            all_user = DctUserManger.objects.all()[start_num:stop_num]
            data = {'code': 0, 'msg': '', 'data': ''}
            user_list = []
            for user in all_user:
                user_dict = {}
                user_dict['id'] = user.id
                user_dict['username'] = user.username
                user_dict['email'] = user.email
                user_dict['is_active'] = user.is_active
                user_dict['is_superuser'] = user.is_superuser
                user_dict['last_login'] = user.last_login
                user_list.append(user_dict)

            data['data'] = user_list
            return JsonResponse(data)

        return render(request, 'user/list.html', {
            "this_user_list": 0,
            "menu": menu.get_menu(1)
        })


class EditUserView(LoginRequiredMixin, View):
    """
    用户编辑
    """

    def get(self, request):
        id = request.GET.get('id', None)
        user = DctUserManger.objects.get(id=id)
        groups = AuthGroupManage.objects.all()

        return render(request, 'user/edit.html', {
            'data': user,
            'groups': groups,
        })

    def post(self, request):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        group = request.POST.get('group', None)
        email = request.POST.get('email', None)
        superuser = request.POST.get('superuser', None)
        switch = request.POST.get('switch', None)

        user = DctUserManger.objects.get(username=username)
        if group is not None:
            if group != '':
                group_db = AuthGroupManage.objects.get(id=group)
                if group != group_db.id:
                    user.group_id = group_db
            else:
                user.group_id = None

        if password:
            user.set_password(password)

        if email != user.email:
            user.email = email

        if superuser != user.is_superuser:
            if superuser == 'True':
                user.is_superuser = 1
            elif superuser == 'False':
                user.is_superuser = 0

        if switch == "on":
            user.is_active = 0
        else:
            user.is_active = 1

        user.save()
        return HttpResponseRedirect(reverse("user:list"))


class AddUserView(LoginRequiredMixin, View):
    """
    添加用户
    """

    def get(self, request):
        groups = AuthGroupManage.objects.all()

        return render(request, 'user/add.html', {'groups': groups})

    def post(self, request):
        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        password1 = request.POST.get('password1', None)
        group_id = request.POST.get('group', None)
        is_superuser = request.POST.get('is_superuser', None)
        is_active = request.POST.get('switch', None)

        if password == password1:
            user = DctUserManger.objects.create_user(username, email, password)
            if is_superuser == 'True':
                user.is_superuser = 1

            if is_active == "on":
                user.is_active = 0

            if group_id is not None and group_id != '':
                group = AuthGroupManage.objects.get(id=group_id)
                user.group_id = group
            from public.asset_api import gen_keys
            if gen_keys(user=user.username):
                user.save()
                return HttpResponseRedirect(reverse("user:list"))
            else:
                return render(request, 'user/add.html', {
                    'username': username,
                    'email': email,
                    'error': '秘钥生成错误',
                })
        else:
            return render(request, 'user/add.html', {
                'username': username,
                'email': email,
                'error': '密码不一致',
            })


class DelUserView(LoginRequiredMixin, View):
    """
    删除用户
    """

    def post(self, request):
        from public.asset_api import del_keys
        type = request.GET.get('type', None)
        data = {'code': 0, 'msg': '删除成功', 'data': ''}
        if type == 'all':
            users = json.loads(request.POST.get('data', None))
            for user_info in users:
                try:
                    user = DctUserManger.objects.get(username=user_info['username'])
                    del_keys(user_info['username'])
                    user.delete()
                except Exception as e:
                    data['code'] = 1
                    data['msg'] = '删除失败,%s' % e
                    return JsonResponse(data)
            return JsonResponse(data)
        else:
            username = request.POST.get('username', None)
            try:
                user = DctUserManger.objects.get(username=username)
                del_keys(username)
                user.delete()
            except Exception as e:
                data['code'] = 1
                data['msg'] = '删除失败,%s' % e

            return JsonResponse(data)


class SeeGroupView(LoginRequiredMixin, View):
    """
    授权组列表
    """

    def get(self, request):
        if request.GET.get('type', None) == 'all':
            page = request.GET.get('page')
            limit = request.GET.get('limit')
            stop_num = int(page) * int(limit)
            start_num = stop_num - int(limit)
            all_group = AuthGroupManage.objects.all()[start_num:stop_num]
            data = {'code': 0, 'msg': '', 'data': ''}
            group_list = []
            for group in all_group:
                group_dict = {}
                group_dict['id'] = group.id
                group_dict['name'] = group.name
                group_dict['users'] = group.users
                group_dict['asset'] = group.asset
                group_list.append(group_dict)

            data['data'] = group_list
            return JsonResponse(data)
        return render(request, 'user/group_list.html', {
            "menu": menu.get_menu(2)
        })


class AddGroupView(LoginRequiredMixin, View):
    """
    添加授权组
    """

    def get(self, request):
        return render(request, 'user/add_group.html')

    def post(self, request):
        name = request.POST.get('name', None)
        data = {"code": 0, "msg": "添加成功", "data": ""}
        try:
            db_group = AuthGroupManage.objects.create(name=name)
            db_group.save()
        except Exception as e:
            log.error(e)
            data["code"] = 1
            data["msg"] = "添加失败"
        return JsonResponse(data)


class EditGroupView(LoginRequiredMixin, View):
    """
    编辑授权组
    """

    def get(self, request):
        id = request.GET.get("id", None)
        data = AuthGroupManage.objects.get(id=id)
        return render(request, 'user/group_edit.html', {'data': data})

    def post(self, request):
        id = request.GET.get('id', None)
        name = request.POST.get('name', None)
        data = {"code": 0, "msg": "修改成功", "data": ""}
        try:
            group = AuthGroupManage.objects.get(id=id)
            group.name = name
            group.save()
        except Exception as e:
            log.error(e)
            data["msg"] = "修改失败，请联系管理员！"
        return JsonResponse(data)


class DelGroupView(LoginRequiredMixin, View):
    """
    删除授权组
    """

    def post(self, request):
        data = json.loads(request.POST.get('data', None))
        json_data = {"code": 0, "msg": "", "data": ""}
        for info in data:
            try:
                group = AuthGroupManage.objects.get(id=info['id'])
                group.delete()
                json_data["msg"] = u"删除成功!"
            except Exception as e:
                log.error(e)
                json_data["code"] = 1
                json_data["msg"] = u"删除失败!"
        return JsonResponse(json_data)


class AuthUserView(LoginRequiredMixin, View):
    """
    授权用户
    """

    def get(self, request):
        if request.is_ajax():
            data = {"code": 0, "msg": "success", "data": ""}
            try:
                groups = AuthGroupManage.objects.get(id=request.GET.get("id", None))
                if groups.users is None or groups.users == '':
                    users_list = []
                else:
                    users_list = groups.users.split(',')

                user_list = []
                if request.GET.get("type", None) == "del":  # 授权用户列表
                    for num in users_list:
                        user_dict = {}
                        user = DctUserManger.objects.get(id=num)
                        user_dict["id"] = user.id
                        user_dict["username"] = user.username
                        user_dict["email"] = user.email
                        user_list.append(user_dict)
                elif request.GET.get("type", None) == "auth":  # 未授权用户列表
                    user_all = DctUserManger.objects.values('id', 'username', 'email')
                    for user in user_all:
                        if str(user['id']) not in users_list:
                            user_list.append(user)
                if len(user_list) != 0:
                    data["data"] = user_list
                else:
                    data["msg"] = "无数据"
                    data["code"] = 1

            except Exception as e:
                log.error(e)
                data["msg"] = "faild"
                data["code"] = 1
            return JsonResponse(data)
        else:
            id = request.GET.get("id", None)
            if request.GET.get("type", None) == "auth":
                return render(request, 'user/auth/auth_user.html', {"id": id})

            elif request.GET.get("type", None) == "del":
                return render(request, 'user/auth/auth_user_del.html', {"id": id})

    def post(self, request):

        if request.is_ajax():
            gid = request.GET.get('gid', None)
            post_data = json.loads(request.POST.get("data"))
            group = AuthGroupManage.objects.get(id=gid)
            if group.users is None or group.users == '':
                users_list = []
            else:
                users_list = group.users.split(',')

            if request.GET.get('type', None) == 'del':  # 移除授权用户
                for user_id in post_data:
                    users_list.remove(str(user_id["id"]))
                group.users = ','.join(users_list)
                group.save()
            elif request.GET.get("type", None) == 'add':  # 授权用户
                for user_info in post_data:
                    if str(user_info["id"]) not in users_list:
                        users_list.append(str(user_info["id"]))
                group.users = ','.join(users_list)
                group.save()

        data = {"code": 0, "msg": "success", "data": ""}
        return JsonResponse(data)


class AuthAssetView(LoginRequiredMixin, View):
    """
    授权资产组
    """

    def get(self, request):
        if request.is_ajax():
            data = {"code": 0, "msg": "success", "data": ""}
            try:
                groups = AuthGroupManage.objects.get(id=request.GET.get("id", None))
                if groups.asset is None or groups.asset == '':
                    asset_list = []
                else:
                    asset_list = groups.asset.split(',')

                asset_group_list = []
                if request.GET.get("type", None) == "del":  # 授权用户列表
                    for num in asset_list:
                        asset_dict = {}
                        asset = AssetGroup.objects.get(id=num)
                        asset_dict["id"] = asset.id
                        asset_dict["name"] = asset.name
                        asset_dict["comment"] = asset.comment
                        asset_group_list.append(asset_dict)
                elif request.GET.get("type", None) == "auth":  # 未授权资产组列表
                    asset_group_all = AssetGroup.objects.values('id', 'name', 'comment')
                    for asset_group in asset_group_all:
                        if str(asset_group['id']) not in asset_list:
                            asset_group_list.append(asset_group)
                if len(asset_group_list) != 0:
                    data["data"] = asset_group_list
                else:
                    data["msg"] = "无数据"
                    data["code"] = 1

            except Exception as e:
                log.error(e)
                data["msg"] = "faild"
                data["code"] = 1
            return JsonResponse(data)
        else:
            id = request.GET.get("id", None)
            if request.GET.get("type", None) == "auth":
                return render(request, 'user/auth/auth_asset.html', {"id": id})

            elif request.GET.get("type", None) == "del":
                return render(request, 'user/auth/auth_asset_del.html', {"id": id})

    def post(self, request):
        if request.is_ajax():
            gid = request.GET.get('gid', None)
            post_data = json.loads(request.POST.get("data"))
            group = AuthGroupManage.objects.get(id=gid)
            if group.asset is None or group.asset == '':
                asset_list = []
            else:
                asset_list = group.asset.split(',')

            if request.GET.get('type', None) == 'del':  # 移除授权资产组
                for user_id in post_data:
                    asset_list.remove(str(user_id["id"]))
                group.asset = ','.join(asset_list)
                group.save()
            elif request.GET.get("type", None) == 'add':  # 授权资产组
                for asset_info in post_data:
                    if str(asset_info["id"]) not in asset_list:
                        asset_list.append(str(asset_info["id"]))
                group.asset = ','.join(asset_list)
                group.save()

        data = {"code": 0, "msg": "success", "data": ""}
        return JsonResponse(data)
