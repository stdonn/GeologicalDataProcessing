# -*- coding: UTF-8 -*-
"""
This module defines views for import processing
"""

from enum import IntEnum, unique
from typing import Dict, List
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QComboBox, QListWidget

from GeologicalDataProcessing.geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget
from GeologicalDataProcessing.miscellaneous.qgis_log_handler import QGISLogHandler
from GeologicalDataProcessing.services.import_service import ImportService

# miscellaneous
from GeologicalDataProcessing.miscellaneous.helper import diff
from GeologicalDataProcessing.miscellaneous.exception_handler import ExceptionHandler


@unique
class ViewTabs(IntEnum):
    POINTS = 0
    LINES = 1
    WELLS = 2
    PROPERTIES = 3
    WELL_LOGS = 4


class ImportViewInterface(QObject):
    """
    interface class defining signals and slots for all import views
    """

    def __init__(self, dock_widget: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view
        :param dock_widget: current GeologicalDataProcessingDockWidget instance
        """

        self.logger = QGISLogHandler(ImportViewInterface.__name__)
        self.__combos = dict()
        self.__dwg = dock_widget

        # initialize user interface
        self._import_service = ImportService.get_instance()
        self._import_service.reset_import.connect(self.reset_import)
        self._import_service.import_columns_changed.connect(self._on_import_columns_changed)

        self._list_widget: QListWidget or None = None

        super().__init__()

    def _connect_combo_listener(self):
        """
        connects all combobox elements to the on_selection_changed slot
        :return: Nothing
        """
        [combo.currentIndexChanged.connect(self.on_selection_changed) for combo in self.__combos]

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
        on_selection_changed slot
        :param combo_dict: dictionary with new combobox elements
        :return: Nothing
        :raises TypeError: if a dictionary value is not an instance of QComboBox or a key is not a str. Sets an empty
        dictionary instead
        """

        self._disconnect_selection_changed()

        for key in combo_dict:
            if not isinstance(key, str):
                self.__combos = dict()
                raise TypeError("{} is not a string".format(str(key)))
            if not isinstance(combo_dict[key], QComboBox):
                self.__combos = dict()
                raise TypeError("{} is not an instance of QComboBox".format(str(key)))

        self.__combos = combo_dict
        self._connect_selection_changed()

    @property
    def list_widget(self) -> QListWidget or None:
        return self._list_widget

    @list_widget.setter
    def list_widget(self, widget: QListWidget) -> None:
        if not isinstance(widget, QListWidget):
            raise TypeError("submitted object is not of type QListWidget: {}", str(widget))

        self._list_widget = widget

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

    start_import = pyqtSignal()
    """signal to start the data import through an ImportController Thread"""

    #
    # slots
    #

    def on_selection_changed(self, _=None) -> None:
        """
        Emits the combobox_changed signal with a list of changed text
        :return: Nothing
        """
        selection_list = [self.combobox_names[key].currentText() for key in self.combobox_names]
        self.selection_changed.emit(selection_list)

        if self._list_widget is None:
            # self.logger.debug("No list widget specified for additional columns")
            return

        cols = diff(self._import_service.selectable_columns, selection_list)

        self.logger.debug("selectable_columns: " + str(self._import_service.selectable_columns))
        self.logger.debug("selected_cols: " + str(selection_list))
        self.logger.debug("additional cols: " + str(cols))

        self._list_widget.show()
        self._list_widget.setEnabled(True)
        self._list_widget.clear()
        self._list_widget.addItems(cols)

    def _on_import_columns_changed(self) -> None:
        """
        change the import columns
        :return: Nothing
        """
        self.logger.debug("(Interface) _on_import_columns_changed")
        self._connect_selection_changed()
        self.on_selection_changed()

    def _on_start_import(self) -> None:
        pass

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

    #
    # protected functions
    #

    def _update_progress_bar(self, value):
        """
        slot to set the current progress bar value
        :param value: value in percent
        :return: nothing
        """
        self.logger.debug("Update progressbar with value {} called".format(value))
        if value < 0:
            self.dockwidget.progress_bar.setValue(0)
        elif value > 100:
            self.progress_bar.setValue(100)
        else:
            self.progress_bar.setValue(int(value))

    def _connect_selection_changed(self):
        [self.__combos[key].currentTextChanged.connect(self.on_selection_changed) for key in self.__combos]

    def _disconnect_selection_changed(self):
        for key in self.__combos:
            try:
                self.__combos[key].currentTextChanged.disconnect(self.on_selection_changed)
            except TypeError:
                # not connected
                pass


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
        self.logger = QGISLogHandler(PointImportView.__name__)

        self.list_widget = self._import_service.dockwidget.import_columns_points

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

    def get_property_columns(self):
        return [item.text() for item in self.dockwidget.import_columns_points.selectedItems()]

    def _on_import_columns_changed(self) -> None:
        """
        change the import columns
        :return: Nothing
        """
        self.logger.debug("_on_import_columns_changed")

        self._disconnect_selection_changed()

        try:
            self.set_combobox_data("easting", self._import_service.number_columns, 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("northing", self._import_service.number_columns, 1)
            self.set_combobox_data("altitude", [''] + self._import_service.number_columns, 3)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("strat", [''] + self._import_service.selectable_columns, 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("strat_age", [''] + self._import_service.number_columns, 0)
            self.set_combobox_data("set_name", [''] + self._import_service.selectable_columns, 0)
            self.set_combobox_data("comment", [''] + self._import_service.selectable_columns, 0)
        except Exception as e:
            self.logger.error("Error", str(ExceptionHandler(e)))
            self._import_service.reset()

        super()._on_import_columns_changed()

    def _on_start_import(self) -> None:
        """
        point import requested
        :return: Nothing
        """

        if self.dockwidget.import_type.currentIndex() != ViewTabs.POINTS:
            return

        data = self._import_service.read_import_file()

        onekey = data[next(iter(data.keys()))]["values"]
        # import json
        # self.logger.info(json.dumps(onekey, indent=2))
        count = len(onekey)

        selection = dict()
        selection["east"] = self.combobox_data("easting")
        selection["north"] = self.combobox_data("northing")
        selection["alt"] = self.combobox_data("altitude")
        selection["strat"] = self.combobox_data("strat")
        selection["age"] = self.combobox_data("strat_age")
        selection["set_name"] = self.combobox_data("set_name")
        selection["comment"] = self.combobox_data("comment")


class LineImportView(ImportViewInterface):
    """
    viewer class for the point import procedure
    """

    def __init__(self, dwg: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view
        :param dwg: current GeologicalDataProcessingDockWidget instance
        """
        super().__init__(dwg)
        self.logger = QGISLogHandler(LineImportView.__name__)

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.combobox_names = {
            "easting": self._import_service.dockwidget.easting_lines,
            "northing": self._import_service.dockwidget.northing_lines,
            "altitude": self._import_service.dockwidget.altitude_lines,
            "strat": self._import_service.dockwidget.strat_lines,
            "strat_age": self._import_service.dockwidget.strat_age_lines,
            "set_name": self._import_service.dockwidget.set_name_lines,
            "comment": self._import_service.dockwidget.comment_lines
        }

    def get_property_columns(self):
        return [item.text() for item in self.dockwidget.import_columns_lines.selectedItems()]

    def _on_import_columns_changed(self) -> None:
        """
        process the selected import_tests file and set possible values for column combo boxes
        :return: Nothing
        """
        self.logger.debug("_on_import_columns_changed")

        self._disconnect_selection_changed()

        try:
            self.set_combobox_data("easting", self._import_service.number_columns, 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("northing", self._import_service.number_columns, 1)
            self.set_combobox_data("altitude", [''] + self._import_service.number_columns, 3)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("strat", [''] + self._import_service.selectable_columns, 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("strat_age", [''] + self._import_service.number_columns, 0)
            self.set_combobox_data("set_name", [''] + self._import_service.selectable_columns, 0)
            self.set_combobox_data("comment", [''] + self._import_service.selectable_columns, 0)

        except Exception as e:
            self.logger.error("Error", str(ExceptionHandler(e)))
            self.reset_import()

        super()._on_import_columns_changed()


class WellImportView(ImportViewInterface):
    """
    viewer class for the point import procedure
    """

    def __init__(self, dwg: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view
        :param dwg: current GeologicalDataProcessingDockWidget instance
        """
        super().__init__(dwg)
        self.logger = QGISLogHandler(WellImportView.__name__)

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.combobox_names = {
            "name": self._import_service.dockwidget.name_wells,
            "short_name": self._import_service.dockwidget.short_name_wells,
            "easting": self._import_service.dockwidget.easting_wells,
            "northing": self._import_service.dockwidget.northing_wells,
            "altitude": self._import_service.dockwidget.altitude_wells,
            "total_depth": self._import_service.dockwidget.total_depth_wells,
            "strat": self._import_service.dockwidget.strat_wells,
            "depth_to": self._import_service.dockwidget.depth_to_wells,
            "comment": self._import_service.dockwidget.comment_wells
        }

    def _on_import_columns_changed(self) -> None:
        """
        process the selected import_tests file and set possible values for column combo boxes
        :return: Nothing
        """
        self.logger.debug("_on_import_columns_changed")

        self._disconnect_selection_changed()

        try:
            self.set_combobox_data("name", self._import_service.selectable_columns, 1)
            self.set_combobox_data("short_name", [''] + self._import_service.selectable_columns, 0)
            self.set_combobox_data("easting", self._import_service.number_columns, 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("northing", self._import_service.number_columns, 1)
            self.set_combobox_data("altitude", self._import_service.number_columns, 2)
            self.set_combobox_data("total_depth", self._import_service.number_columns, 3)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("strat", [''] + self._import_service.selectable_columns, 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("depth_to", [''] + self._import_service.selectable_columns, 0)
            self.set_combobox_data("comment", [''] + self._import_service.selectable_columns, 0)
        except Exception as e:
            self.logger.error("Error", str(ExceptionHandler(e)))
            self.reset_import()

        super()._on_import_columns_changed()
