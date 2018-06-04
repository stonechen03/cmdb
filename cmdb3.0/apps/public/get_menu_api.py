#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2018/1/4'


class Menu(object):
    """
    获取当前菜单
    """
    def __init__(self, primary=1):
        if not isinstance(primary, int):
            raise TypeError
        self.primary = primary
        self.__user_manage = 1
        self.__asset_manage = 2
        self.__file_manage = 3
        self.__command_exec = 4
        self.__alarm = 5
        self.__data = {"primary": "", "secondary": ""}

    def get_menu(self, secondary=1):
        if self.primary == self.__user_manage:
            self.__data["primary"] = self.__user_manage
        elif self.primary == self.__asset_manage:
            self.__data["primary"] = self.__asset_manage
        elif self.primary == self.__file_manage:
            self.__data["primary"] = self.__file_manage
        elif self.primary == self.__command_exec:
            self.__data["primary"] = self.__command_exec
        elif self.primary == self.__alarm:
            self.__data["primary"] = self.__alarm

        self.__data["secondary"] = int(str(self.primary) + str(secondary))
        print self.__data
        return self.__data
