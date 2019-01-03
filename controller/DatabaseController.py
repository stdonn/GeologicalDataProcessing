# -*- coding: UTF-8 -*-
"""
Defines controller for the database handling
"""

# ToDo: Database initialization and handling

import os
import platform
import tempfile

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog

from GeologicalDataProcessing.config import debug
from GeologicalDataProcessing.geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget
from GeologicalDataProcessing.miscellaneous.Helper import get_file_name
from GeologicalDataProcessing.miscellaneous.QGISDebugLog import QGISDebugLog
from GeologicalDataProcessing.services.DatabaseService import DatabaseService


class DatabaseController(QObject):
    """
    Controller class for database interaction
    """

    logger = QGISDebugLog()

    def __init__(self, dwg: GeologicalDataProcessingDockWidget = None) -> None:
        """
        Constructor
        :param dwg: current GeologicalDataProcessingDockWidget
        :return: nothing
        """
        QObject.__init__(self)

        self.logger.debug(self.__class__.__name__, "__init__")
        self.__db_service = DatabaseService.get_instance()

        self.__dwg = None
        self.dockwidget = dwg

        self._on_db_type_changed(self.dockwidget.DB_type.currentText())

    #
    # slots
    #

    def _on_db_type_changed(self, db_type: str):
        """
        Slot called, when the database type was changed to show / hide specific elements
        :param db_type: selected database type
        :return: nothing
        :raises ValueError: if type is unknown
        """
        self.logger.debug("Selecting new database type: {}".format(db_type))
        if db_type == "SQLite":
            self.dockwidget.create_DB_button.show()
            self.dockwidget.select_DB_button.show()
            self.dockwidget.password_label.hide()
            self.dockwidget.password.hide()
            self.dockwidget.username_label.hide()
            self.dockwidget.username.hide()
            self.dockwidget.check_connection.hide()
        elif db_type == "PostgreSQL":
            self.dockwidget.create_DB_button.hide()
            self.dockwidget.select_DB_button.hide()
            self.dockwidget.password_label.show()
            self.dockwidget.password.show()
            self.dockwidget.username_label.show()
            self.dockwidget.username.show()
            self.dockwidget.check_connection.show()
        else:
            raise ValueError("Unknown DB Format: {}".format(db_type))

        if debug:
            if self.dockwidget.DB_type.currentText() == "PostgreSQL":
                self.dockwidget.database_connection.setText("localhost:5432/geology")
                self.dockwidget.password.setText("geology")
                self.dockwidget.username.setText("geology")
            elif self.dockwidget.DB_type.currentText() == "SQLite":
                tempdir = "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
                filename = "geology.sqlite"
                self.dockwidget.database_connection.setText(os.path.join(tempdir, filename))
                self.dockwidget.password.setText("")
                self.dockwidget.username.setText("")

    def _on_create_db_clicked(self) -> None:
        """
        slot for creating a new database
        :return: Nothing
        """

        self.__validate()
        # noinspection PyCallByClass,PyArgumentList
        filename = get_file_name(QFileDialog.getSaveFileName(self.dockwidget, "Select database file", "",
                                                             "Databases(*.db *.sqlite *.data);;Any File Type (*)"))

        if filename != "":
            # noinspection PyTypeChecker
            if os.path.splitext(filename)[-1].lower().lstrip('.') not in ["db", "data", "sqlite"]:
                filename += ".data"
            self.dockwidget.database_file.setText(filename)

    def _on_select_db(self) -> None:
        """
        slot for selecting a sqlite database file and set the result to the related lineedit
        :return: Nothing
        """

        self.__validate()
        # noinspection PyCallByClass,PyArgumentList
        filename = get_file_name(QFileDialog.getOpenFileName(self.dockwidget, "Select database file", "",
                                                             "Databases(*.db *.sqlite *.data);;Any File Type (*)"))

        if filename != "":
            # noinspection PyTypeChecker
            if os.path.splitext(filename)[-1].lower().lstrip('.') not in ["db", "data", "sqlite"]:
                filename += ".data"
            self.dockwidget.database_file.setText(filename)

    def _on_check_connection(self):
        """
        Check the requested database connection
        :return: nothing
        :raises ValueError: if database type is unknown
        """
        self.logger.debug("_on_check_connection called")

        result = self.__db_service.check_connection()

        if result == "":
            self.logger.info("Connection successfully tested.")
        else:
            self.logger.error("Cannot establish connection", result)

    def _update_db_service(self, _: object = None) -> None:
        """
        Update the database service, if a GUI input element changed
        :param _: temporary parameter for QLineEdit update
        :return: Nothing
        """
        self.__db_service.db_type = self.dockwidget.DB_type.currentText()
        self.__db_service.connection = self.dockwidget.database_connection.text()
        self.__db_service.password = self.dockwidget.password.text()
        self.__db_service.username = self.dockwidget.username.text()

    #
    # setter and getter
    #

    @property
    def dockwidget(self) -> GeologicalDataProcessingDockWidget:
        """
        Returns the currently active plugin-dockwidget
        :return: returns the currently active plugin-dockwidget
        """
        return self.__dwg

    @dockwidget.setter
    def dockwidget(self, value: GeologicalDataProcessingDockWidget) -> None:
        """
        Sets the currently active plugin-dockwidget
        :return: returns the currently active plugin-dockwidget
        :raises TypeError: if value is not of type GeologicalDataProcessingDockWidget
        """
        if isinstance(value, GeologicalDataProcessingDockWidget):
            if self.__dwg is not None:
                self.dockwidget.create_DB_button.clicked.disconnect(self._on_create_db_clicked)
                self.dockwidget.select_DB_button.clicked.disconnect(self._on_select_db)
                self.dockwidget.check_connection.clicked.disconnect(self._on_check_connection)
                self.dockwidget.database_connection.textChanged.disconnect(self._update_db_service)
                self.dockwidget.password.textChanged.disconnect(self._update_db_service)
                self.dockwidget.username.textChanged.disconnect(self._update_db_service)
                self.dockwidget.DB_type.currentIndexChanged[str].disconnect(self._on_db_type_changed)

            self.__dwg = value

            self.dockwidget.create_DB_button.clicked.connect(self._on_create_db_clicked)
            self.dockwidget.select_DB_button.clicked.connect(self._on_select_db)
            self.dockwidget.check_connection.clicked.connect(self._on_check_connection)
            self.dockwidget.database_connection.textChanged.connect(self._update_db_service)
            self.dockwidget.password.textChanged.connect(self._update_db_service)
            self.dockwidget.username.textChanged.connect(self._update_db_service)
            self.dockwidget.DB_type.currentIndexChanged[str].connect(self._on_db_type_changed)

            self.dockwidget.database_connection.setText("")
            self.dockwidget.password.setText("")
            self.dockwidget.username.setText("")

        else:
            raise TypeError("committed parameter is not of type GeologicalDataProcessingDockWidget")

    #
    # private functions
    #

    def __validate(self):
        """
        Validates, if the service can be executed
        :return: Nothing
        :raises
        """

        self.logger.debug(self.__class__.__name__, "__validate")

        if self.dockwidget is None:
            raise AttributeError("No dockwidget is set to the DatabaseService")
