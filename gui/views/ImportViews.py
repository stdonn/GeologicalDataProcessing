# -*- coding: UTF-8 -*-
"""
This module defines views for import processing
"""

import os.path
from typing import Dict, List
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QComboBox
from qgis.core import QgsCoordinateReferenceSystem

from GeologicalDataProcessing.geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget


class ImportViewInterface(QObject):
    """
    interface class defining signals and slots for all import views
    """

    def __init__(self, dockwidget: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view
        :param dockwidget: current GeologicalDataProcessingDockWidget instance
        """
        self.__combos = dict()
        self.__dwg = dockwidget

        self.__dwg.import_file.textChanged.connect(self._on_import_file_change)
        self.__db = ""
        self.__separator = ";"
        self.__working_dir = ""

        self.db = self.__dwg.database_file.text()
        self.separator = self.__dwg
        self.working_directory = self.__dwg.working_dir.text()

        # initialize user interface
        self.__dwg.separator.addItems([';', ',', '<tabulator>', '.', '-', '_', '/', '\\'])

        super().__init__()

    # setter and getter
    @property
    def dockwidget(self) -> GeologicalDataProcessingDockWidget:
        """
        Returns the currently active plugin-dockwidget
        :return: returns the currently active plugin-dockwidget
        """
        return self.__dwg

    @property
    def combobox_names(self) -> Dict:
        """
        Returns a dictionary of comboboxes for the current view
        :return: returns a dictionary of comboboxes for the current view
        """
        return self.__combos

    @combobox_names.setter
    def combobox_names(self, combo_dict: Dict) -> None:
        """
        Sets a new dictionary to the combobox list. Disconnects the old ones and connects the new tp the _on_selection_change slot
        :param combo_dict: dictionary with new combobox elements
        :return: Nothing
        :raises TypeError: if a dictionary value is not an instance of QComboBox or a key is not a str. Sets an empty dictionary instead
        """
        [self.__combos[key].disconnect(self._on_selection_change) for key in self.__combos]

        for key in combo_dict:
            if not isinstance(key, str):
                self.__combos = dict()
                raise TypeError("{} is not a string".format(str(key)))
            if not isinstance(combo_dict[key], QComboBox):
                self.__combos = dict()
                raise TypeError("{} is not an instance of QComboBox".format(str(key)))

        self.__combos = combo_dict
        [self.__combos[key].connect(self._on_selection_change) for key in self.__combos]

    @property
    def database(self):
        """
        Returns the currently selected database
        :return: returns the currently selected database
        """
        return self.__db

    @database.setter
    def database(self, db: str) -> None:
        """
        database setter
        :param db: new path to the database (or an empty path for in-memory usage)
        :return: Nothing
        :raises ValueError: if the file doesn't exists
        """
        db = os.path.normpath(str(db))
        if (os.path.exists(db) and not os.path.isfile(db)) or db == "":
            self.__db = db
        else:
            raise ValueError("Database does not exists: {}".format(db))

    @property
    def working_directory(self) -> str:
        """
        Returns the currently selected working directory
        :return: returns the currently selected working directory
        """
        return self.__working_dir

    @working_directory.setter
    def working_directory(self, work_dir: str) -> None:
        """
        working directory setter
        :param work_dir: new working directory (or an empty path for in-memory usage)
        :return: Nothing
        :raises ValueError: if the path doesn't exist or isn't a directory
        """
        work_dir = os.path.normpath(str(work_dir))
        if (os.path.exists(work_dir) and os.path.isdir(work_dir)) or work_dir == "":
            self.__working_dir = work_dir
        else:
            raise ValueError("Committed value is not a directory: {}".format(work_dir))

    @property
    def separator(self):
        """
        get / set the separator of the input file
        possible values are: ';', ',', '\t', '.', '-', '_', '/', '\\'
        :return: returns the currently selected separator
        """
        sep = self.__dwg.separator.currentText()
        if sep == "<tabulator>":
            sep = '\t'
        return sep

    @separator.setter
    def separator(self, sep):
        """
        get / set the separator of the input file
        possible values are: ';', ',', '\t', '.', '-', '_', '/', '\\'
        :return: nothing
        :param sep: new separator
        :return: Nothing
        :raises ValueError: if sep is not in list of possible values.
        """
        if sep not in [';', ',', '\t', '.', '-', '_', '/', '\\']:
            raise ValueError("{} as separator is not allowed!")

        if sep == '\t':
            sep = "<tabulator>"

        self.__dwg.setCurrentText(sep)

    @property
    def crs(self) -> QgsCoordinateReferenceSystem:
        """
        gets / sets the Reference System in QGIS format
        :return: current coordinate reference system
        :raises TypeError: if crs is an instance of QgsCoordinateReferenceSystem
        :raises ValueError: if the committed reference system is not valid
        """
        return self.__dwg.mQgsProjectionSelectionWidget.crs()

    @crs.setter
    def crs(self, _crs:QgsCoordinateReferenceSystem) -> None:
        """
        gets / sets the Reference System in QGIS format
        :return: current coordinate reference system
        :raises TypeError: if crs is an instance of QgsCoordinateReferenceSystem
        """
        if not isinstance(_crs, QgsCoordinateReferenceSystem):
            raise TypeError("committed value is not of type QgsCoordinateReferenceSystem!")

        if not _crs.isValid():
            raise ValueError("committed reference system is not valid")

        self.__dwg.mQgsProjectionSelectionWidget.setCrs(_crs)

    # signals
    crs_changed = pyqtSignal(QgsCoordinateReferenceSystem)
    """signal send, when the selected coordinate reference system changes"""
    import_file_changed = pyqtSignal(str)
    """signal send, when the import file name changes"""
    selection_changed = pyqtSignal(list)
    """data changed signal which gives the index or name of the changed column and the newly selected text"""


    # slots
    def _on_crs_changes(self) -> None:
        """
        slot called, when the selected coordinate reference system has changed
        :return: Nothing
        """
        self.crs_changed.emit(self.__dwg.mQgsProjectionSelectionWidget.crs())

    def _on_import_file_change(self, file: str) -> None:
        """
        slot for textChanged(str) signal of the filename lineedit
        :param file: newly selected filename
        :return: Nothing
        """
        self.import_file_changed.emit(file)

    def _on_selection_change(self, _) -> None:
        """
        Emits the combobox_changed signal with a list of changed text
        :return: Nothing
        """
        selection_list = [self.combobox_names[key].currentText() for key in self.combobox_names]
        self.selection_changed.emit(selection_list)

    # public functions
    def combobox_data(self, index: int or str) -> str:
        """
        Returns the currently selected item of the gui element with the given index
        :param index: index of the requested gui element as integer or string
        :return: Returns the data at the given index
        :raises IndexError: if index is not part in the available list
        """

        if isinstance(index, int):
            index = [self.combobox_names.keys()][index]
        else:
            index = str(index)

        if index not in self.combobox_names:
            raise IndexError("{} is not available".format(index))

        return self.combobox_names[index].currentText()

    def get_name(self, index: int) -> str or None:
        """
        Returns the name of the combobox with the given index
        :param index: index of the requested combobox
        :return: Returns the name of the combobox with the given index
        :raises IndexError: if the requested index is not in the list
        :raises ValueError: if the index is not convertible to an integer
        """
        index = int(index)

        if 0 <= index < len(self.combobox_names.keys()):
            return list(self.combobox_names.keys())[0]

    def get_names(self):
        """
        Returns a list of the combobox names
        :return: Returns a list of the combobox names
        """
        return list(self.combobox_names.keys())

    def set_combobox_data(self, index: int or str, values: List[str], default_index: int = 0) -> None:
        """
        Sets the committed values list to the gui combobox elements for the given index
        :param index: index of the requested gui element as integer or string
        :param values: new values for the combo boxes as a list of strings
        :param default_index: default selected index. If no default value is given, or the index is not part of the
                              list, the first entry will be selected by default
        :return: Returns, if the data setting was successful
        :raises IndexError: if index is not part in the available list
        :raises TypeError: if default_index is not an instance of int
        """

        if isinstance(index, int):
            index = [self.combobox_names.keys()][index]
        else:
            index = str(index)

        if index not in self.combobox_names:
            raise IndexError("{} is not available".format(index))

        if isinstance(default_index, int):
            raise TypeError("default_index({}) is not an instance of int!")

        self.combobox_names[index].clear()
        for item in values:
            self.combobox_names[index].addItem(str(item))

        if not (0 <= default_index <= len(values)):
            default_index = 0
        self.combobox_names[index].setCurrentIndex(default_index)


class PointImportView(ImportViewInterface):
    """
    viewer class for the point import procedure
    """

    def __init__(self, dwg: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view
        :param dwg: current GeologicalDataProcessingDockWidget instance
        """
        super().__init__(dwg)

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.combobox_names = {
            "easting": self.dockwidget.easting_points,
            "northing": self.dockwidget.northing_points,
            "altitude": self.dockwidget.altitude_points,
            "strat": self.dockwidget.strat_points,
            "strat_age": self.dockwidget.strat_age_points,
            "set_name": self.dockwidget.set_name_points,
            "comment": self.dockwidget.comment_points
        }
