# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeologicalDataProcessing
                                 A QGIS plugin
 This plugin connect the GeologicalToolbox Python module to QGIS.
                              -------------------
        begin                : 2018-01-24
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Stephan Donndorf
        email                : stephan@donndorf.info
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import platform
import sys
import traceback

# noinspection PyUnresolvedReferences
import os.path
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox
# noinspection PyUnresolvedReferences
from qgis.core import QgsMessageLog

# Import the code for the DockWidget
from .geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget
# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences
from .resources import *

debug = True


class GeologicalDataProcessing:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
                self.plugin_dir,
                'i18n',
                'GeologicalDataProcessing_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Geological Data Processing')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GeologicalDataProcessing')
        self.toolbar.setObjectName(u'GeologicalDataProcessing')

        self.pluginIsActive = False
        self.dockwidget = None

        # user defined class variables
        self.__import_widgets = dict()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeologicalDataProcessing', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        # noinspection PyUnresolvedReferences
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                    self.menu,
                    action)

        self.actions.append(action)

        return action

    # noinspection PyPep8Naming
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GeologicalDataProcessing/icon.png'
        self.add_action(
                icon_path,
                text=self.tr(u'Geological Data Processing'),
                callback=self.run,
                parent=self.iface.mainWindow())

    # --------------------------------------------------------------------------

    # noinspection PyPep8Naming
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # print "** CLOSING GeologicalDataProcessing"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashes
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        # print "** UNLOAD GeologicalDataProcessing"

        for action in self.actions:
            self.iface.removePluginMenu(
                    self.tr(u'&Geological Data Processing'),
                    action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # --------------------------------------------------------------------------

    def run(self) -> None:
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            # print "** STARTING GeologicalDataProcessing"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget is None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = GeologicalDataProcessingDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

            #
            # manual added content
            #

            # summarize import Widgets
            # noinspection SpellCheckingInspection
            self.__import_widgets = {
                "Points": {
                    "easting"  : self.dockwidget.easting_points,
                    "northing" : self.dockwidget.northing_points,
                    "altitude" : self.dockwidget.altitude_points,
                    "strat"    : self.dockwidget.strat_points,
                    "strat_age": self.dockwidget.strat_age_points,
                    "set_name" : self.dockwidget.set_name_points,
                    "comment"  : self.dockwidget.comment_points
                },
                "Lines" : {
                    "easting"  : self.dockwidget.easting_lines,
                    "northing" : self.dockwidget.northing_lines,
                    "altitude" : self.dockwidget.altitude_lines,
                    "strat"    : self.dockwidget.strat_lines,
                    "strat_age": self.dockwidget.strat_age_lines,
                    "set_name" : self.dockwidget.set_name_lines,
                    "comment"  : self.dockwidget.comment_lines
                }
            }

            # initialize the gui and connect signals and slots
            # 1 - General
            self.dockwidget.create_DB_button.clicked.connect(self.on_create_db_clicked)
            self.dockwidget.select_DB_button.clicked.connect(self.on_select_db)
            self.dockwidget.select_data_file_button.clicked.connect(self.on_select_data_file)
            # 2 - Import tab
            # 2.1 - Import points
            self.dockwidget.import_columns_points.hide()
            self.dockwidget.separator.addItems([';', ',', '<tabulator>', '.', '-', '_', '/', '\\'])
            self.dockwidget.separator.currentIndexChanged[str].connect(self.process_import)
            self.dockwidget.import_type.currentChanged.connect(self.on_import_item_changed_event)

    #
    # user defined functions
    # private functions
    #
    def __clear_import_combos(self) -> None:
        """
        Clear all import combo boxes
        :return: Nothing
        """
        for key in self.__import_widgets:
            for combo in self.__import_widgets[key]:
                self.__import_widgets[key][combo].clear()

    #
    # public functions
    #
    def process_import(self, separator: str) -> None:
        """
        process the selected import file and set possible values for column combo boxes
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
                                     "Maybe use a different separator or another import file")
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
            _, _, exc_traceback = sys.exc_info()
            text = "Error Message:\n{}\nTraceback:\n{}".format(str(e), ''.join(traceback.format_tb(exc_traceback)))
            # text = "Error Message:\nNone\nTraceback:\n{}".format(traceback.print_exc())
            self.iface.messageBar().pushMessage("Error",
                                                "An exception occurred during the process. " +
                                                "For more details, please take a look to the log windows.",
                                                level=2)
            # noinspection PyCallByClass, PyArgumentList
            QgsMessageLog.logMessage(text, level=2)

    #
    # slots
    #
    def on_create_db_clicked(self) -> None:
        """
        slot for creating a new database
        :return: Nothing
        """
        filename = QFileDialog.getSaveFileName(self.dockwidget, "Select database file", "",
                                               "Databases(*.db *.sqlite *.data);;Any File Type (*)")

        if filename != "":
            # noinspection PyTypeChecker
            if os.path.splitext(filename)[-1].lower().lstrip('.') not in ["db", "data", "sqlite"]:
                filename += ".data"
            self.dockwidget.database_file.setText(filename)

    def on_import_item_changed_event(self, _: int) -> None:
        """
        Calls the process_import function, if the active QToolBox Item changes in order to reset the combo boxes
        :param _: unused index, delivered by the currentChanged signal
        :return: nothing
        """
        self.process_import(self.dockwidget.separator.currentText())

    def on_select_data_file(self) -> None:
        """
        slot for selecting an import data file and processing the corresponding fields inside the import data tab.
        :return: Nothing
        """
        path = u"/Users/stephan/Documents/work/Dissertation/PythonModules/GeologicalToolbox/GeologicalToolbox/" + \
               u"tests/test_data/"
        if platform.system() == "Windows":
            # noinspection SpellCheckingInspection
            path = u"C:/Programmieren/GeologicalToolbox/GeologicalToolbox/tests/test_data"

        filename = QFileDialog.getOpenFileName(self.dockwidget, "Select data file", path,
                                               "Data Files(*.txt *.csv *.data);;Any File Type (*)")

        # noinspection PyCallByClass, PyArgumentList
        QgsMessageLog.logMessage("Import File: {}".format(filename), level=0)

        if filename != "":
            self.dockwidget.import_file.setText(filename)
            self.__clear_import_combos()

            import_file = self.dockwidget.import_file.text()
            try:
                import_file = open(import_file, 'r')
            except IOError:
                self.__clear_import_combos()
                return

            cols = import_file.readline().strip()
            props = import_file.readline().strip()
            data = import_file.readline().strip()
            import_file.close()

            if '' in [cols, props, data]:
                QMessageBox.critical(self.dockwidget, "Import File Error",
                                     "Cannot process import file, wrong file format!")
            else:
                self.dockwidget.import_file.setText(filename)

            for sep in [';', ',', '\t', '.', '-', '_', '/', '\\']:
                split = cols.split(sep)
                if len(split) < 3:
                    continue
                if sep == '\t':
                    index = self.dockwidget.separator.findText("<tabulator>", Qt.MatchFixedString)
                    if index >= 0:
                        self.dockwidget.separator.setCurrentIndex(index)
                        break
                index = self.dockwidget.separator.findText(sep, Qt.MatchFixedString)
                if index >= 0:
                    self.dockwidget.separator.setCurrentIndex(index)
                    break

    def on_select_db(self) -> None:
        """
        slot for selecting a sqlite database file and set the result to the related lineedit
        :return: Nothing
        """
        filename = QFileDialog.getOpenFileName(self.dockwidget, "Select database file", "",
                                               "Databases(*.db *.sqlite *.data);;Any File Type (*)")

        if filename != "":
            # noinspection PyTypeChecker
            if os.path.splitext(filename)[-1].lower().lstrip('.') not in ["db", "data", "sqlite"]:
                filename += ".data"
            self.dockwidget.database_file.setText(filename)
