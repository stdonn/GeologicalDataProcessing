# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject

from Service import Service


class Parent(QObject):
    def __init__(self):
        super().__init__()
        self._service = Service.get_instance()
        self._service.something_changed.connect(self._something_changed)
        print("Init Parent: " + self.__class__.__name__)

    def _something_changed(self):
        print("Parent - _something_changed: " + self.__class__.__name__)


class Child1(Parent):
    def __init__(self):
        super().__init__()
        print("Init Child1: " + self.__class__.__name__)

    def _something_changed(self):
        print("Child1 - _something_changed: " + self.__class__.__name__)


class Child2(Parent):
    def __init__(self):
        super().__init__()
        print("Init Child2: " + self.__class__.__name__)

    def _something_changed(self):
        print("Child2 - _something_changed: " + self.__class__.__name__)

