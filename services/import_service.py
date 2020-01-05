# -*- coding: UTF-8 -*-
"""
module to provide the import service
"""

import inspect
import os

from typing import Dict, List, Tuple

from qgis.core import QgsCoordinateReferenceSystem

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QFileDialog

from GeologicalDataProcessing.geological_data_processing import GeologicalDataProcessingDockWidget
from GeologicalDataProcessing.miscellaneous.config_handler import ConfigHandler
from GeologicalDataProcessing.miscellaneous.exception_handler import ExceptionHandler
from GeologicalDataProcessing.miscellaneous.qgis_log_handler import QGISLogHandler
from GeologicalDataProcessing.miscellaneous.helper import get_file_name


class ImportService(QObject):
    """
    Singleton class controlling the import procedures
    """
    __instance = None
    __dwg = None
    __selectable_columns: List[Tuple[str, str]] = list()
    __number_columns: List[Tuple[str, str]] = list()

    logger = QGISLogHandler("ImportService")

    @staticmethod
    def get_instance(dwg: GeologicalDataProcessingDockWidget = None) -> "ImportService":
        """
        Creates a new object instance if no object exists or updates the existing one.
        :return: The single instance of this class
        """

        if ImportService.__instance is None:
            ImportService.logger.debug(ImportService.__class__.__name__, "Create new ImportService instance")
            ImportService(dwg)

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
            self.separator = ","
            self.import_file = ""
            self.__config_handler = ConfigHandler()

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

            self.dockwidget.start_import_button.setEnabled(False)
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

    def get_crs(self):
        """
        returns the selected coordinate reference system
        :return: the selected coordinate reference system
        """
        # from qgis.gui import QgsProjectionSelectionWidget
        # wdg = QgsProjectionSelectionWidget()
        return self.dockwidget.reference.crs()

    @property
    def crs(self) -> QgsCoordinateReferenceSystem:
        """
        gets / sets the Reference System in QGIS format
        :return: current coordinate reference system
        :raises TypeError: if crs is an instance of QgsCoordinateReferenceSystem
        :raises ValueError: if the committed reference system is not valid
        """
        self.__validate()

        return self.dockwidget.reference.crs()

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

        self.dockwidget.reference.setCrs(_crs)

    @property
    def selectable_columns(self) -> List[Tuple[str, str]]:
        """
        Returns a list of selectable columns
        :return: Returns a list of selectable columns
        """
        return ImportService.__selectable_columns

    @property
    def number_columns(self) -> List[Tuple[str, str]]:
        """
        Returns a list of number columns
        :return: Returns a list of number columns
        """
        return ImportService.__number_columns

    #
    # private functions
    #

    def __validate(self):
        """
        Validates, if the service can be executed
        :return: Nothing
        :raises
        """

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

        self.logger.debug("reset")

        ImportService.__selectable_columns = list()
        ImportService.__number_columns = list()
        self.dockwidget.start_import_button.setEnabled(False)
        self.import_file_changed.emit("")
        self.reset_import.emit()

    def read_import_file(self) -> Dict:
        """
        Read the import file and return the resulting dictionary
        :return: the resulting dictionary
        """
        self.logger.debug("reading import file {}".format(self.import_file))

        try:
            separator = self.separator
            if separator == "<tabulator>":
                separator = '\t'

            result = dict()

            with open(os.path.normpath(self.import_file), 'r') as import_file:

                cols = import_file.readline().strip().split(separator)
                props = import_file.readline().strip().split(separator)

                if len(cols) < 2:
                    raise ImportError("Cannot read import file, not enough columns for selected separator")

                self.logger.debug("cols:\t{}".format(cols))
                self.logger.debug("props:\t{}".format(props))

                for i in range(0, len(cols)):
                    try:
                        p = props[i]
                    except IndexError:
                        p = ""

                    result[cols[i]] = {
                        "property": p,
                        "values": list()
                    }

                for line in import_file:
                    line = line.strip().split(separator)
                    for i in range(0, len(line)):
                        if i >= len(cols):
                            break

                        result[cols[i]]["values"].append(line[i])

                    # fill the rest with empty values
                    for i in range(len(line), len(cols)):
                        result[cols[i]]["values"].append("")

            return result

        except IOError:
            ("Cannot open file", "{}".format(self.import_file))
        except Exception as e:
            self.logger.error("Error", str(ExceptionHandler(e)))
            self.reset()

    #
    # slots
    #

    def _on_crs_changed(self) -> None:
        """
        slot called, when the selected coordinate reference system has changed
        :return: Nothing
        """
        self.__validate()

        self.logger.debug("_on_crs_changed")

        self.crs_changed.emit(self.dockwidget.mQgsProjectionSelectionWidget.crs())

    def _on_import_file_changed(self, filename: str) -> None:
        """
        slot for textChanged(str) signal of the filename lineedit
        :param filename: newly selected filename
        :return: Nothing
        """
        self.__validate()

        self.logger.debug("_on_import_file_changed")

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

            cols = import_file.readline().strip()

            if len(cols.split(separator)) < 3:
                self.separator = self.find_separator(cols)
                separator = self.separator
                self.logger.debug("Selected another separator: {}"
                                  .format("<tabulator>" if separator == '\t' else separator))

            cols = cols.split(separator)
            units = import_file.readline().strip().split(separator)
            data = import_file.readline().strip().split(separator)

            self.logger.debug("cols:\t{}".format(cols))
            self.logger.debug("units:\t{}".format(units))
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
                self.logger.warn("Not enough columns",
                                 "Cannot find enough columns. " +
                                 "Maybe use a different separator or another import file")
                self.reset()
                return

            ImportService.__selectable_columns = list()
            for i in range(len(cols)):
                name = cols[i]
                try:
                    unit = units[i]
                except IndexError:
                    unit = ""
                ImportService.__selectable_columns.append((name, unit))

            ImportService.__number_columns = list()
            for i in nr_cols:
                name = cols[i]
                try:
                    unit = units[i]
                except IndexError:
                    unit = ""
                ImportService.__number_columns.append((name, unit))

            self.dockwidget.start_import_button.setEnabled(True)
            self.import_file_changed.emit(filename)
            self.import_columns_changed.emit()

        except Exception as e:
            self.logger.error("Error", str(ExceptionHandler(e)))
            self.reset()

    @staticmethod
    def find_separator(line: str) -> str:
        for sep in [';', ',', '\t', '.', '-', '_', '/', '\\']:
            if len(line.split(sep)) >= 3:
                return sep
        else:
            return ';'

    def _on_separator_changed(self, _: str = "") -> None:
        """
        slot called, if another separator was selected
        :param _: unused, but necessary for signal connection
        :return: Nothing
        """
        self.__validate()

        self.logger.debug("_on_separator_changed")

        self._on_import_file_changed(self.import_file)

    def __on_select_data_file(self):
        """
        slot for selecting and checking of a working directory
        :return: Nothing
        """
        self.__validate()

        self.logger.debug("_on_select_data_file")

        path = self.__config_handler.get("General", "current working path")
        # if config.debug:
        # get current module path
        # path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        # add relative path to test-data
        # path = os.path.join(path, "../../tests/test_data")

        # noinspection PyCallByClass,PyArgumentList
        filename = get_file_name(QFileDialog.getOpenFileName(self.dockwidget, "Select data file", path,
                                                             "Data Files(*.txt *.csv *.data);;Any File Type (*)"))
        if filename != "":
            self.__config_handler.set("General", "current working path", os.path.dirname(filename))
            try:
                import_file = open(filename, 'r')
            except IOError as e:
                self.logger.error("Cannot open file", e)
                self.dockwidget.start_import_button.setEnabled(False)
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
