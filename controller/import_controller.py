# -*- coding: UTF-8 -*-
"""
Defines controller for the data import_tests
ToDo: Add Property Type to Point and Line Import
"""
import json
from concurrent.futures import Future
from typing import Dict, List

from GeologicalDataProcessing.miscellaneous.exception_handler import ExceptionHandler
from GeologicalDataProcessing.miscellaneous.qgis_log_handler import QGISLogHandler
from GeologicalDataProcessing.models.log_model import PropertyImportData, LogImportData
from GeologicalDataProcessing.services.database_service import DatabaseService
from GeologicalDataProcessing.services.import_service import ImportService
from PyQt5.QtCore import pyqtSignal, QThread, QMutex
from geological_toolbox.db_handler import AbstractDBObject
from geological_toolbox.exceptions import WellMarkerDepthException, DatabaseRequestException
from geological_toolbox.geometries import GeoPoint, Line
from geological_toolbox.properties import Property
from geological_toolbox.stratigraphy import StratigraphicObject
from geological_toolbox.well_logs import WellLogValue, WellLog
from geological_toolbox.wells import WellMarker, Well


class ImportControllersInterface(QThread):
    """
    Basic interface for all import_tests controller
    """

    def __init__(self, data: Dict, selection: Dict, properties: List[PropertyImportData]) -> None:
        """
        :param data: import data parsed from the file to import
        :param selection: dictionary of selected columns
        """
        super().__init__()

        self._logger = QGISLogHandler(self.__class__.__name__)
        self._data: Dict = data
        self._selection: Dict = selection
        self._properties: List[PropertyImportData] = properties
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

    import_finished_with_warnings = pyqtSignal(str)
    """signal emitted, when the import process has finished with warnings"""

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
        self._logger.debug("import done")

        self._view.dockwidget.progress_bar_layout.setVisible(False)
        self._view.dockwidget.cancel_import.clicked.disconnect(self._stop_import)
        if (future is not None) and future.cancelled():
            self._logger.warn("future run finished, import cancelled!")
        elif future is not None:
            self._logger.info("future run finished, import successful")

        self._logger.info("QThread finished")
        if self.__thread is not None:
            self._logger.debug("waiting for the end...")
            self.__thread.wait()
            self._logger.debug("at the end...")
            self.__thread = None
            # self.__current_future = None


class PointImportController(ImportControllersInterface):
    """
    controller for the point data import
    """

    def __init__(self, data: Dict, selection: Dict, property_cols: List[PropertyImportData]) -> None:
        """
        :param data: import data parsed from the file to import
        :param selection: dictionary of selected columns
        """
        super().__init__(data, selection, property_cols)

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
            # self._logger.info(json.dumps(onekey, indent=2))
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

            self._logger.debug("Saving with reference system\n{}".format(reference))

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
                    self._logger.debug("point update")

                else:
                    point = GeoPoint(strat_obj, False if (h is None) else True, reference,
                                     e, n, 0 if (h is None) else h, session, sn, c)
                    self._logger.debug("new point")

                # add / update properties
                for item in self._properties:
                    self._logger.debug("Property: {}".format(item))
                    if point.has_property(item.name):
                        p = point.get_property(item.name)
                        p.property_unit = item.unit
                        p.value = self._data[item.name]["values"][i]
                        p.property_type = item.property_type
                    else:
                        p = Property(value=self._data[item.name]["values"][i], property_name=item.name,
                                     _type=item.property_type, property_unit=item.unit,
                                     session=session)
                        point.add_property(p)

                self._logger.debug("point: {}".format(point))
                point.save_to_db()

                if self._cancel:
                    self._logger.debug("Import canceled")
                    self.import_failed.emit(self._message)
                    break

            if not self._cancel:
                self.update_progress.emit(100)
                self._logger.debug("Points successfully imported")
                self.import_finished.emit()

        except Exception as e:
            msg = str(ExceptionHandler(e))
            self.import_failed.emit(msg)
            self._logger.error("Error", msg)

        finally:
            service.close_session()

        self._mutex.unlock()
        self.quit()


