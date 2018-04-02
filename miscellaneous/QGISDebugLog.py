"""
Python Module for pushing debug messages to QGIS
"""

from datetime import datetime

import os
import platform
import tempfile


class QGISDebugLog:
    """
    Singleton class for pushing log messages to QGIS and / or a log file
    """
    __instance = None
    to_file = False
    to_QGIS = False
    logfile = ""

    # noinspection PyUnresolvedReferences
    def __new__(cls, to_file: bool = False, to_QGIS: bool = False) -> QGISDebugLog:
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        if to_file and logfile == "":
            cur_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            tempdir = '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
            cls.__instance.logfile = os.path.join(tempdir, cur_time + "_GeologicalDataProcessing.log")

        cls.__instance.to_file = to_file
        cls.__instance.to_QGIS = to_QGIS

        return cls.__instance

    def __to_logfile(self, text:str) -> None:
        """
        Writes the string text to self.__logfile
        :param text: string to write to the logfile
        :return: Nothing
        """
        if self.logfile == "":
            assert "log file not known..."

        with open(self.logfile, "a") as logfile:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logfile.write("{}\t{}\n".format(time, text))
