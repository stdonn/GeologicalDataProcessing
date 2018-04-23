# -*- coding: UTF-8 -*-
"""
Defines controller for the data import_tests
"""

from geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget
from gui.models.ImportModels import ImportModelInterface, PointImportModel
from miscellaneous.ExceptionHandling import ExceptionHandling

class ImportControllersInterface:
    """
    Basic interface for all import_tests controller
    """

    def __init__(self, model: ImportModelInterface = None, view: GeologicalDataProcessingDockWidget = None) -> None:
        """

        :param model: PointImportModel
        :param view:
        """
        self._model = model
        self._view = view

    def on_import_file_changed(self, filename:str) -> None:
        pass

    def on_model_changed(self) -> None:
        pass

    def on_start_import(self) -> None:
        pass


class PointImportController(ImportControllersInterface):
    def __init__(self, model:PointImportModel, view:GeologicalDataProcessingDockWidget) -> None:
        super().__init__(model, view)
        pass

    def on_import_file_changed(self, filename:str) -> None:
        """
                process the selected import_tests file and set possible values for column combo boxes
                :param separator: selected separator
                :return: Nothing
                """
        try:
            if debug:
                # noinspection PyCallByClass, PyArgumentList
                QgsMessageLog.logMessage("Selected separator: {}".format(separator), level=0)
            if separator == "<tabulator>":
                separator = '\t'

            self.__clear_import_combos()

            import_file_name = self.dockwidget.import_file.text()
            try:
                import_file = open(import_file_name, 'r')
            except IOError:
                # noinspection PyCallByClass, PyArgumentList
                QgsMessageLog.logMessage("Cannot open file: {}".format(import_file_name), level=0)
                return

            cols = import_file.readline().strip().split(separator)
            props = import_file.readline().strip().split(separator)
            data = import_file.readline().strip().split(separator)

            if debug:
                # noinspection PyCallByClass, PyArgumentList
                QgsMessageLog.logMessage("cols:\t{}".format(cols), level=0)
                # noinspection PyCallByClass, PyArgumentList
                QgsMessageLog.logMessage("props:\t{}".format(props), level=0)
                # noinspection PyCallByClass, PyArgumentList
                QgsMessageLog.logMessage("data:\t{}".format(data), level=0)

            import_file.close()

            nr_cols = []
            for col in data:
                try:
                    float(col)
                    nr_cols.append(data.index(col))
                except ValueError:
                    pass

            if len(nr_cols) < 3:
                QMessageBox.critical(self.dockwidget, "Not enough columns",
                                     "Cannot find enough columns. " +
                                     "Maybe use a different separator or another import_tests file")
                self.__clear_import_combos()
                return

            numbers = [cols[x] for x in nr_cols]

            current_item_index = self.dockwidget.import_type.currentIndex()
            current_item_name = self.dockwidget.import_type.itemText(current_item_index)

            if debug:
                # noinspection PyCallByClass, PyArgumentList
                QgsMessageLog.logMessage("current Item: {}[{}]".format(current_item_name, current_item_index), level=0)

            if current_item_name in ["Points", "Lines"]:
                self.__import_widgets[current_item_name]["easting"].addItems(numbers)
                self.__import_widgets[current_item_name]["easting"].setCurrentIndex(0)
                self.__import_widgets[current_item_name]["northing"].addItems(numbers)
                self.__import_widgets[current_item_name]["northing"].setCurrentIndex(1)
                self.__import_widgets[current_item_name]["altitude"].addItems([''] + numbers)
                self.__import_widgets[current_item_name]["altitude"].setCurrentIndex(0)
                # noinspection SpellCheckingInspection
                self.__import_widgets[current_item_name]["strat"].addItems([''] + cols)
                # noinspection SpellCheckingInspection
                self.__import_widgets[current_item_name]["strat_age"].addItems([''] + numbers)
                self.__import_widgets[current_item_name]["set_name"].addItems([''] + cols)
                self.__import_widgets[current_item_name]["comment"].addItems([''] + cols)
        except Exception as e:
            ExceptionHandling(e).push_last_to_qgis(self._view)
            
    def on_model_changed(self) -> None:
        pass

    def on_start_import(self) -> None:
        pass