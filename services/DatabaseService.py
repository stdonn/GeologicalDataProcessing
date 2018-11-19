# -*- coding: UTF-8 -*-
"""
module with a service providing all database related connections and functions
"""

from PyQt5.QtWidgets import QFileDialog

from GeologicalDataProcessing.geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget
from GeologicalDataProcessing.config import debug
from GeologicalDataProcessing.miscellaneous.QGISDebugLog import QGISDebugLog
from GeologicalDataProcessing.miscellaneous.Helper import get_file_name


class DatabaseService:
    """
    Singleton class controlling all database related processes
    """
    __instance = None

    logger = QGISDebugLog()
    __dwg = None

    @staticmethod
    def get_instance() -> "DatabaseService":
        """
        Creates a new object instance if no object exists or updates the existing one.
        :return: The single instance of this class
        """
        if DatabaseService.__instance is None:
            if debug:
                DatabaseService.logger.push_message(DatabaseService.__class__.__name__,
                                                    "Create new DatabaseService instance", level=3)
            DatabaseService()
        elif debug:
            DatabaseService.logger.push_message(DatabaseService.__name__,
                                                "Returning existing DatabaseService instance", level=3)

        return DatabaseService.__instance

    def __init__(self):
        """ Virtually private constructor. """
        super().__init__()
        if DatabaseService.__instance is not None:
            raise BaseException("The DatabaseService-class is a singleton and can't be called directly. " +
                                "Use DatabaseService.get_instance() instead!")
        else:
            DatabaseService.__instance = self

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
                self.dockwidget.create_DB_button.clicked.disconnect(self.on_create_db_clicked)
                self.dockwidget.select_DB_button.clicked.disconnect(self.on_select_db)

            self.__dwg = value

            self.dockwidget.database_file.setText('')
            self.dockwidget.create_DB_button.clicked.connect(self._on_create_db_clicked)
            self.dockwidget.select_DB_button.clicked.connect(self._on_select_db)

        else:
            raise TypeError("committed parameter is not of type GeologicalDataProcessingDockWidget")

    #
    # slots
    #

    def _on_create_db_clicked(self) -> None:
        """
        slot for creating a new database
        :return: Nothing
        """

        self.__validate()

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

        filename = get_file_name(QFileDialog.getOpenFileName(self.dockwidget, "Select database file", "",
                                                             "Databases(*.db *.sqlite *.data);;Any File Type (*)"))

        if filename != "":
            # noinspection PyTypeChecker
            if os.path.splitext(filename)[-1].lower().lstrip('.') not in ["db", "data", "sqlite"]:
                filename += ".data"
            self.dockwidget.database_file.setText(filename)

    def _on_change_database(self, database: str) -> None:
        """
        Setting a new database connection
        :param database: The new database connection string
        :return: Nothing
        """
        self.__validate()

        self.logger.push_message(self.__class__.__name__, "New database: " + database, level=3)

    #
    # private functions
    #

    def __validate(self):
        """
        Validates, if the service can be executed
        :return: Nothing
        :raises
        """

        if debug:
            self.logger.push_message(self.__class__.__name__, "__validate", level=3)

        if self.dockwidget is None:
            raise AttributeError("No dockwidget is set to the DatabaseService")
