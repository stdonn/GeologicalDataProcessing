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
    __instance = None
    to_file = False
    iface = None
    logfile = ""

    # noinspection PyUnresolvedReferences
    def __new__(cls, to_file: bool = False, iface: QgisInterface = None) -> QGISDebugLog:
        """
        Creates a new object instance if no object exists or updates the existing one.
        :param to_file: if True, write all outputs to a temporary file
        :param iface: if not None push all messages to QGIS
        :return: The single instance of this class
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        if to_file and logfile == "":
            cur_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            tempdir = '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
            cls.__instance.logfile = os.path.join(tempdir, cur_time + "_GeologicalDataProcessing.log")

        cls.__instance.to_file = to_file
        cls.__instance.iface = iface

        return cls.__instance

    def __to_logfile(self, title: str, text: str, level: int = 0) -> None:
        """
        Writes the string text to self.__logfile
        :param title: message title
        :param text: message to write to the QGIS messagebar / messagelog
        :param level: QGIS message level (standard: 0 -> QgsMessageLog.INFO)
        :return: Nothing
        """
        if self.logfile == "":
            assert "log file not known..."

        level_text = "INFO"
        if level == 1:
            level_text = "WARNING"
        elif level == 2:
            level_text = "CRITICAL"

        with open(self.logfile, "a") as logfile:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logfile.write("{}\t[{}] {} - {}\n".format(time, level_text, title, text))

    def __to_qgis(self, title: str, text: str, level: int = 0) -> None:
        """
        Writes the text to QGIS message bar
        :param title: message title
        :param text: message to write to the QGIS messagebar / messagelog
        :param level: QGIS message level (standard: 0 -> QgsMessageLog.INFO)
        :return: Nothing
        :raises ValueError: if self.iface is None
        """
        if self.iface is None:
            raise ValueError("self.iface instance is None, cannot push messages to QGIS!")
        if level == 1:
            self.iface.messageBar().pushWarning(title, text)
        elif level == 2:
            self.iface.messageBar().pushCritical(title, text)
        else:
            self.iface.messageBar().pushInfo(title, text)

    def push_message(self, title: str, text: str, level: int = 0):
        """
        :param title: message title
        :param text: message to write to the QGIS messagebar / messagelog
        :param level: QGIS message level (standard: 0 -> QgsMessageLog.INFO)
        :return: Nothing
        """
        if self.to_file:
            self.__to_logfile(title, text, level)
        if self.iface is not None:
            self.__to_qgis(title, text, level)
