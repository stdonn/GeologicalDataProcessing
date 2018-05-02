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
        super().__init__()

    # signals
    data_changed = pyqtSignal([int], ["QString"])
    """data changed signal which gives the index or name of the changed column"""

    # slots
    def _on_data_change(self, *args) -> None:
        """
        slot for all gui-data-changed-signals
        :param args: possible arguments which could be submitted
        :return: Nothing
        """
        pass

    def data(self, index: int or str) -> str:
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

    def set_data(self, index: int or str, values: List[str], default_index: int = 0) -> None:
        """
        Sets the committed values list to the gui combobox element for the given index
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
