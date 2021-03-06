# -*- coding: UTF-8 -*-
"""
Python Module for pushing debug messages to QGIS
"""

import os
import platform
import tempfile
from datetime import datetime
from enum import Enum

# noinspection PyUnresolvedReferences
from qgis.core import Qgis, QgsMessageLog
from qgis.gui import QgisInterface

import GeologicalDataProcessing.config as config


class LogLevel(Enum):
    INFO = 0,
    WARNING = 1,
    CRITICAL = 2,
    DEBUG = 3


def push_to_qgislogging(title: str, text: str = None, level: LogLevel = LogLevel.INFO) -> None:
    """
    Writes the text to QGIS Logging
    :param title: message title
    :param text: message to write to the QGIS messagelog
    :param level: QGIS message level (standard: 0 -> QgsMessageLog.INFO)
    :return: Nothing
    """
    if level == LogLevel.DEBUG:
        return

    loglevel = Qgis.Info
    if level == LogLevel.WARNING:
        loglevel = Qgis.Warning
    elif level == LogLevel.CRITICAL:
        loglevel = Qgis.Critical

    if text is not None:
        msg = "{} - {}".format(text, title)
    else:
        msg = title
    QgsMessageLog().logMessage(msg, tag="GeologicalDataProcessing", level=loglevel,
                               notifyUser=True)


