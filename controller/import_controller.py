# -*- coding: UTF-8 -*-
"""
Defines controller for the data import_tests
ToDo: Add Property Type to Point and Line Import
"""

from concurrent.futures import Future

from PyQt5.QtCore import pyqtSignal, QThread, QMutex
from geological_toolbox.exceptions import WellMarkerDepthException
from geological_toolbox.geometries import GeoPoint, Line
from geological_toolbox.properties import Property, PropertyTypes
from geological_toolbox.stratigraphy import StratigraphicObject
from geological_toolbox.wells import WellMarker, Well
from typing import Dict, List

from geological_toolbox.db_handler import AbstractDBObject
from GeologicalDataProcessing.miscellaneous.qgis_log_handler import QGISLogHandler
from GeologicalDataProcessing.services.database_service import DatabaseService
from GeologicalDataProcessing.services.import_service import ImportService

# miscellaneous
from GeologicalDataProcessing.miscellaneous.exception_handler import ExceptionHandler


class ImportControllersInterface(QThread):
    """
    Basic interface for all import_tests controller
    """

    def __init__(self, data: Dict, selection: Dict, property_cols: List[str]) -> None:
        """
        :param data: import data parsed from the file to import
        :param selection: dictionary of selected columns
        """
        super().__init__()

        self._logger = QGISLogHandler(ImportControllersInterface.__name__)
        self._data: Dict = data
        self._selection: Dict = selection
        self._property_cols: List[str] = property_cols
        self._mutex = QMutex()
        self._cancel = False
        self._message = ""

    def run(self) -> None:
        """
        Thread execution function to import data
        :return: Nothing
        """
        pass

    #
    # signals
    #

    update_progress = pyqtSignal(int)
    """update progress bar signal. Committed value has to be between 0 and 100"""

    import_finished = pyqtSignal()
    """signal emitted, when the import process has finished"""

    import_failed = pyqtSignal(str)
    """signal emitted, when the import process was canceled or failed through a call of the cancel_import slot"""

    #
    # slots
    #

    def cancel_import(self, msg: str = "") -> None:
        """
        slot for canceling the import process. A trigger variable will hint the importer to stop at the next
        possibility. This should ensure the finalization of all started write processes and therefore the integrity of
        all database objects.

        The :func:`~GeologicalDataProcessing.controller.import_controller.ImportControllersInterface.import_cancelled`
        signal will be sent, if the import process was successfully cancelled.
        :return: Nothing
        """
        self._cancel = True
        if msg == "":
            self._message = "Import canceled"
        else:
            self._message = msg

    def _import_done(self, future: Future = None) -> None:
        """
        function called, when import is done or canceled
        :param future: import executing future object
        :return: nothing
        """
        self.logger.debug("import done")

        self._view.dockwidget.progress_bar_layout.setVisible(False)
        self._view.dockwidget.cancel_import.clicked.disconnect(self._stop_import)
        if (future is not None) and future.cancelled():
            self.logger.warn("future run finished, import cancelled!")
        elif future is not None:
            self.logger.info("future run finished, import successful")

        self.logger.info("QThread finished")
        if self.__thread is not None:
            self.logger.debug("waiting for the end...")
            self.__thread.wait()
            self.logger.debug("at the end...")
            self.__thread = None
            # self.__current_future = None


