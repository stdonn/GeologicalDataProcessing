# -*- coding: UTF-8 -*-
"""
Defines controller for the data import_tests
"""

from PyQt5.QtWidgets import QListWidget
from typing import List

from GeologicalDataProcessing.gui.views.ImportViews import ImportViewInterface, PointImportView, LineImportView
from GeologicalDataProcessing.miscellaneous.ExceptionHandling import ExceptionHandling
from GeologicalDataProcessing.miscellaneous.QGISDebugLog import QGISDebugLog
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

        self._list_widget: QListWidget = None
        self._selectable_columns = []
        self._number_columns = []
        self._working_dir = []

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
