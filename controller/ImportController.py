# -*- coding: UTF-8 -*-
"""
Defines controller for the data import_tests
"""
from GeologicalToolbox.Geometries import GeoPoint, Line
from GeologicalToolbox.Stratigraphy import StratigraphicObject
from PyQt5.QtWidgets import QListWidget
from typing import List

from GeologicalToolbox.DBHandler import AbstractDBObject
from GeologicalDataProcessing.views.ImportViews import ImportViewInterface, PointImportView, LineImportView
from GeologicalDataProcessing.miscellaneous.ExceptionHandling import ExceptionHandling
from GeologicalDataProcessing.miscellaneous.QGISDebugLog import QGISDebugLog
from GeologicalDataProcessing.services.DatabaseService import DatabaseService
from GeologicalDataProcessing.services.ImportService import ImportService

# miscellaneous
from GeologicalDataProcessing.miscellaneous.Helper import diff


class ImportControllersInterface:
    """
    Basic interface for all import_tests controller
    """
    logger = QGISDebugLog()

    def __init__(self, view: ImportViewInterface = None) -> None:
        """
        :param view: ImportViewInterface
        """

        self.logger.debug(self.__class__.__name__, "__init__")

        self._view: ImportViewInterface = view

        self._import_service = ImportService.get_instance()
        self._import_service.import_columns_changed.connect(self._on_import_columns_changed)

        self._view.selection_changed.connect(self._on_selection_changed)
        self._view.dockwidget.start_import_button.clicked.connect(self._on_start_import)

        self._list_widget: QListWidget = None
        self._selectable_columns = []
        self._number_columns = []
        self._working_dir = []
        self.__db_objects: List[AbstractDBObject] = list()

    def _on_import_columns_changed(self) -> None:
        """
        change the import columns
        :return: Nothing
        """

        self.logger.debug(self.__class__.__name__, "_on_import_columns_changed")

        self._selectable_columns = self._import_service.selectable_columns

    def _on_import_file_changed(self, filename: str) -> None:
        """
        Test slot if the import file changed
        :param filename: importfile
        :return: Nothing
        """

        self.logger.debug(self.__class__.__name__, "_on_import_file_changed(" + filename + ")")

    def _on_model_changed(self) -> None:
        pass

    def _on_start_import(self) -> None:
        """
        Abstract slot. Has to be overridden to save the objects to the database
        :return: Nothing
        """
        pass

    def _on_selection_changed(self, selected_cols: List[str]) -> None:
        """
        process the selection change event and update the additional import columns
        :param selected_cols: selected columns to exclude
        :return: Nothing
        """

        self.logger.debug(self.__class__.__name__, "_on_selection_changed")

        if self._list_widget is None:
            self.logger.warn(self.__class__.__name__, "No list widget specified for additional columns")
            return

        cols = diff(self._selectable_columns, selected_cols)

        self.logger.debug(self.__class__.__name__, "selectable_columns: " + str(self._selectable_columns))
        self.logger.debug(self.__class__.__name__, "selected_cols: " + str(selected_cols))
        self.logger.debug(self.__class__.__name__, "additional cols: " + str(cols))

        self._list_widget.show()
        self._list_widget.setEnabled(True)
        self._list_widget.clear()
        self._list_widget.addItems(cols)


class PointImportController(ImportControllersInterface):
    """
    controller for the point data import
    """

    def __init__(self, view: PointImportView) -> None:
        """
        Initialize the PointImportController Object
        :param view: PointImportView
        """

        self.logger.debug(self.__class__.__name__, "__init__")

        super().__init__(view)
        self._list_widget = self._import_service.dockwidget.import_columns_points

    def _on_import_columns_changed(self) -> None:
        """
        change the import columns
        :return: Nothing
        """
        self.logger.debug(self.__class__.__name__, "_on_import_columns_changed")

        super()._on_import_columns_changed()
        try:
            self._view.set_combobox_data("easting", self._import_service.number_columns, 0)
            # noinspection SpellCheckingInspection
            self._view.set_combobox_data("northing", self._import_service.number_columns, 1)
            self._view.set_combobox_data("altitude", [''] + self._import_service.number_columns, 3)
            # noinspection SpellCheckingInspection
            self._view.set_combobox_data("strat", [''] + self._import_service.selectable_columns, 0)
            # noinspection SpellCheckingInspection
            self._view.set_combobox_data("strat_age", [''] + self._import_service.number_columns, 0)
            self._view.set_combobox_data("set_name", [''] + self._import_service.selectable_columns, 0)
            self._view.set_combobox_data("comment", [''] + self._import_service.selectable_columns, 0)

        except Exception as e:
            self.logger.error("Error", str(ExceptionHandling(e)))
            self._import_service.reset()

    def _on_start_import(self):
        """
        Save the Point Object(s) to the database
        :return: Nothing
        """

        if self._view.dockwidget.import_type.itemText(self._view.dockwidget.import_type.currentIndex()) != "Points":
            return

        data = self._import_service.read_import_file()

        onekey = data[next(iter(data.keys()))]["values"]
        # import json
        # self.logger.info(json.dumps(onekey, indent=2))
        count = len(onekey)

        east = self._view.combobox_data("easting")
        north = self._view.combobox_data("northing")
        alt = self._view.combobox_data("altitude")
        strat = self._view.combobox_data("strat")
        age = self._view.combobox_data("strat_age")
        set_name = self._view.combobox_data("set_name")
        comment = self._view.combobox_data("comment")

        service = DatabaseService.get_instance()
        service.close_session()
        service.connect()
        session = DatabaseService.get_instance().get_session()

        reference = self._import_service.get_crs()
        if reference is None:
            reference = ""
        else:
            reference = reference.toWkt()

        self.logger.debug("Saving with reference system\n{}".format(reference))

        for i in range(count):
            if (data[east]["values"][i] == "") and (data[north]["values"][i] == ""):
                continue

            e = float(data[east]["values"][i])
            n = float(data[north]["values"][i])
            h = None if alt == "" else float(data[alt]["values"][i])
            s = "" if strat == "" else data[strat]["values"][i]
            a = -1 if age == "" else float(data[age]["values"][i])
            sn = "" if set_name == "" else data[set_name]["values"][i]
            c = "" if comment == "" else data[comment]["values"][i]

            strat_obj = StratigraphicObject.init_stratigraphy(session, s, a)
            point = GeoPoint(strat_obj, False if (h is None) else True, reference,
                             e, n, 0 if (h is None) else h, session, sn, c)

            point.save_to_db()

        self.logger.info("Points successfully imported")


