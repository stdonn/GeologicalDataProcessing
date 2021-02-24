# -*- coding: UTF-8 -*-
"""
This module defines views for import processing
"""

from enum import IntEnum, unique
from typing import Dict, List

from GeologicalDataProcessing.controller.import_controller import PointImportController, LineImportController, \
    WellImportController, PropertyImportController, ImportControllersInterface, WellLogImportController
from GeologicalDataProcessing.geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget
from GeologicalDataProcessing.miscellaneous.exception_handler import ExceptionHandler
from GeologicalDataProcessing.miscellaneous.helper import diff
# miscellaneous
from GeologicalDataProcessing.miscellaneous.qgis_log_handler import QGISLogHandler
from GeologicalDataProcessing.models.log_model import PropertyImportModel, PropertyImportDelegate, \
    PropertyImportData, LogImportModel, LogImportDelegate, LogImportData
from GeologicalDataProcessing.services.import_service import ImportService
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QComboBox, QTableView, QHeaderView
from geological_toolbox.properties import PropertyTypes


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

        self.logger = QGISLogHandler(self.__class__.__name__)
        self.__combos = dict()
        self._dwg = dock_widget

        # initialize user interface
        self._import_service = ImportService.get_instance()
        self._import_service.reset_import.connect(self.reset_import)
        self._import_service.import_columns_changed.connect(self._on_import_columns_changed)

        self._table_view: QTableView or None = None
        self._only_number_in_table_view: bool = False
        self._table_model: PropertyImportModel = PropertyImportModel()
        self._dwg.start_import_button.clicked.connect(self._on_start_import)
        self._controller_thread: ImportControllersInterface or None = None

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
    def table_view(self) -> QTableView or None:
        return self._table_view

    @table_view.setter
    def table_view(self, widget: QTableView) -> None:
        if not isinstance(widget, QTableView):
            raise TypeError("submitted object is not of type QTableView: {}", str(widget))

        self._table_model.clear()
        self._table_view = widget
        self._table_view.setModel(self._table_model)

        if self._only_number_in_table_view:
            self._table_view.setItemDelegate(LogImportDelegate())
        else:
            self._table_view.setItemDelegate(PropertyImportDelegate())
        # self._table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self._table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    @property
    def dockwidget(self) -> GeologicalDataProcessingDockWidget:
        """
        Returns the current dockwidget
        :return: the current dockwidget
        """
        return self._dwg

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

        if self._table_view is None:
            self.logger.debug("No list widget specified for additional columns")
            return

        if self._only_number_in_table_view:
            cols = diff(self._import_service.number_columns, selection_list)
        else:
            cols = diff(self._import_service.selectable_columns, selection_list)

        self.logger.debug("selectable_columns: " + str(self._import_service.selectable_columns))
        self.logger.debug("selected_cols: " + str(selection_list))
        self.logger.debug("additional cols: " + str(cols))

        if self._table_view is not None:
            self._table_view.show()
            self._table_view.setEnabled(True)
            self._table_view.clearSelection()

        self._table_model.clear()
        for col in cols:
            property_type = PropertyTypes.FLOAT if col in self._import_service.number_columns else PropertyTypes.STRING
            self._table_model.add(PropertyImportData(name=col[0], unit=col[1], property_type=property_type))

    def _on_import_columns_changed(self) -> None:
        """
        change the import columns
        :return: Nothing
        """
        self.logger.debug("(Interface) _on_import_columns_changed")
        self._connect_selection_changed()
        self.on_selection_changed()

    def _on_start_import(self) -> None:
        self.logger.debug("(Interface) _on_start_import")
        self._update_progress_bar(0)
        self._dwg.progress_bar_layout.setVisible(True)

    def _on_import_failed(self, msg: str) -> None:
        self.logger.debug("(Interface) _on_import_failed")
        self.__import_finished()
        self.logger.error("Import failed", msg, to_messagebar=True)

    def _on_import_finished_with_warnings(self, msg: str) -> None:
        self.logger.debug("(Interface) _on_import_finished_with_warnings")
        self.logger.warn("Import finished with warnings", msg, to_messagebar=True)
        self.__import_finished()

    def _on_import_successful(self):
        self.logger.debug("(Interface) _on_import_successful")
        self.logger.info("Import successful", to_messagebar=True)
        self.__import_finished()

    def _on_cancel_import(self):
        self._controller_thread.cancel_import("Import canceled by user")

    def __import_finished(self):
        self._dwg.progress_bar_layout.setVisible(False)
        self._disconnect_thread()

        self._controller_thread.wait(2000)
        self._controller_thread = None

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

    def get_property_columns(self) -> List[PropertyImportData]:
        selection = set([x.row() for x in self._table_view.selectedIndexes()])
        self.logger.debug("selected rows indices: {}".format(selection))
        erg = [self._table_model.row(x) for x in selection]
        self.logger.debug("Selection:")
        [self.logger.debug("\t{}".format(x)) for x in erg]
        return erg

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
            self.dockwidget.progress_bar.setValue(100)
        else:
            self.dockwidget.progress_bar.setValue(int(value))

    def _connect_selection_changed(self):
        self.logger.debug("_connect_selection_changed")
        [self.__combos[key].currentTextChanged.connect(self.on_selection_changed) for key in self.__combos]

    def _disconnect_selection_changed(self):
        for key in self.__combos:
            try:
                self.__combos[key].currentTextChanged.disconnect(self.on_selection_changed)
            except TypeError:
                # not connected
                pass

    def _connect_thread(self):
        self._controller_thread.import_finished.connect(self._on_import_successful)
        self._controller_thread.import_failed.connect(self._on_import_failed)
        self._controller_thread.import_finished_with_warnings.connect(self._on_import_finished_with_warnings)
        self._controller_thread.update_progress.connect(self._update_progress_bar)
        self._dwg.cancel_import.clicked.connect(self._on_cancel_import)

    def _disconnect_thread(self):
        self._controller_thread.import_finished.disconnect(self._on_import_successful)
        self._controller_thread.import_failed.disconnect(self._on_import_failed)
        self._controller_thread.import_finished_with_warnings.disconnect(self._on_import_finished_with_warnings)
        self._controller_thread.update_progress.disconnect(self._update_progress_bar)
        self._dwg.cancel_import.clicked.disconnect(self._on_cancel_import)


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
        self.table_view = self._dwg.import_columns_points

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.combobox_names = {
            "easting": self._dwg.easting_points,
            "northing": self._dwg.northing_points,
            "altitude": self._dwg.altitude_points,
            "strat": self._dwg.strat_points,
            "strat_age": self._dwg.strat_age_points,
            "set_name": self._dwg.set_name_points,
            "comment": self._dwg.comment_points
        }

    def _on_import_columns_changed(self) -> None:
        """
        change the import columns
        :return: Nothing
        """
        self.logger.debug("_on_import_columns_changed")

        self._disconnect_selection_changed()

        try:
            self.set_combobox_data("easting", [x[0] for x in self._import_service.number_columns], 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("northing", [x[0] for x in self._import_service.number_columns], 1)
            self.set_combobox_data("altitude", [''] + [x[0] for x in self._import_service.number_columns], 3)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("strat", [''] + [x[0] for x in self._import_service.selectable_columns], 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("strat_age", [''] + [x[0] for x in self._import_service.number_columns], 0)
            self.set_combobox_data("set_name", [''] + [x[0] for x in self._import_service.selectable_columns], 0)
            self.set_combobox_data("comment", [''] + [x[0] for x in self._import_service.selectable_columns], 0)
        except Exception as e:
            self.logger.error("Error", str(ExceptionHandler(e)))
            self._import_service.reset()

        super()._on_import_columns_changed()

    def _on_start_import(self) -> None:
        """
        point import requested
        :return: Nothing
        """
        self.logger.debug("_on_start_import")
        super()._on_start_import()

        if self.dockwidget.import_type.currentIndex() != ViewTabs.POINTS:
            self.logger.debug("currentIndex != ViewTabs.POINTS [{}]", self.dockwidget.import_type.currentIndex())
            return

        data = self._import_service.read_import_file()

        selection = dict()
        selection["easting"] = self.combobox_data("easting")
        selection["northing"] = self.combobox_data("northing")
        selection["altitude"] = self.combobox_data("altitude")
        selection["strat"] = self.combobox_data("strat")
        selection["strat_age"] = self.combobox_data("strat_age")
        selection["set_name"] = self.combobox_data("set_name")
        selection["comment"] = self.combobox_data("comment")

        self.logger.debug("starting import...")
        self._controller_thread = PointImportController(data, selection, self.get_property_columns())
        self._connect_thread()
        self._controller_thread.start()


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
        self.table_view = self._dwg.import_columns_lines

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.combobox_names = {
            "easting": self._dwg.easting_lines,
            "northing": self._dwg.northing_lines,
            "altitude": self._dwg.altitude_lines,
            "strat": self._dwg.strat_lines,
            "strat_age": self._dwg.strat_age_lines,
            "set_name": self._dwg.set_name_lines,
            "comment": self._dwg.comment_lines
        }

    def _on_import_columns_changed(self) -> None:
        """
        change the import columns
        :return: Nothing
        """
        self.logger.debug("_on_import_columns_changed")

        self._disconnect_selection_changed()

        try:
            self.set_combobox_data("easting", [x[0] for x in self._import_service.number_columns], 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("northing", [x[0] for x in self._import_service.number_columns], 1)
            self.set_combobox_data("altitude", [''] + [x[0] for x in self._import_service.number_columns], 3)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("strat", [''] + [x[0] for x in self._import_service.selectable_columns], 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("strat_age", [''] + [x[0] for x in self._import_service.number_columns], 0)
            self.set_combobox_data("set_name", [''] + [x[0] for x in self._import_service.selectable_columns], 0)
            self.set_combobox_data("comment", [''] + [x[0] for x in self._import_service.selectable_columns], 0)

        except Exception as e:
            self.logger.error("Error", str(ExceptionHandler(e)))
            self.reset_import()

        super()._on_import_columns_changed()

    def _on_start_import(self) -> None:
        """
        point import requested
        :return: Nothing
        """
        self.logger.debug("_on_start_import")
        super()._on_start_import()

        if self.dockwidget.import_type.currentIndex() != ViewTabs.LINES:
            self.logger.debug("currentIndex != ViewTabs.LINES [{}]", self.dockwidget.import_type.currentIndex())
            return

        data = self._import_service.read_import_file()

        selection = dict()
        selection["easting"] = self.combobox_data("easting")
        selection["northing"] = self.combobox_data("northing")
        selection["altitude"] = self.combobox_data("altitude")
        selection["strat"] = self.combobox_data("strat")
        selection["strat_age"] = self.combobox_data("strat_age")
        selection["set_name"] = self.combobox_data("set_name")
        selection["comment"] = self.combobox_data("comment")

        self.logger.debug("starting import...")
        self._controller_thread = LineImportController(data, selection, self.get_property_columns())
        self._connect_thread()
        self._controller_thread.start()


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

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.combobox_names = {
            "name": self._dwg.name_wells,
            "short_name": self._dwg.short_name_wells,
            "easting": self._dwg.easting_wells,
            "northing": self._dwg.northing_wells,
            "altitude": self._dwg.altitude_wells,
            "total_depth": self._dwg.total_depth_wells,
            "strat": self._dwg.strat_wells,
            "depth_to": self._dwg.depth_to_wells,
            "comment": self._dwg.comment_wells
        }

    def _on_import_columns_changed(self) -> None:
        """
        process the selected import_tests file and set possible values for column combo boxes
        :return: Nothing
        """
        self.logger.debug("_on_import_columns_changed")

        self._disconnect_selection_changed()

        try:
            self.set_combobox_data("name", [x[0] for x in self._import_service.selectable_columns], 1)
            self.set_combobox_data("short_name", [''] + [x[0] for x in self._import_service.selectable_columns], 0)
            self.set_combobox_data("easting", [x[0] for x in self._import_service.number_columns], 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("northing", [x[0] for x in self._import_service.number_columns], 1)
            self.set_combobox_data("altitude", [x[0] for x in self._import_service.number_columns], 2)
            self.set_combobox_data("total_depth", [x[0] for x in self._import_service.number_columns], 3)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("strat", [''] + [x[0] for x in self._import_service.selectable_columns], 0)
            # noinspection SpellCheckingInspection
            self.set_combobox_data("depth_to", [''] + [x[0] for x in self._import_service.selectable_columns], 0)
            self.set_combobox_data("comment", [''] + [x[0] for x in self._import_service.selectable_columns], 0)
        except Exception as e:
            self.logger.error("Error", str(ExceptionHandler(e)))
            self.reset_import()

        super()._on_import_columns_changed()

    def _on_start_import(self) -> None:
        """
        point import requested
        :return: Nothing
        """
        self.logger.debug("_on_start_import")
        super()._on_start_import()

        if self.dockwidget.import_type.currentIndex() != ViewTabs.WELLS:
            self.logger.debug("currentIndex != ViewTabs.WELLS [{}]", self.dockwidget.import_type.currentIndex())
            return

        data = self._import_service.read_import_file()

        selection = dict()
        selection["name"] = self.combobox_data("name")
        selection["short_name"] = self.combobox_data("short_name")
        selection["easting"] = self.combobox_data("easting")
        selection["northing"] = self.combobox_data("northing")
        selection["altitude"] = self.combobox_data("altitude")
        selection["total_depth"] = self.combobox_data("total_depth")
        selection["strat"] = self.combobox_data("strat")
        selection["depth_to"] = self.combobox_data("depth_to")
        selection["comment"] = self.combobox_data("comment")

        self.logger.debug("starting import...")
        self._controller_thread = WellImportController(data, selection, [])
        self._connect_thread()
        self._controller_thread.start()


class PropertyImportView(ImportViewInterface):
    """
    viewer class for the property import procedure
    """

    def __init__(self, dwg: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view
        :param dwg: current GeologicalDataProcessingDockWidget instance
        """
        super().__init__(dwg)
        self.table_view = self._dwg.values_props

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.combobox_names = {
            "id": self._dwg.id_props
        }

    def _on_import_columns_changed(self) -> None:
        """
        change the import columns
        :return: Nothing
        """
        self.logger.debug("_on_import_columns_changed")

        self._disconnect_selection_changed()

        try:
            selection = 0
            for i in range(len(self._import_service.number_columns)):
                if "id" in self._import_service.number_columns[i][0].lower():
                    selection = i
                    break
            self.set_combobox_data("id", [x[0] for x in self._import_service.number_columns], selection)
        except Exception as e:
            self.logger.error("Error", str(ExceptionHandler(e)))
            self._import_service.reset()

        super()._on_import_columns_changed()

    def _on_start_import(self) -> None:
        """
        point import requested
        :return: Nothing
        """
        self.logger.debug("_on_start_import")
        super()._on_start_import()

        if self.dockwidget.import_type.currentIndex() != ViewTabs.PROPERTIES:
            self.logger.debug("currentIndex != ViewTabs.PROPERTIES [{}]", self.dockwidget.import_type.currentIndex())
            return

        data = self._import_service.read_import_file()

        selection = dict()
        selection["id"] = self.combobox_data("id")

        self.logger.debug("starting import...")
        self._controller_thread = PropertyImportController(data, selection, self.get_property_columns())
        self._connect_thread()
        self._controller_thread.start()


class WellLogImportView(ImportViewInterface):
    """
    viewer class for well log import procedure
    """

    def __init__(self, dwg: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialize the view
        :param dwg: current GeologicalDataProcessingDockWidget instance
        """
        super().__init__(dwg)
        self._table_model = LogImportModel()

        self.table_view = self._dwg.values_logs
        self._only_number_in_table_view = True

        # summarize import_tests Widgets
        # noinspection SpellCheckingInspection
        self.combobox_names = {
            "well_name": self._dwg.well_name_logs,
            "depth": self._dwg.depth_logs
        }

    def _on_import_columns_changed(self) -> None:
        """
        change the import columns
        :return: Nothing
        """
        self.logger.debug("_on_import_columns_changed")

        self._disconnect_selection_changed()

        try:
            well_selection = 0
            depth_selection = 0
            for i in range(len(self._import_service.selectable_columns)):
                if "name" in self._import_service.selectable_columns[i][0].lower():
                    well_selection = i
                    break
            for i in range(len(self._import_service.number_columns)):
                if "depth" in self._import_service.number_columns[i][0].lower():
                    depth_selection = i
                    break
            self.set_combobox_data("well_name", [x[0] for x in self._import_service.selectable_columns], well_selection)
            self.set_combobox_data("depth", [x[0] for x in self._import_service.number_columns], depth_selection)
        except Exception as e:
            self.logger.error("Error", str(ExceptionHandler(e)))
            self._import_service.reset()

        super()._on_import_columns_changed()

    def _on_start_import(self) -> None:
        """
        point import requested
        :return: Nothing
        """
        self.logger.debug("_on_start_import")
        super()._on_start_import()

        if self.dockwidget.import_type.currentIndex() != ViewTabs.WELL_LOGS:
            self.logger.debug("currentIndex != ViewTabs.WELL_LOGS [{}]", self.dockwidget.import_type.currentIndex())
            return

        data = self._import_service.read_import_file()

        selection = dict()
        selection["well_name"] = self.combobox_data("well_name")
        selection["depth"] = self.combobox_data("depth")

        self.logger.debug("starting import...")
        self._controller_thread = WellLogImportController(data, selection, self.get_property_columns())
        self._connect_thread()
        self._controller_thread.start()
