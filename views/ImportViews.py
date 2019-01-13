# -*- coding: UTF-8 -*-
"""
This module defines views for import processing
"""

from typing import Dict, List
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QComboBox

from GeologicalDataProcessing.geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget
from GeologicalDataProcessing.miscellaneous.QGISDebugLog import QGISDebugLog
from GeologicalDataProcessing.services.ImportService import ImportService


class ImportViewInterface(QObject):
    """
    interface class defining signals and slots for all import views
    """
    logger = QGISDebugLog()

    def __init__(self, dockwidget: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view
        :param dockwidget: current GeologicalDataProcessingDockWidget instance
        """

        self.logger.debug(self.__class__.__name__, "__init__")

        self.__combos = dict()
        self.__dwg = dockwidget

        # initialize user interface
        self._import_service = ImportService.get_instance()
        self._import_service.reset_import.connect(self.reset_import)

        super().__init__()

    def _connect_combo_listener(self):
        """
        connects all combobox elements to the _on_selection_change slot
        :return: Nothing
        """
        [combo.currentIndexChanged.connect(self._on_selection_change) for combo in self.__combos]

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
        Sets a new dictionary to the combobox list. Disconnects the old ones and connects the new to the
        _on_selection_change slot
        :param combo_dict: dictionary with new combobox elements
        :return: Nothing
        :raises TypeError: if a dictionary value is not an instance of QComboBox or a key is not a str. Sets an empty
        dictionary instead
        """
        [self.__combos[key].currentTextChanged.disconnect(self._on_selection_change) for key in self.__combos]

        for key in combo_dict:
            if not isinstance(key, str):
                self.__combos = dict()
                raise TypeError("{} is not a string".format(str(key)))
            if not isinstance(combo_dict[key], QComboBox):
                self.__combos = dict()
                raise TypeError("{} is not an instance of QComboBox".format(str(key)))

        self.__combos = combo_dict
        [self.__combos[key].currentTextChanged.connect(self._on_selection_change) for key in self.__combos]

    @property
    def dockwidget(self) -> GeologicalDataProcessingDockWidget:
        """
        Returns the current dockwidget
        :return: the current dockwidget
        """
        return self.__dwg

    #
    # signals
    #

    selection_changed = pyqtSignal(list)
    """data changed signal which gives the index or name of the changed column and the newly selected text"""

    #
    # slots
    #

    def _on_selection_change(self, _) -> None:
        """
        Emits the combobox_changed signal with a list of changed text
        :return: Nothing
        """
        selection_list = [self.combobox_names[key].currentText() for key in self.combobox_names]
        self.selection_changed.emit(selection_list)

    #
    # public functions
    #

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

        if not isinstance(default_index, int):
            raise TypeError("default_index({}) is not an instance of int!".format(default_index))

        self.combobox_names[index].clear()
        for item in values:
            self.combobox_names[index].addItem(str(item))

        if not (0 <= default_index <= len(values)):
            default_index = 0
        self.combobox_names[index].setCurrentIndex(default_index)

    def reset_import(self) -> None:
        """
        Clears all import combo boxes, in case of a failure
        :return: Nothing
        """
        [self.set_combobox_data(name, []) for name in self.get_names()]


class PointImportView(ImportViewInterface):
    """
    viewer class for the point import procedure
    """

    def __init__(self, dwg: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view
        :param dwg: current GeologicalDataProcessingDockWidget instance
        """

        self.logger.debug(self.__class__.__name__, "__init__")

        super().__init__(dwg)

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.combobox_names = {
            "easting": self._import_service.dockwidget.easting_points,
            "northing": self._import_service.dockwidget.northing_points,
            "altitude": self._import_service.dockwidget.altitude_points,
            "strat": self._import_service.dockwidget.strat_points,
            "strat_age": self._import_service.dockwidget.strat_age_points,
            "set_name": self._import_service.dockwidget.set_name_points,
            "comment": self._import_service.dockwidget.comment_points
        }


class LineImportView(ImportViewInterface):
    """
    viewer class for the point import procedure
    """

    def __init__(self, dwg: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view
        :param dwg: current GeologicalDataProcessingDockWidget instance
        """

        self.logger.debug(self.__class__.__name__, "__init__")

        super().__init__(dwg)

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.combobox_names = {
            "identifier": self._import_service.dockwidget.identifier_lines,
            "easting": self._import_service.dockwidget.easting_lines,
            "northing": self._import_service.dockwidget.northing_lines,
            "altitude": self._import_service.dockwidget.altitude_lines,
            "strat": self._import_service.dockwidget.strat_lines,
            "strat_age": self._import_service.dockwidget.strat_age_lines,
            "set_name": self._import_service.dockwidget.set_name_lines,
            "comment": self._import_service.dockwidget.comment_lines
        }