class QGISLogHandler:
    """
    Singleton class for pushing log messages to QGIS and / or a log file
    """
    __iface = None
    __instance = None
    __logfile = ""
    __to_file = False

    # def __new__(cls) -> "QGISLogHandler":
    #     """
    #     Creates a new object instance if no object exists or updates the existing one.
    #     :return: The single instance of this class
    #     """
    #     if cls.__instance is None:
    #         cls.__instance = object.__new__(cls)
    #
    #     return cls.__instance

    def __init__(self, name=""):
        self.name = name

    def __push_to_logfile(self, title: str, text: str = None, level: LogLevel = LogLevel.INFO) -> None:
        """
        Writes the string text to self.__logfile
        :param title: message title
        :param text: message to write to the QGIS messagebar / messagelog
        :param level: QGIS message level (standard: 0 -> QgsMessageLog.INFO)
        :return: Nothing
        """
        if self.__logfile == "":
            assert "log file not known..."

        if (level != LogLevel.DEBUG) or config.debug:
            with open(self.__logfile, "a") as logfile:
                line = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if self.name != "":
                    line = "{} - {}".format(line, self.name)
                line = "{} - {} - {}".format(line, level.name, title)
                if text is not None:
                    line = "{}: {}".format(line, text)

                logfile.write("{}\n".format(line))

    def __push_to_qgis(self, title: str, text: str, level: LogLevel = LogLevel.INFO) -> None:
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

        if text is None:
            if level == LogLevel.INFO:
                self.__iface.messageBar().pushInfo('', title)
            elif level == LogLevel.WARNING:
                self.__iface.messageBar().pushWarning('', title)
            elif level == LogLevel.CRITICAL:
                self.__iface.messageBar().pushCritical('', title)
            else:
                # level == LogLevel.DEBUG => do nothing
                pass
        else:
            if level == LogLevel.INFO:
                self.__iface.messageBar().pushInfo(title, text)
            elif level == LogLevel.WARNING:
                self.__iface.messageBar().pushWarning(title, text)
            elif level == LogLevel.CRITICAL:
                self.__iface.messageBar().pushCritical(title, text)
            else:
                # level == LogLevel.DEBUG => do nothing
                pass

    def push_message(self, title: str, text: str = None, level: LogLevel = LogLevel.INFO, only_logfile: bool = False,
                     to_messagebar: bool = False):
        """
        :param title: message title
        :param text: message to write to the QGIS messagebar / messagelog
        :param level: QGIS message level (standard: 0 -> QgsMessageLog.INFO)
        :param only_logfile: Don't write output to QGIS interface, even if it is set
        :param to_messagebar: Notify user with messagebar notification
        :return: Nothing
        """
        if self.__to_file:
            self.__push_to_logfile(title, text, level)
        if not only_logfile:
            push_to_qgislogging(title, text, level)
        if (self.__iface is not None) and to_messagebar:
            self.__push_to_qgis(title, text, level)

    def debug(self, title: str, text: str = None) -> None:
        """
        Log a debug message
        :param title: title to be logged
        :param text: text to be logged
        :return: Nothing
        """
        self.push_message(title=title, text=text, level=LogLevel.DEBUG)

    def error(self, title: str, text: str = None, only_logfile: bool = False, to_messagebar: bool = False) -> None:
        """
        Log an error message
        :param title: title to be logged
        :param text: text to be logged
        :param only_logfile: Don't write output to QGIS interface, even if it is set
        :param to_messagebar: Notify user with messagebar notification
        :return: Nothing
        """
        self.push_message(title=title, text=text, level=LogLevel.CRITICAL, only_logfile=only_logfile,
                          to_messagebar=to_messagebar)

    def info(self, title: str, text: str = None, only_logfile: bool = False, to_messagebar: bool = False) -> None:
        """
        Log an info message
        :param title: title to be logged
        :param text: text to be logged
        :param only_logfile: Don't write output to QGIS interface, even if it is set
        :param to_messagebar: Notify user with messagebar notification
        :return: Nothing
        """
        self.push_message(title=title, text=text, level=LogLevel.INFO, only_logfile=only_logfile,
                          to_messagebar=to_messagebar)

    def warn(self, title: str, text: str = None, only_logfile: bool = False, to_messagebar: bool = False) -> None:
        """
        Log a warning message
        :param title: title to be logged
        :param text: text to be logged
        :param only_logfile: Don't write output to QGIS interface, even if it is set
        :param to_messagebar: Notify user with messagebar notification
        :return: Nothing
        """
        self.push_message(title=title, text=text, level=LogLevel.WARNING, only_logfile=only_logfile,
                          to_messagebar=to_messagebar)

    # setter and getter
    @property
    def logfile(self) -> str:
        """
        Return the path of the current logfile. This path will be empty if no logfile is defined.
        :return: Return the path of the current logfile
        """
        return QGISLogHandler.__logfile

    @property
    def save_to_file(self) -> bool:
        """
        Returns True, if the messages should be saved to the a log file, else False
        :return: Returns True, if the messages should be saved to the a log file, else False
        """
        return QGISLogHandler.__to_file

    @save_to_file.setter
    def save_to_file(self, to_file: bool) -> None:
        """
        Setter, if the messages should be saved to the a log file
        :param to_file: if True, write all outputs to a logfile
        :return: Nothing
        """

        QGISLogHandler.__to_file = bool(to_file)

        if not to_file:
            QGISLogHandler.__logfile = ""
            return

        if QGISLogHandler.__logfile == "":
            # cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            tempdir = '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
            QGISLogHandler.__logfile = os.path.join(tempdir, "GeologicalDataProcessing.log")

    @property
    def qgis_iface(self) -> QgisInterface or None:
        """
        Returns the currently set QgsInterface class or None if messages shouldn't be pushed to QGIS
        :return: Returns the currently set QgsInterface class or None
        """
        return QGISLogHandler.__iface

    @qgis_iface.setter
    def qgis_iface(self, iface: QgisInterface or None):
        """
        Sets the qgis interface. If the iface parameter is None, no messages will be pushed to QGIS.
        :param iface: The qgis interface. If this parameter is None, no messages will be pushed to QGIS.
        :return: Nothing
        :raises TypeError: if iface is not an instance of QgisInterface
        """
        if not isinstance(iface, QgisInterface) and iface is not None:
            raise TypeError("iface parameter is not an instance of QgisInterface!")

        QGISLogHandler.__iface = iface