class PointImportController(ImportControllersInterface):
    """
    controller for the point data import
    """

    def __init__(self, data: Dict, selection: Dict, property_cols: List[str]) -> None:
        """
        :param data: import data parsed from the file to import
        :param selection: dictionary of selected columns
        """
        super().__init__(data, selection, property_cols)
        self.logger = QGISLogHandler(PointImportController.__name__)

    def run(self):
        """
        Save the Point Object(s) to the database
        :return: True if function executed successfully, else False
        """

        self._mutex.lock()
        service = DatabaseService.get_instance()
        service.close_session()
        service.connect()
        session = service.get_session()

        try:
            onekey = self._data[next(iter(self._data.keys()))]["values"]
            # import json
            # self.logger.info(json.dumps(onekey, indent=2))
            count = len(onekey)

            east = self._selection["easting"]
            north = self._selection["northing"]
            alt = self._selection["altitude"]
            strat = self._selection["strat"]
            age = self._selection["strat_age"]
            set_name = self._selection["set_name"]
            comment = self._selection["comment"]

            reference = ImportService.get_instance().get_crs()
            if reference is None:
                reference = ""
            else:
                reference = reference.toWkt()

            self.logger.debug("Saving with reference system\n{}".format(reference))

            for i in range(count):
                self.update_progress.emit(100 * i / count)

                if (self._data[east]["values"][i] == "") and (self._data[north]["values"][i] == ""):
                    continue

                _id = None
                if "gpt_id" in self._data:
                    try:
                        _id = int(self._data["gpt_id"]["values"][i])
                    except ValueError:
                        pass

                e = float(self._data[east]["values"][i])
                n = float(self._data[north]["values"][i])
                h = None if alt == "" else float(self._data[alt]["values"][i])
                s = "" if strat == "" else self._data[strat]["values"][i]
                a = -1 if age == "" else float(self._data[age]["values"][i])
                sn = "" if set_name == "" else self._data[set_name]["values"][i]
                c = "" if comment == "" else self._data[comment]["values"][i]

                strat_obj = StratigraphicObject.init_stratigraphy(session, s, a)

                if (_id is not None) and (_id > -1):
                    point = GeoPoint.load_by_id_from_db(_id, session)
                    point.easting = e
                    point.northing = n
                    point.altitude = h
                    point.del_z() if h is None else point.use_z()
                    point.reference_system = reference
                    point.horizon = strat_obj
                    point.name = sn
                    point.comment = c
                    self.logger.debug("point update")

                else:
                    point = GeoPoint(strat_obj, False if (h is None) else True, reference,
                                     e, n, 0 if (h is None) else h, session, sn, c)
                    self.logger.debug("new point")

                # add / update properties
                for item in self._property_cols:
                    self.logger.debug("Property: {}".format(item))
                    if point.has_property(item):
                        p = point.get_property(item)
                        p.property_unit = self._data[item]["property"]
                        p.value = self._data[item]["values"][i]
                    else:
                        p = Property(value=self._data[item]["values"][i], property_name=item,
                                     _type=PropertyTypes.STRING, property_unit=self._data[item]["property"],
                                     session=session)
                        point.add_property(p)

                self.logger.debug("point: {}".format(point))
                point.save_to_db()

                if self._cancel:
                    self.logger.debug("Import canceled")
                    self.import_failed.emit(self._message)
                    break

            if not self._cancel:
                self.update_progress.emit(100)
                self.logger.debug("Points successfully imported")
                self.import_finished.emit()

        except Exception as e:
            msg = str(ExceptionHandler(e))
            self.import_failed.emit(msg)
            self.logger.error("Error", msg)

        finally:
            service.close_session()

        self._mutex.unlock()
        self.quit()


