# -*- coding: UTF-8 -*-
"""
This module defines views for import processing
"""

from PyQt5.QtCore import pyqtSignal

from GeologicalDataProcessing.geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget


class PointImportView:
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

    # slots
    def _on_data_change(self, *args) -> None:
        """
        slot for all gui-data-changed-signals
        :param args: possible arguments which could be submited
        :return: Nothing
        """