class LineImportController(ImportControllersInterface):
    """
    controller for the line data import
    """

    def __init__(self, data: Dict, selection: Dict, property_cols: List[PropertyImportData]) -> None:
        """
        :param data: import data parsed from the file to import
        :param selection: dictionary of selected columns
        """
        super().__init__(data, selection, property_cols)

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
            # self._logger.info(json.dumps(onekey, indent=2))
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

            self._logger.debug("Saving with reference system\n{}".format(reference))

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
                for item in self._properties:
                    self._logger.debug("Property: {}".format(item))
                    if point.has_property(item.name):
                        p = point.get_property(item.name)
                        p.property_unit = item.unit
                        p.value = self._data[item.name]["values"][i]
                        p.property_type = item.property_type
                    else:
                        p = Property(value=self._data[item.name]["values"][i], property_name=item.name,
                                     _type=item.property_type, property_unit=item.unit,
                                     session=session)
                        point.add_property(p)

                if _id is not None:
                    point.line_id = _id

                self._logger.debug("line point: {}".format(point))

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
                    self._logger.debug("Import canceled")
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

                            self._logger.debug("Updated existing line")

                    if line["id"] is None or new_line is None:  # new_line is None ? not in database -> create a new one
                        new_line = Line(closed, line["strat"], line["points"], session, line["name"], line["comment"])
                        self._logger.debug("Created new line")

                    new_line.save_to_db()
                    self._logger.debug("Line: {}".format(str(new_line)))

                    self.update_progress.emit(100 * i / maximum)

                    if self._cancel:
                        self._logger.debug("Import canceled")
                        self.import_failed.emit(self._message)
                        break

            if not self._cancel:
                self.update_progress.emit(100)
                self._logger.debug("Lines successfully imported")
                self.import_finished.emit()

        except Exception as e:
            msg = str(ExceptionHandler(e))
            self.import_failed.emit(msg)
            self._logger.error("Error", msg)

        finally:
            service.close_session()

        self._mutex.unlock()
        self.quit()


class WellImportController(ImportControllersInterface):
    """
    controller for well data import
    """

    def __init__(self, data: Dict, selection: Dict, property_cols: List[PropertyImportData]) -> None:
        """
        :param data: import data parsed from the file to import
        :param selection: dictionary of selected columns
        """
        super().__init__(data, selection, property_cols)

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

            self._logger.debug("Saving with reference system\n{}".format(reference))

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
                    self._logger.debug("Import canceled")
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
                            self._logger.debug("Updating existing well: {}".format(new_well))
                            for marker in new_well.marker:
                                WellMarker.delete_from_db(marker, session)

                            new_well.save_to_db()
                            new_well.marker = well["marker"]
                            new_well.short_name = well["short_name"]
                            new_well.easting = well["easting"]
                            new_well.northing = well["northing"]
                            new_well.depth = well["total_depth"]
                        except WellMarkerDepthException as e:
                            self._logger.error("WellMarkerDepthException", "{}\n{}".format(new_well, str(e)))
                            return False
                    else:
                        self._logger.debug("Creating new well with name [{}]".format(well_name))
                        new_well = Well(well_name, well["short_name"], well["total_depth"], reference_system=reference,
                                        easting=well["easting"], northing=well["northing"], altitude=well["altitude"],
                                        session=session)

                        new_well.marker = well["marker"]

                    new_well.save_to_db()

                    self._logger.debug("Saved well:\n{}".format(new_well))

                    self.update_progress.emit(100 * i / maximum)

                    if self._cancel:
                        self._logger.debug("Import canceled")
                        self.import_failed.emit(self._message)
                        break

            if not self._cancel:
                self.update_progress.emit(100)
                self._logger.debug("Lines successfully imported")
                self.import_finished.emit()

        except Exception as e:
            msg = str(ExceptionHandler(e))
            self.import_failed.emit(msg)
            self._logger.error("Error", msg)

        finally:
            service.close_session()

        self._mutex.unlock()
        self.quit()