class LineImportController(ImportControllersInterface):
    """
    controller for the line data import
    """

    def __init__(self, data: Dict, selection: Dict, property_cols: List[str]) -> None:
        """
        :param data: import data parsed from the file to import
        :param selection: dictionary of selected columns
        """
        super().__init__(data, selection, property_cols)
        self.logger = QGISLogHandler(LineImportController.__name__)

    def run(self):
        """
        Save the Point Object(s) to the database
        :return: True if function executed successfully, else False
        """
        self._mutex.lock()
        service = DatabaseService.get_instance()
        service.close_session()
        service.connect()
        session = DatabaseService.get_instance().get_session()

        try:
            onekey = self._data[next(iter(self._data.keys()))]["values"]
            # import json
            # self.logger.info(json.dumps(onekey, indent=2))
            count = len(onekey)

            east = self._selection["easting"]
            north = self._selection["northing"]
            alt = self._selection["altitude"]
            strat = self._selection["strat"]
            age = self._selection["strat_age"]
            set_name = self._selection["set_name"]
            comment = self._selection["comment"]

            reference = ImportService.get_instance().get_crs()
            if reference is None:
                reference = ""
            else:
                reference = reference.toWkt()

            self.logger.debug("Saving with reference system\n{}".format(reference))

            lines = dict()

            line = 0

            maximum = count
            for i in range(count):
                _id = None
                if "gln_id" in self._data:
                    try:
                        _id = int(self._data["gln_id"]["values"][i])
                    except ValueError:
                        pass

                if (self._data[east]["values"][i] == "") and (self._data[north]["values"][i] == ""):
                    line += 1
                    continue

                e = float(self._data[east]["values"][i])
                n = float(self._data[north]["values"][i])
                h = None if alt == "" else float(self._data[alt]["values"][i])
                s = "" if strat == "" else self._data[strat]["values"][i]
                a = -1 if age == "" else float(self._data[age]["values"][i])
                sn = "" if set_name == "" else self._data[set_name]["values"][i]
                c = "" if comment == "" else self._data[comment]["values"][i]

                strat_obj = StratigraphicObject.init_stratigraphy(session, s, a)
                point = GeoPoint(None, False if (h is None) else True, reference,
                                 e, n, 0 if (h is None) else h, session, sn, c)

                # add / update properties
                for item in self._property_cols:
                    if point.has_property(item):
                        p = point.get_property(item)
                        p.property_unit = self._data[item]["property"]
                        p.value = self._data[item]["values"][i]
                    else:
                        p = Property(value=self._data[item]["values"][i], property_name=item,
                                     _type=PropertyTypes.STRING, property_unit=self._data[item]["property"],
                                     session=session)
                        point.add_property(p)
                    self.logger.debug("Property: {}".format(item))

                if _id is not None:
                    point.line_id = _id

                self.logger.debug("line point: {}".format(point))

                if line in lines:
                    lines[line]["points"].append(point)
                else:
                    lines[line] = {
                        "id": _id,
                        "strat": strat_obj,
                        "points": [point],
                        "name": sn,
                        "comment": c
                    }
                    maximum += 1

                i += 1
                self.update_progress.emit(100 * i / maximum)

                if self._cancel:
                    self.logger.debug("Import canceled")
                    self.import_failed.emit(self._message)
                    break

            i = count
            if not self._cancel:
                for l in lines:
                    i += 1

                    line = lines[l]
                    closed = False
                    if (len(line["points"]) > 1) and (line["points"][0] == line["points"][-1]):
                        closed = True
                        line["points"].pop()

                    new_line = None
                    if line["id"] is not None:
                        new_line = Line.load_by_id_from_db(line["id"], session)
                        if new_line is not None:
                            for point in new_line.points:
                                AbstractDBObject.delete_from_db(point, session)
                                del point

                            new_line.closed = closed
                            new_line.points = line["points"]
                            new_line.horizon = line["strat"]
                            new_line.name = line["name"]
                            new_line.comment = line["comment"]

                            self.logger.debug("Updated existing line")

                    if line["id"] is None or new_line is None:  # new_line is None ? not in database -> create a new one
                        new_line = Line(closed, line["strat"], line["points"], session, line["name"], line["comment"])
                        self.logger.debug("Created new line")

                    new_line.save_to_db()
                    self.logger.debug("Line: {}".format(str(new_line)))

                    self.update_progress.emit(100 * i / maximum)

                    if self._cancel:
                        self.logger.debug("Import canceled")
                        self.import_failed.emit(self._message)
                        break

            if not self._cancel:
                self.update_progress.emit(100)
                self.logger.debug("Lines successfully imported")
                self.import_finished.emit()

        except Exception as e:
            msg = str(ExceptionHandler(e))
            self.import_failed.emit(msg)
            self.logger.error("Error", msg)

        finally:
            service.close_session()

        self._mutex.unlock()
        self.quit()


