# -*- coding: UTF-8 -*-
"""
This module defines views for import processing
"""

from typing import List
from PyQt5.QtCore import pyqtSignal, QObject

from GeologicalDataProcessing.geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget


class PointImportView(QObject):
    """
    viewer class for the point import procedure
    """

    def __init__(self, dockwidget: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view

        :param dockwidget: current GeologicalDataProcessingDockWidget instance
        """

        self.__dockwidget = dockwidget

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.__names = {
            "easting": self.__dockwidget.easting_points,
            "northing": self.__dockwidget.northing_points,
            "altitude": self.__dockwidget.altitude_points,
            "strat": self.__dockwidget.strat_points,
            "strat_age": self.__dockwidget.strat_age_points,
            "set_name": self.__dockwidget.set_name_points,
            "comment": self.__dockwidget.comment_points
        }

        for key in self.__names:
            self.__names[key].currentTextChanged.connect(self._on_combobox_text_change)

        self.__dockwidget.import_file.textChanged.connect(self._on_input_file_change)
        super().__init__()

    # signals
    combobox_changed = pyqtSignal(list)
    """data changed signal which gives the index or name of the changed column and the newly selected text"""
    input_file_changed = pyqtSignal(str)
    """signal send, when the import file name changes"""

    # slots
    def _on_combobox_text_change(self, _) -> None:
        """
        Emits the combobox_changed signal with a list of changed text
        :return: Nothing
        """
        selection_list = [self.__names[key].currentText() for key in self.__names]
        self.combobox_changed.emit(selection_list)

    def _on_input_file_change(self, file: str) -> None:
        """
        slot for textChanged(str) signal of the filename lineedit
        :param file: newly selected filename
        :return: Nothing
        """
        self.input_file_changed.emit(file)

    # public functions
    def combobox_data(self, index: int or str) -> str:
        """
        Returns the currently selected item of the gui element with the given index
        :param index: index of the requested gui element as integer or string
        :return: Returns the data at the given index
        :raises IndexError: if index is not part in the available list
        """

        if isinstance(index, int):
            index = [self.__names.keys()][index]
        else:
            index = str(index)

        if index not in self.__names:
            raise IndexError("{} is not available".format(index))

        return self.__names[index].currentText()

    def get_name(self, index: int) -> str or None:
        """
        Returns the name of the combobox with the given index
        :param index: index of the requested combobox
        :return: Returns the name of the combobox with the given index
        :raises IndexError: if the requested index is not in the list
        :raises ValueError: if the index is not convertible to an integer
        """
        index = int(index)
        if 0 <= index < len(self.__names.keys()):
            return list(self.__names.keys())[0]

    def get_names(self):
        """
        Returns a list of the combobox names
        :return: Returns a list of the combobox names
        """
        return list(self.__names.keys())

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
            index = [self.__names.keys()][index]
        else:
            index = str(index)

        if index not in self.__names:
            raise IndexError("{} is not available".format(index))

        if isinstance(default_index, int):
            raise TypeError("default_index({}) is not an instance of int!")

        self.__names[index].clear()
        for item in values:
            self.__names[index].addItem(str(item))

        if not (0 <= default_index <= len(values)):
            default_index = 0
        self.__names[index].setCurrentIndex(default_index)
