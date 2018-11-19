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

import os.path
import unittest
from io import StringIO

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog

# Import the code for the DockWidget
from GeologicalDataProcessing.geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget
from GeologicalDataProcessing.miscellaneous.QGISDebugLog import QGISDebugLog
from GeologicalDataProcessing.services.ImportService import ImportService
# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences
from GeologicalDataProcessing.resources import *

# import MVC-Classes
from GeologicalDataProcessing.gui.controller.ImportController import PointImportController, LineImportController
from GeologicalDataProcessing.gui.models.ImportModels import PointImportModel, LineImportModel
from GeologicalDataProcessing.gui.views.ImportViews import PointImportView, LineImportView

# import tests
from GeologicalDataProcessing.tests.miscellaneouse.test_ExceptionHandling import TestExceptionHandlingClass
from GeologicalDataProcessing.tests.import_tests.test_point_import import TestPointImportClass

# miscellaneous
from GeologicalDataProcessing.config import debug
from GeologicalDataProcessing.miscellaneous.ExceptionHandling import ExceptionHandling
from GeologicalDataProcessing.miscellaneous.Helper import get_file_name


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
        self.__current_selected_tab = "Points"

        # save model, view and controller instances
        self.__controllers = dict()
        self.__models = dict()
        self.__views = dict()

        self.__import_service = None

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

            try:
                # initialize logger
                logger = QGISDebugLog()
                # logger.qgis_iface = self.iface
                logger.save_to_file = True

                self.__import_service = ImportService.get_instance()

                # initialize the gui and connect signals and slots
                self.dockwidget.import_type.currentChanged.connect(self.on_import_type_changed_event)

                # start tests button
                # -> only visible and active when the debug flag is True
                if debug:
                    self.dockwidget.start_tests_button.clicked.connect(self.on_start_tests)
                else:
                    self.dockwidget.start_tests_separator.setVisible(False)
                    self.dockwidget.start_tests_button.setVisible(False)

                self.__import_service.dockwidget = self.dockwidget
                self.__import_service.iface = self.iface

                self.__views['import_points'] = PointImportView(self.dockwidget)
                self.__views['import_lines'] = LineImportView(self.dockwidget)
                self.__controllers['import_points'] = PointImportController(self.__views['import_points'])
                self.__controllers['import_lines'] = LineImportController(self.__views['import_lines'])
            except Exception as e:
                ExceptionHandling(e).log()

    #
    # user defined functions
    # private functions
    #

    #
    # slots
    #
    def on_import_type_changed_event(self, index: int) -> None:
        """
        Calls the process_import function, if the active QToolBox Item changes in order to reset the combo boxes
        :param index: index of the newly selected tab, delivered by the currentChanged signal
        :return: nothing
        """
        pass
        # TODO: Hier muss das neu ausgewählte Tab aktualisiert werden!!!

    def on_start_tests(self) -> None:
        """
        start a test suite
        :return: Nothing
        """
        debug_log = QGISDebugLog()
        debug_log.qgis_iface = self.iface
        debug_log.save_to_file = True

        stream = StringIO()
        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner(stream=stream)
        suite = unittest.TestSuite()

        suite.addTests(loader.loadTestsFromTestCase(TestExceptionHandlingClass))

        test_cases = loader.getTestCaseNames(TestPointImportClass)
        for name in test_cases:
            suite.addTest(TestPointImportClass(name, iface=self.iface, dockwidget=self.dockwidget))

        # result = runner.run(unittest.makeSuite(TestExceptionHandlingClass))
        result = runner.run(suite)

        level = 0
        if len(result.errors) > 0 or len(result.failures) > 0:
            level = 2

        debug_log.push_message("logfile", debug_log.logfile)
        debug_log.push_message("Test runs", str(result.testsRun))
        debug_log.push_message("Test errors", str(len(result.errors)), level=level)
        debug_log.push_message("Failures", str(len(result.failures)), level=level)

        stream.seek(0)
        debug_log.push_message("Test output", '\n' + str(stream.read()), level=level)