class LineImportController(ImportControllersInterface):
    """
    controller for the line data import
    """

    def __init__(self, view: LineImportView) -> None:
        """
        Initialize the LineImportController
        :param view: LineImportView
        """

        self.logger.debug(self.__class__.__name__, "__init__")

        super().__init__(view)
        self._list_widget = self._import_service.dockwidget.import_columns_lines

    def _on_import_columns_changed(self) -> None:
        """
        process the selected import_tests file and set possible values for column combo boxes
        :return: Nothing
        """

        self.logger.debug(self.__class__.__name__, "_on_import_columns_changed")

        super()._on_import_columns_changed()
        try:
            self._view.set_combobox_data("identifier", [''] + self._import_service.selectable_columns, 1)
            self._view.set_combobox_data("easting", self._import_service.number_columns, 0)
            # noinspection SpellCheckingInspection
            self._view.set_combobox_data("northing", self._import_service.number_columns, 1)
            self._view.set_combobox_data("altitude", [''] + self._import_service.number_columns, 3)
            # noinspection SpellCheckingInspection
            self._view.set_combobox_data("strat", [''] + self._import_service.selectable_columns, 0)
            # noinspection SpellCheckingInspection
            self._view.set_combobox_data("strat_age", [''] + self._import_service.number_columns, 0)
            self._view.set_combobox_data("set_name", [''] + self._import_service.selectable_columns, 0)
            self._view.set_combobox_data("comment", [''] + self._import_service.selectable_columns, 0)

        except Exception as e:
            self.logger.error("Error", str(ExceptionHandling(e)))
            self._view.reset_import()

    def _on_start_import(self):
        """
        Save the Point Object(s) to the database
        :return: Nothing
        """

        if self._view.dockwidget.import_type.itemText(self._view.dockwidget.import_type.currentIndex()) != "Lines":
            return

        data = self._import_service.read_import_file()

        onekey = data[next(iter(data.keys()))]["values"]
        # import json
        # self.logger.info(json.dumps(onekey, indent=2))
        count = len(onekey)

        identifier = self._view.combobox_data("identifier")
        east = self._view.combobox_data("easting")
        north = self._view.combobox_data("northing")
        alt = self._view.combobox_data("altitude")
        strat = self._view.combobox_data("strat")
        age = self._view.combobox_data("strat_age")
        set_name = self._view.combobox_data("set_name")
        comment = self._view.combobox_data("comment")

        service = DatabaseService.get_instance()
        service.close_session()
        service.connect()
        session = DatabaseService.get_instance().get_session()

        reference = self._import_service.get_crs()
        if reference is None:
            reference = ""
        else:
            reference = reference.toWkt()

        self.logger.debug("Saving with reference system\n{}".format(reference))

        lines = dict()

        line = 0

        for i in range(count):
            if identifier != "":
                line = data[identifier]["values"][i]
            elif (data[east]["values"][i] == "") and (data[north]["values"][i] == ""):
                line += 1
                continue

            e = float(data[east]["values"][i])
            n = float(data[north]["values"][i])
            h = None if alt == "" else float(data[alt]["values"][i])
            s = "" if strat == "" else data[strat]["values"][i]
            a = -1 if age == "" else float(data[age]["values"][i])
            sn = "" if set_name == "" else data[set_name]["values"][i]
            c = "" if comment == "" else data[comment]["values"][i]

            strat_obj = StratigraphicObject.init_stratigraphy(session, s, a)
            point = GeoPoint(None, False if (h is None) else True, reference,
                             e, n, 0 if (h is None) else h, session, sn, c)

            if line in lines:
                lines[line]["points"].append(point)
            else:
                lines[line] = {
                    "strat": strat_obj,
                    "points": [point]
                }

        for l in lines:
            line = lines[l]
            closed = False
            if (len(line["points"]) > 1) and (line["points"][0] == line["points"][-1]):
                closed = True
                line["points"].pop()

            new_line = Line(closed, line["strat"], line["points"], session, l, c)
            new_line.save_to_db()

        self.logger.info("Lines successfully imported")