# -*- coding: UTF-8 -*-
"""
module to provide the import service
"""

import inspect
import os

from typing import List

from qgis.core import QgsCoordinateReferenceSystem

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QFileDialog

from GeologicalDataProcessing.config import debug
from GeologicalDataProcessing.geological_data_processing import GeologicalDataProcessingDockWidget
from GeologicalDataProcessing.miscellaneous.ExceptionHandling import ExceptionHandling
from GeologicalDataProcessing.miscellaneous.QGISDebugLog import QGISDebugLog
from GeologicalDataProcessing.miscellaneous.Helper import get_file_name


class ImportService(QObject):
    """
    Singleton class controlling the import procedures
    """
    __instance = None
    __dwg = None
    __selectable_columns: List[str] = []
    __number_columns: List[str] = []

    logger = QGISDebugLog()

    @staticmethod
    def get_instance(dwg: GeologicalDataProcessingDockWidget = None) -> "ImportService":
        """
        Creates a new object instance if no object exists or updates the existing one.
        :return: The single instance of this class
        """

        if ImportService.__instance is None:
            ImportService.logger.debug(ImportService.__class__.__name__, "Create new ImportService instance")
            ImportService(dwg)
        else:
            ImportService.logger.debug(ImportService.__name__, "Returning existing ImportService instance")

        return ImportService.__instance

    def __init__(self, dwg: GeologicalDataProcessingDockWidget = None):
        """ Virtual private constructor. """
        super().__init__()
        if ImportService.__instance is not None:
            raise BaseException("The ImportService-class is a singleton and can't be called directly. " +
                                "Use ImportService.get_instance() instead!")
        else:
            if dwg is not None:
                self.dockwidget = dwg
            ImportService.__instance = self
            self.separator = ','
            self.import_file = ''

    #
    # signals
    #

    crs_changed = pyqtSignal(QgsCoordinateReferenceSystem)
    """signal send, when the selected coordinate reference system changes"""
    import_file_changed = pyqtSignal(str)
    """signal send, when the import file name changes"""
    separator_changed = pyqtSignal(str)
    """signal send, when the selected separator changes"""
    import_columns_changed = pyqtSignal()
    """signal send, when the import columns changed"""
    reset_import = pyqtSignal()
    """signal send, when the reset was requested"""

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
        :return: Nothing
        :raises TypeError: if value is not of type GeologicalDataProcessingDockWidget
        """
        if isinstance(value, GeologicalDataProcessingDockWidget):
            if self.__dwg is not None:
                self.dockwidget.import_file.textChanged.disconnect(self._on_import_file_changed)
                self.dockwidget.select_data_file_button.clicked.disconnect(self.__on_select_data_file)
                self.dockwidget.separator.currentIndexChanged[str].disconnect(self._on_separator_changed)

            self.__dwg = value

            self.dockwidget.import_file.textChanged.connect(self._on_import_file_changed)
            self.dockwidget.select_data_file_button.clicked.connect(self.__on_select_data_file)
            self.dockwidget.separator.currentIndexChanged[str].connect(self._on_separator_changed)

            self.__dwg.separator.addItems([';', ',', '<tabulator>', '.', '-', '_', '/', '\\'])
            self.separator = ','
            self.import_file = ''
        else:
            raise TypeError("committed parameter is not of type GeologicalDataProcessingDockWidget")

    @property
    def import_file(self):
        """
        Returns the currently selected import file
        :return: returns the currently selected import file
        """
        self.__validate()

        return self.dockwidget.import_file.text()

    @import_file.setter
    def import_file(self, filename: str) -> None:
        """
        import file setter
        :param filename: new path to the import file
        :return: Nothing
        :raises ValueError: if the file doesn't exists
        """
        self.__validate()

        self.dockwidget.import_file.setText(str(filename))

    @property
    def separator(self) -> str:
        """
        get / set the separator of the input file
        possible values are: ';', ',', '\t', '.', '-', '_', '/', '\\'
        :return: returns the currently selected separator
        """
        self.__validate()

        sep = self.dockwidget.separator.currentText()
        if sep == "<tabulator>":
            sep = '\t'
        return sep

    @separator.setter
    def separator(self, sep: str) -> None:
        """
        get / set the separator of the input file
        possible values are: ';', ',', '\t', '.', '-', '_', '/', '\\'
        :return: nothing
        :param sep: new separator
        :return: Nothing
        :raises ValueError: if sep is not in list of possible values.
        """
        self.__validate()

        if sep not in [';', ',', '\t', '.', '-', '_', '/', '\\']:
            raise ValueError("{} as separator is not allowed!")

        if sep == '\t':
            sep = "<tabulator>"

        self.dockwidget.separator.setCurrentText(sep)

    @property
    def crs(self) -> QgsCoordinateReferenceSystem:
        """
        gets / sets the Reference System in QGIS format
        :return: current coordinate reference system
        :raises TypeError: if crs is an instance of QgsCoordinateReferenceSystem
        :raises ValueError: if the committed reference system is not valid
        """
        self.__validate()

        return self.dockwidget.mQgsProjectionSelectionWidget.crs()

    @crs.setter
    def crs(self, _crs: QgsCoordinateReferenceSystem) -> None:
        """
        gets / sets the Reference System in QGIS format
        :return: current coordinate reference system
        :raises TypeError: if crs is an instance of QgsCoordinateReferenceSystem
        """
        self.__validate()

        if not isinstance(_crs, QgsCoordinateReferenceSystem):
            raise TypeError("committed value is not of type QgsCoordinateReferenceSystem!")

        if not _crs.isValid():
            raise ValueError("committed reference system is not valid")

        self.dockwidget.mQgsProjectionSelectionWidget.setCrs(_crs)

    @property
    def selectable_columns(self) -> List[str]:
        """
        Returns a list of selectable columns
        :return: Returns a list of selectable columns
        """
        return self.__selectable_columns

    @property
    def number_columns(self) -> List[str]:
        """
        Returns a list of number columns
        :return: Returns a list of number columns
        """
        return self.__number_columns

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
            raise AttributeError("No dockwidget is set to the ImportService")

    #
    # public functions
    #

    def reset(self):
        """
        Reset the import service and related fields
        :return: Nothing
        """
        self.__validate()

        self.logger.debug(self.__class__.__name__, "reset")

        self.__selectable_columns = []
        self.__number_columns = []
        self.import_file_changed.emit("")
        self.reset_import.emit()

    #
    # slots
    #

    def _on_crs_changed(self) -> None:
        """
        slot called, when the selected coordinate reference system has changed
        :return: Nothing
        """
        self.__validate()

        self.logger.debug(self.__class__.__name__, "_on_crs_changed")

        self.crs_changed.emit(self.dockwidget.mQgsProjectionSelectionWidget.crs())

    def _on_import_file_changed(self, filename: str) -> None:
        """
        slot for textChanged(str) signal of the filename lineedit
        :param filename: newly selected filename
        :return: Nothing
        """
        self.__validate()

        self.logger.debug(self.__class__.__name__, "_on_import_file_changed")

        if not os.path.isfile(os.path.normpath(filename)):
            self.reset()
            # self.logger.warn("Not a file", filename)
            return

        try:
            separator = self.separator
            self.logger.debug("Selected file", "{}".format(filename))
            if separator == "<tabulator>":
                separator = '\t'

            try:
                import_file = open(os.path.normpath(filename), 'r')
            except IOError:
                self.logger.error("Cannot open file", "{}".format(filename))
                return

            cols = import_file.readline().strip().split(separator)
            props = import_file.readline().strip().split(separator)
            data = import_file.readline().strip().split(separator)

            self.logger.debug("cols:\t{}".format(cols))
            self.logger.debug("props:\t{}".format(props))
            self.logger.debug("data:\t{}".format(data))

            import_file.close()

            nr_cols = []
            for col in data:
                try:
                    float(col)
                    nr_cols.append(data.index(col))
                except ValueError:
                    pass

            if len(nr_cols) < 3:
                self.logger.error("Not enough columns",
                                  "Cannot find enough columns. " +
                                  "Maybe use a different separator or another import_tests file")
                self.reset()
                return

            self.__number_columns = [cols[x] for x in nr_cols]
            self.__selectable_columns = cols
            self.import_file_changed.emit(filename)
            self.import_columns_changed.emit()

        except Exception as e:
            self.logger.error("Error", str(ExceptionHandling(e)))
            self.reset()

    def _on_separator_changed(self, _: str = "") -> None:
        """
        slot called, if another separator was selected
        :param _: unused, but necessary for signal connection
        :return: Nothing
        """
        self.__validate()

        self.logger.debug(self.__class__.__name__, "_on_separator_changed")

        self._on_import_file_changed(self.import_file)

    def __on_select_data_file(self):
        """
        slot for selecting and checking of a working directory
        :return: Nothing
        """
        self.__validate()

        self.logger.debug(self.__class__.__name__, "_on_select_data_file")

        path = ""
        if debug:
            # get current module path
            path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            # add relative path to test-data
            path = os.path.join(path, "../../tests/test_data")

        filename = get_file_name(QFileDialog.getOpenFileName(self.dockwidget, "Select data file", path,
                                                             "Data Files(*.txt *.csv *.data);;Any File Type (*)"))

        if filename != "":
            try:
                import_file = open(filename, 'r')
            except IOError as e:
                self.logger.error("Cannot open file", e)
                return

            cols = import_file.readline().strip()
            props = import_file.readline().strip()
            data = import_file.readline().strip()
            import_file.close()

            if '' in [cols, props, data]:
                self.logger.error("Import File Error",
                                  "Cannot process import_tests file, wrong file format!")
                return

            for sep in [';', ',', '\t', '.', '-', '_', '/', '\\']:
                split = cols.split(sep)
                if len(split) < 3:
                    continue

                self.separator = sep
                self.import_file = filename
                break

    def __on_select_working_dir(self) -> None:
        """
        slot for selecting an import_tests data file and processing the corresponding fields inside the import_tests
        data tab.
        :return: Nothing
        """
        self.__validate()

        self.logger.debug(self.__class__.__name__, "_on_select_working_dir")

        path = ""
        if debug:
            # get current module path
            path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            # add relative path to test-data
            path = os.path.join(path, "../../tests/test_data")

        dirname = get_file_name(QFileDialog.getExistingDirectory(self.dockwidget, "Select working directory", path,
                                                                 QFileDialog.ShowDirsOnly |
                                                                 QFileDialog.DontResolveSymlinks))

        if dirname != "" and os.path.isdir(dirname):
            self.working_directory = dirname
        else:
            self.working_directory = ""
            self.logger.error("Cannot set working directory: ", dirname)
