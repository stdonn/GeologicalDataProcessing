# -*- coding: UTF-8 -*-
"""
Python Module for pushing debug messages to QGIS
"""

import os
import platform
import tempfile
from datetime import datetime

# noinspection PyUnresolvedReferences
from qgis.gui import QgisInterface


class QGISDebugLog:
    """
    Singleton class for pushing log messages to QGIS and / or a log file
    """
    __iface = None
    __instance = None
    __logfile = ""
    __to_file = False

    def __new__(cls) -> "QGISDebugLog":
        """
        Creates a new object instance if no object exists or updates the existing one.
        :return: The single instance of this class
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        return cls.__instance

    def __push_to_logfile(self, title: str, text: str, level: int = 0) -> None:
        """
        Writes the string text to self.__logfile
        :param title: message title
        :param text: message to write to the QGIS messagebar / messagelog
        :param level: QGIS message level (standard: 0 -> QgsMessageLog.INFO)
        :return: Nothing
        """
        if self.__logfile == "":
            assert "log file not known..."

        level_text = "INFO"
        if level == 1:
            level_text = "WARNING"
        elif level == 2:
            level_text = "CRITICAL"

        with open(self.__logfile, "a") as logfile:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logfile.write("{}\t[{}] {} - {}\n".format(time, level_text, title, text))

    def __push_to_qgis(self, title: str, text: str, level: int = 0) -> None:
        """
        Writes the text to QGIS message bar
        :param title: message title
        :param text: message to write to the QGIS messagebar / messagelog
        :param level: QGIS message level (standard: 0 -> QgsMessageLog.INFO)
        :return: Nothing
        :raises ValueError: if self.iface is None
        """
        if self.__iface is None:
            raise ValueError("self.iface instance is None, cannot push messages to QGIS!")
        if level == 1:
            self.__iface.messageBar().pushWarning(title, text)
        elif level == 2:
            self.__iface.messageBar().pushCritical(title, text)
        else:
            self.__iface.messageBar().pushInfo(title, text)

    def push_message(self, title: str, text: str, level: int = 0):
        """
        :param title: message title
        :param text: message to write to the QGIS messagebar / messagelog
        :param level: QGIS message level (standard: 0 -> QgsMessageLog.INFO)
        :return: Nothing
        """
        if self.__to_file:
            self.__push_to_logfile(title, text, level)
        if self.__iface is not None:
            self.__push_to_qgis(title, text, level)

    # setter and getter
    @property
    def logfile(self) -> str:
        """
        Return the path of the current logfile. This path will be empty if no logfile is defined.
        :return: Return the path of the current logfile
        """
        return self.__logfile

    @property
    def save_to_file(self) -> bool:
        """
        Returns True, if the messages should be saved to the a log file, else False
        :return: Returns True, if the messages should be saved to the a log file, else False
        """
        return self.__to_file

    @save_to_file.setter
    def save_to_file(self, to_file: bool) -> None:
        """
        Setter, if the messages should be saved to the a log file
        :param to_file: if True, write all outputs to a logfile
        :return: Nothing
        """

        self.__to_file = bool(to_file)

        if not to_file:
            self.__logfile = ""
            return

        if self.__logfile == "":
            cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            tempdir = '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
            self.__logfile = os.path.join(tempdir, cur_time + "_GeologicalDataProcessing.log")

    @property
    def qgis_iface(self) -> QgisInterface or None:
        """
        Returns the currently set QgsInterface class or None if messages shouldn't be pushed to QGIS
        :return: Returns the currently set QgsInterface class or None
        """
        return self.__iface

    @qgis_iface.setter
    def qgis_iface(self, iface: QgisInterface):
        """
        Sets the qgis interface. If the iface parameter is None, no messages will be pushed to QGIS.
        :param iface: The qgis interface. If this parameter is None, no messages will be pushed to QGIS.
        :return: Nothing
        :raises TypeError: if iface is not an instance of QgisInterface
        """
        if not isinstance(iface, QgisInterface):
            raise TypeError("iface parameter is not an instance of QgisInterface!")

        self.__iface = iface
