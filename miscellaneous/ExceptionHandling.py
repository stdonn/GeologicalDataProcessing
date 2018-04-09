# -*- coding: UTF-8 -*-
"""
Module for basic exception handling
"""

import sys
import traceback

from PyQt5.QtWidgets import QPushButton
# noinspection PyUnresolvedReferences
from qgis.core import QgsMessageLog
# noinspection PyUnresolvedReferences
from qgis.gui import QgisInterface


class ExceptionHandling:
    """
    Singleton class for basic exception handling
    """
    __instance = None
    last_exception = None

    def __new__(cls, e: Exception = None):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        if e is not None:
            _, _, exc_traceback = sys.exc_info()
            cls.__instance.last_exception = "Error Message:\n{}\nTraceback:\n{}". \
                format(str(e), ''.join(traceback.format_tb(exc_traceback)))

        return cls.__instance

    def __str__(self) -> str:
        """
        Return last exception as a string
        :return: Return last exception as a string
        """
        return self.last_exception

    def push_last_to_qgis(self, iface: QgisInterface) -> None:
        """
        Show last exception in QGIS log message window and as a message bar hint
        :param iface: QgisInterface representation
        :return: Nothing
        """
        widget = iface.messageBar().createMessage("Error",
                                                  "An exception occurred during the process. " +
                                                  "For more details, please take a look to the log windows.")
        button = QPushButton(widget)
        button.setText("Show log windows")
        # noinspection PyUnresolvedReferences
        button.pressed.connect(self.iface.openMessageLog)
        widget.layout().addWidget(button)
        iface.messageBar().pushWidget(widget, level=2)

        # noinspection PyCallByClass, PyArgumentList
        QgsMessageLog.logMessage(self.last_exception, level=2)
