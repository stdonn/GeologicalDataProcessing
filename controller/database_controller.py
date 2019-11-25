# -*- coding: UTF-8 -*-
"""
Defines controller for the database handling
"""

import os
import platform
import tempfile
from typing import Dict

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog

from GeologicalDataProcessing.miscellaneous.config_handler import ConfigHandler
from GeologicalDataProcessing.miscellaneous.helper import get_file_name
from GeologicalDataProcessing.miscellaneous.qgis_log_handler import QGISLogHandler
from GeologicalDataProcessing.services.database_service import DatabaseService
from GeologicalDataProcessing.settings_dialog import SettingsDialog

found_keyring = True
# noinspection PyBroadException
try:
    import keyring
except Exception:
    found_keyring = False


class DatabaseController(QObject):
    """
    Controller class for database interaction
    """

    def __init__(self, settings: SettingsDialog = None) -> None:
        """
        Constructor
        :param settings: settings dialog
        :return: nothing
        """
        QObject.__init__(self)

        self.logger = QGISLogHandler(DatabaseController.__name__)

        self.__db_service = DatabaseService.get_instance()
        self.__last_db_settings = dict()

        self.__settings = None
        self.__config = ConfigHandler()
        self.settings = settings

        db_type = self.__config.get("General", "db_type")
        if db_type != "" and db_type in ["SQLite", "PostgreSQL"]:
            self.settings.DB_type.setCurrentText(db_type)
        else:
            db_type = "SQLite"
            self.__config.set("General", "db_type", db_type)
            self.settings.DB_type.setCurrentText(db_type)

        self.__on_db_type_changed(db_type)

    #
    # slots
    #

    def __on_db_type_changed(self, db_type: str):
        """
        Slot called, when the database type was changed to show / hide specific elements
        :param db_type: selected database type
        :return: nothing
        :raises ValueError: if type is unknown
        """
        self.logger.debug("Selecting new database type: {}".format(db_type))
        if db_type == "SQLite":
            self.settings.create_DB_button.show()
            self.settings.select_DB_button.show()
            self.settings.password_label.hide()
            self.settings.password.hide()
            self.settings.username_label.hide()
            self.settings.username.hide()
            self.settings.save_password.hide()

            tempdir = "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
            filename = "geology.sqlite"
            self.settings.database_connection.setPlaceholderText(os.path.join(tempdir, filename))

        elif db_type == "PostgreSQL":
            self.settings.create_DB_button.hide()
            self.settings.select_DB_button.hide()
            self.settings.password_label.show()
            self.settings.password.show()
            self.settings.username_label.show()
            self.settings.username.show()
            if found_keyring:
                self.settings.save_password.show()
            else:
                self.settings.save_password.hide()

            self.settings.database_connection.setPlaceholderText("localhost:5432/geology")
            self.settings.username.setPlaceholderText("postgres")
            self.settings.password.setPlaceholderText("")
        else:
            self.settings.database_connection.setText("")
            self.settings.username.setText("")
            self.settings.password.setText("")
            self.settings.database_connection.setPlaceholderText("")
            self.settings.username.setPlaceholderText("")
            self.settings.password.setPlaceholderText("")
            raise ValueError("Unknown DB Format: {}".format(db_type))

        if self.__config.has_section(db_type):
            self.settings.database_connection.setText(self.__config.get(db_type, "connection"))
            self.settings.username.setText(self.__config.get(db_type, "username"))
            self.settings.password.setText("")

        else:
            self.settings.database_connection.setText("")
            self.settings.username.setText("")
            self.settings.password.setText("")

        self.__update_db_service()

    def __on_create_db_clicked(self) -> None:
        """
        slot for creating a new database
        :return: Nothing
        """

        self.__validate()
        # noinspection PyCallByClass,PyArgumentList
        filename = get_file_name(
            QFileDialog.getSaveFileName(parent=self.settings, caption="Select database file", directory="",
                                        filter="Databases(*.db *.sqlite *.data);;Any File Type (*)"))

        if filename != "":
            # noinspection PyTypeChecker
            if os.path.splitext(filename)[-1].lower().lstrip('.') not in ["db", "data", "sqlite"]:
                filename += ".data"
            self.settings.database_connection.setText(filename)

    def __on_select_db(self) -> None:
        """
        slot for selecting a sqlite database file and set the result to the related lineedit
        :return: Nothing
        """

        self.__validate()
        # noinspection PyCallByClass,PyArgumentList
        filename = get_file_name(QFileDialog.getOpenFileName(self.settings, "Select database file", "",
                                                             "Databases(*.db *.sqlite *.data);;Any File Type (*)"))

        if filename != "":
            # noinspection PyTypeChecker
            if os.path.splitext(filename)[-1].lower().lstrip('.') not in ["db", "data", "sqlite"]:
                filename += ".data"
            self.settings.database_connection.setText(filename)

    def __on_check_connection(self):
        """
        Check the requested database connection
        :return: if the connection check was successful
        :raises ValueError: if database type is unknown
        """
        result = self.__db_service.check_connection()

        if result == "":
            self.logger.info("Connection test successful")
            return True

        else:
            self.logger.error("connection test failed", result)
            return False

    def __on_save(self):
        self.__last_db_settings = self.__get_db_settings()
        self.__update_db_service()
        if self.__on_check_connection():
            self.__update_config()
            self.settings.accept()
        else:
            self.__restore_db_settings(self.__last_db_settings)

    def __on_cancel(self):
        self.__on_db_type_changed(self.settings.DB_type.currentText())
        self.settings.reject()

    #
    # private functions
    #

    def __update_db_service(self, _: object = None) -> None:
        """
        Update the database service, if a GUI input element changed
        :param _: temporary parameter for QLineEdit update
        :return: Nothing
        """

        self.__db_service.db_type = self.settings.DB_type.currentText()
        self.__db_service.connection = self.settings.database_connection.text()
        self.__db_service.username = self.settings.username.text()
        self.__db_service.password = self.settings.password.text()

        if self.__db_service.connection == "":
            self.__db_service.connection = self.settings.database_connection.placeholderText()
        if self.__db_service.username == "":
            self.__db_service.username = self.settings.username.placeholderText()
        if self.__db_service.password == "" and found_keyring:
            # empty password ? try request from system keystore
            self.__db_service.password = keyring.get_password(
                "Postgres {}".format(self.__db_service.connection), self.__db_service.username)

        # self.logger.debug("Connection settings:\ndatabase:\t{}\nconnection:\t{}\nusername:\t{}\npassword:\t{}".format(
        #    self.__db_service.db_type, self.__db_service.connection,
        #    self.__db_service.username, self.__db_service.password))

    def __get_db_settings(self) -> Dict:
        """
        Returns the current database connection settings as dictionary
        :return: current database connection settings
        """
        return {"db": self.__db_service.db_type,
                "connection": self.__db_service.connection,
                "username": self.__db_service.username,
                "password": self.__db_service.password}

    def __restore_db_settings(self, values: Dict) -> None:
        """
        Restores the database connection settings
        :param values: dictionary with connection settings
        :return: Nothing
        """
        try:
            self.__db_service.db_type = values["db"]
            self.__db_service.connection = values["connection"]
            self.__db_service.username = values["username"]
            self.__db_service.password = values["password"]
        except KeyError as e:
            self.logger.error("Can't restore database settings: {}", str(e))

    def __update_config(self):
        db_type = self.settings.DB_type.currentText()

        if db_type == "PostgreSQL":
            self.__config.set("PostgreSQL", "connection", self.__db_service.connection)
            self.__config.set("PostgreSQL", "username", self.__db_service.username)

            if self.settings.save_password.isChecked() and found_keyring:
                keyring.set_password("Postgres {}".format(self.__db_service.connection), self.__db_service.username,
                                     self.__db_service.password)

        elif db_type == "SQLite":
            self.__config.set("SQLite", "connection", self.__db_service.connection)

        if db_type in ["PostgreSQL", "SQLite"]:
            self.__config.set("General", "db_type", db_type)
            self.__on_db_type_changed(self.__config.get("General", "db_type"))

    def __validate(self):
        """
        Validates, if the service can be executed
        :return: Nothing
        :raises
        """

        if self.settings is None:
            raise AttributeError("No settings dialog is set")

        if self.__config is None:
            raise AttributeError("No config is set")

    #
    # setter and getter
    #

    @property
    def settings(self) -> SettingsDialog:
        """
        Returns the currently active settings dialog
        :return: returns the currently active settings dialog
        """
        return self.__settings

    @settings.setter
    def settings(self, value: SettingsDialog) -> None:
        """
        Sets the currently active settings dialog
        :return: returns the currently active settings dialog
        :raises TypeError: if value is not of type SettingsDialog
        """

        if isinstance(value, SettingsDialog):
            if self.__settings is not None:
                self.__settings.create_DB_button.clicked.disconnect(self.__on_create_db_clicked)
                self.__settings.select_DB_button.clicked.disconnect(self.__on_select_db)
                self.__settings.DB_type.currentIndexChanged[str].disconnect(self.__on_db_type_changed)
                self.__settings.save_button.clicked.disconnect(self.__on_save)
                self.__settings.cancel_button.clicked.disconnect(self.__on_cancel)

            self.__settings = value

            self.__settings.create_DB_button.clicked.connect(self.__on_create_db_clicked)
            self.__settings.select_DB_button.clicked.connect(self.__on_select_db)
            self.__settings.DB_type.currentIndexChanged[str].connect(self.__on_db_type_changed)
            self.__settings.save_button.clicked.connect(self.__on_save)
            self.__settings.cancel_button.clicked.connect(self.__on_cancel)

        else:
            raise TypeError("committed parameter is not of type SettingsDialog")