class WellImportController(ImportControllersInterface):
    """
    controller for well data import
    """

    def __init__(self, data: Dict, selection: Dict, property_cols: List[str]) -> None:
        """
        :param data: import data parsed from the file to import
        :param selection: dictionary of selected columns
        """
        super().__init__(data, selection, property_cols)
        self.logger = QGISLogHandler(WellImportController.__name__)

    def run(self) -> bool:
        """
        Save the Well Object(s) to the database
        :return: True if function executed successfully, else False
        """

        self._mutex.lock()
        service = DatabaseService.get_instance()
        service.close_session()
        service.connect()
        session = DatabaseService.get_instance().get_session()

        try:
            onekey = self._data[next(iter(self._data.keys()))]["values"]
            count = len(onekey)

            name = self._selection["name"]
            short_name = self._selection["short_name"]
            east = self._selection["easting"]
            north = self._selection["northing"]
            alt = self._selection["altitude"]
            total_depth = self._selection["total_depth"]
            strat = self._selection["strat"]
            depth_to = self._selection["depth_to"]
            comment = self._selection["comment"]

            reference = ImportService.get_instance().get_crs()
            if reference is None:
                reference = ""
            else:
                reference = reference.toWkt()

            self.logger.debug("Saving with reference system\n{}".format(reference))

            wells = dict()

            maximum = count
            for i in range(count):
                if (self._data[east]["values"][i] == "") and (self._data[north]["values"][i] == ""):
                    continue

                na = self._data[name]["values"][i]
                sn = "" if short_name == "" else self._data[short_name]["values"][i]
                e = float(self._data[east]["values"][i])
                n = float(self._data[north]["values"][i])
                kb = None if alt == "" else float(self._data[alt]["values"][i])
                td = -1 if total_depth == "" else float(self._data[total_depth]["values"][i])
                s = "" if strat == "" else self._data[strat]["values"][i]
                dt = -1 if depth_to == "" else float(self._data[depth_to]["values"][i])
                c = "" if comment == "" else self._data[comment]["values"][i]

                strat_obj = StratigraphicObject.init_stratigraphy(session, s, -1)
                strat_obj.save_to_db()

                marker = WellMarker(dt, strat_obj, session=session, comment=c)
                # marker.save_to_db()
                # point = GeoPoint(None, False if (h is None) else True, reference,
                #                e, n, 0 if (h is None) else h, session, sn, c)

                if na in wells:
                    wells[na]["marker"].append(marker)
                else:
                    wells[na] = {
                        "short_name": sn,
                        "easting": e,
                        "northing": n,
                        "altitude": kb,
                        "total_depth": td,
                        "marker": [marker]
                    }

                    maximum += 1

                if self._cancel:
                    self.logger.debug("Import canceled")
                    self.import_failed.emit(self._message)
                    break

                self.update_progress.emit(100 * i / maximum)

            i = count
            if not self._cancel:
                for well_name in wells:
                    i += 1
                    well = wells[well_name]

                    new_well = Well.load_by_wellname_from_db(well_name, session)
                    if new_well is not None:
                        try:
                            self.logger.debug("Updating existing well: {}".format(new_well))
                            for marker in new_well.marker:
                                WellMarker.delete_from_db(marker, session)

                            new_well.save_to_db()
                            new_well.marker = well["marker"]
                            new_well.short_name = well["short_name"]
                            new_well.easting = well["easting"]
                            new_well.northing = well["northing"]
                            new_well.depth = well["total_depth"]
                        except WellMarkerDepthException as e:
                            self.logger.error("WellMarkerDepthException", "{}\n{}".format(new_well, str(e)))
                            return False
                    else:
                        self.logger.debug("Creating new well with name [{}]".format(well_name))
                        new_well = Well(well_name, well["short_name"], well["total_depth"], reference_system=reference,
                                        easting=well["easting"], northing=well["northing"], altitude=well["altitude"],
                                        session=session)

                        new_well.marker = well["marker"]

                    new_well.save_to_db()

                    self.logger.debug("Saved well:\n{}".format(new_well))

                    self.update_progress.emit(100 * i / maximum)

                    if self._cancel:
                        self.logger.debug("Import canceled")
                        self.import_failed.emit(self._message)
                        break

            if not self._cancel:
                self.update_progress.emit(100)
                self.logger.debug("Lines successfully imported")
                self.import_finished.emit()

        except Exception as e:
            msg = str(ExceptionHandler(e))
            self.import_failed.emit(msg)
            self.logger.error("Error", msg)

        finally:
            service.close_session()

        self._mutex.unlock()
        self.quit()