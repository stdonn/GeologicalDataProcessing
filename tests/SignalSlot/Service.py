# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject, pyqtSignal


class Service(QObject):
    __instance = None

    something_changed = pyqtSignal()

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Service.__instance is None:
            print("Creating new service")
            Service()
        else:
            print("Returning existing service")

        return Service.__instance

    def __init__(self):
        """ Virtually private constructor. """
        super().__init__()
        if Service.__instance is not None:
            raise BaseException("This class is a singleton!")
        else:
            Service.__instance = self

    def do_something(self):
        print("Do something")
        self.something_changed.emit()