class PropertyImportController(ImportControllersInterface):
    """
    controller for the additional property import
    """

    def __init__(self, data: Dict, selection: Dict, property_cols: List[PropertyImportData]) -> None:
        """
        :param data: import data parsed from the file to import
        :param selection: dictionary of selected columns
        """
        super().__init__(data, selection, property_cols)

    def run(self):
        """
        Save the Properties to the database
        :return: Nothing, emits Qt Signals
        """

        self._mutex.lock()
        service = DatabaseService.get_instance()
        service.close_session()
        service.connect()
        session = service.get_session()

        failed_imports = 0
        try:
            onekey = self._data[next(iter(self._data.keys()))]["values"]
            # import json
            # self._logger.info(json.dumps(onekey, indent=2))
            count = len(onekey)

            id_col = self._selection["id"]

            reference = ImportService.get_instance().get_crs()
            if reference is None:
                reference = ""
            else:
                reference = reference.toWkt()

            self._logger.debug("Saving with reference system\n{}".format(reference))

            for i in range(count):
                self.update_progress.emit(100 * i / count)

                try:
                    _id = int(self._data[id_col]["values"][i])
                except ValueError:
                    self._logger.warn("No id specified for current data set at line {}".format(i), only_logfile=True)
                    failed_imports += 1
                    continue

                if (_id is None) or (_id < 0):
                    self._logger.warn("Unknown Geopoint ID found: [{}]".format(_id))
                    failed_imports += 1
                    continue

                try:
                    point = GeoPoint.load_by_id_from_db(_id, session)
                    if point is None:
                        self._logger.warn("No Geopoint with ID [{}] found".format(_id))
                        failed_imports += 1
                        continue

                    point.reference_system = reference

                    # add / update properties
                    for item in self._properties:
                        self._logger.debug("Property: {}".format(item))
                        if point.has_property(item.name):
                            p = point.get_property(item.name)
                            p.property_unit = item.unit
                            p.value = self._data[item.name]["values"][i]
                            p.property_type = item.property_type
                        else:
                            p = Property(value=self._data[item.name]["values"][i], property_name=item.name,
                                         _type=item.property_type, property_unit=item.unit,
                                         session=session)
                            point.add_property(p)

                    self._logger.debug("point: {}".format(point))
                    point.save_to_db()

                except DatabaseRequestException:
                    self._logger.warn("Cannot find Geopoint with ID [{}]. Skipping property import".format(_id))
                    failed_imports += 1

                if self._cancel:
                    self._logger.debug("Import canceled")
                    self.import_failed.emit(self._message)
                    break

            if not self._cancel:
                if failed_imports > 0:
                    self.import_finished_with_warnings.emit("Could not import {} properties.".format(failed_imports))
                self.update_progress.emit(100)
                self.import_finished.emit()

        except Exception as e:
            msg = str(ExceptionHandler(e))
            self.import_failed.emit(msg)
            self._logger.error("Error", msg, to_messagebar=True)

        finally:
            service.close_session()

        self._mutex.unlock()
        self.quit()


class WellLogImportController(ImportControllersInterface):
    """
    controller for well log data import
    """

    def __init__(self, data: Dict, selection: Dict, log_cols: List[LogImportData]) -> None:
        """
        :param data: import data parsed from the file to import
        :param selection: dictionary of selected columns
        """
        super().__init__(data, selection, log_cols)

    def run(self):
        """
        Save well logs to the database
        :return: Nothing, emits Qt Signals
        """

        self._mutex.lock()
        service = DatabaseService.get_instance()
        service.close_session()
        service.connect()
        session = service.get_session()

        failed_imports = 0
        try:
            onekey = self._data[next(iter(self._data.keys()))]["values"]
            # import json
            # self._logger.info(json.dumps(onekey, indent=2))
            count = len(onekey)

            well_name_col = self._selection["well_name"]
            depth_col = self._selection["depth"]

            reference = ImportService.get_instance().get_crs()
            if reference is None:
                reference = ""
            else:
                reference = reference.toWkt()

            self._logger.debug("Saving with reference system\n{}".format(reference))

            for i in range(count):
                self.update_progress.emit(100 * i / count)

                try:
                    well_name = self._data[well_name_col]["values"][i]
                except ValueError:
                    self._logger.warn("No well_name specified for current data set at line {}".format(i))
                    failed_imports += 1
                    continue

                if (well_name is None) or (well_name == ""):
                    self._logger.warn("Unknown well name found: [{}]".format(well_name))
                    failed_imports += 1
                    continue

                try:
                    well: Well = Well.load_by_wellname_from_db(well_name, session)
                    if well is None:
                        self._logger.warn("No well with name [{}] found...".format(well_name))
                        failed_imports += 1
                        continue

                    well.reference_system = reference

                    # add / update properties
                    for item in self._properties:
                        self._logger.debug("Property: {}".format(item))
                        if well.has_log(item.name):
                            log = well.get_log(item.name)
                        else:
                            log = WellLog(property_name = item.name, property_unit = item.unit, session=session)
                            well.add_log(log)

                        depth = self._data[depth_col]["values"][i]
                        value = self._data[item.name]["values"][i]
                        try:
                            log_value: WellLogValue = log.get_value_by_depth(depth)
                        except ValueError:
                            log_value = WellLogValue(depth, value, session=session)

                        log_value.value = value
                        log.insert_log_value(log_value)

                    self._logger.debug("well: {}".format(well))
                    well.save_to_db()

                except DatabaseRequestException:
                    self._logger.warn("Cannot find well with name [{}]. Skipping log import".format(well_name))
                    failed_imports += 1

                if self._cancel:
                    self._logger.debug("Import canceled")
                    self.import_failed.emit(self._message)
                    break

            if not self._cancel:
                if failed_imports > 0:
                    self.import_finished_with_warnings.emit("Could not import {} properties.".format(failed_imports))
                self.update_progress.emit(100)
                self.import_finished.emit()

        except Exception as e:
            msg = str(ExceptionHandler(e))
            self.import_failed.emit(msg)
            self._logger.error("Error", msg, to_messagebar=True)

        finally:
            service.close_session()

        self._mutex.unlock()
        self.quit()
