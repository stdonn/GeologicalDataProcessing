# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\geological_data_processing_dockwidget_base.ui'
#
# Created: Mon Jan 29 19:23:14 2018
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_GeologicalDataProcessingDockWidgetBase(object):
    def setupUi(self, GeologicalDataProcessingDockWidgetBase):
        GeologicalDataProcessingDockWidgetBase.setObjectName(_fromUtf8("GeologicalDataProcessingDockWidgetBase"))
        GeologicalDataProcessingDockWidgetBase.resize(420, 796)
        GeologicalDataProcessingDockWidgetBase.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.database_file = QtGui.QLineEdit(self.dockWidgetContents)
        self.database_file.setObjectName(_fromUtf8("database_file"))
        self.horizontalLayout_3.addWidget(self.database_file)
        self.select_DB = QtGui.QPushButton(self.dockWidgetContents)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/ic_storage_48px.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.select_DB.setIcon(icon)
        self.select_DB.setObjectName(_fromUtf8("select_DB"))
        self.horizontalLayout_3.addWidget(self.select_DB)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tabwidget = QtGui.QTabWidget(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabwidget.sizePolicy().hasHeightForWidth())
        self.tabwidget.setSizePolicy(sizePolicy)
        self.tabwidget.setMinimumSize(QtCore.QSize(400, 100))
        self.tabwidget.setObjectName(_fromUtf8("tabwidget"))
        self.import_data = QtGui.QWidget()
        self.import_data.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.import_data.setAutoFillBackground(True)
        self.import_data.setObjectName(_fromUtf8("import_data"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.import_data)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.import_file = QtGui.QLineEdit(self.import_data)
        self.import_file.setObjectName(_fromUtf8("import_file"))
        self.horizontalLayout_2.addWidget(self.import_file)
        self.import_file_button = QtGui.QPushButton(self.import_data)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/ic_perm_media_48px.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.import_file_button.setIcon(icon1)
        self.import_file_button.setObjectName(_fromUtf8("import_file_button"))
        self.horizontalLayout_2.addWidget(self.import_file_button)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.working_dir = QtGui.QLineEdit(self.import_data)
        self.working_dir.setObjectName(_fromUtf8("working_dir"))
        self.horizontalLayout_4.addWidget(self.working_dir)
        self.working_dir_button = QtGui.QPushButton(self.import_data)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/ic_folder_open_48px.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.working_dir_button.setIcon(icon2)
        self.working_dir_button.setObjectName(_fromUtf8("working_dir_button"))
        self.horizontalLayout_4.addWidget(self.working_dir_button)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_14 = QtGui.QHBoxLayout()
        self.horizontalLayout_14.setObjectName(_fromUtf8("horizontalLayout_14"))
        self.label_12 = QtGui.QLabel(self.import_data)
        self.label_12.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_14.addWidget(self.label_12)
        self.mQgsProjectionSelectionWidget = QgsProjectionSelectionWidget(self.import_data)
        self.mQgsProjectionSelectionWidget.setObjectName(_fromUtf8("mQgsProjectionSelectionWidget"))
        self.horizontalLayout_14.addWidget(self.mQgsProjectionSelectionWidget)
        self.verticalLayout_3.addLayout(self.horizontalLayout_14)
        self.toolBox = QtGui.QToolBox(self.import_data)
        self.toolBox.setObjectName(_fromUtf8("toolBox"))
        self.point_tab = QtGui.QWidget()
        self.point_tab.setGeometry(QtCore.QRect(0, 0, 374, 381))
        self.point_tab.setObjectName(_fromUtf8("point_tab"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.point_tab)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_9 = QtGui.QLabel(self.point_tab)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.verticalLayout_4.addWidget(self.label_9)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.label_2 = QtGui.QLabel(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(100, 0))
        self.label_2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_5.addWidget(self.label_2)
        self.easting_points = QtGui.QComboBox(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.easting_points.sizePolicy().hasHeightForWidth())
        self.easting_points.setSizePolicy(sizePolicy)
        self.easting_points.setObjectName(_fromUtf8("easting_points"))
        self.horizontalLayout_5.addWidget(self.easting_points)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label_3 = QtGui.QLabel(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QtCore.QSize(100, 0))
        self.label_3.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_6.addWidget(self.label_3)
        self.northing_points = QtGui.QComboBox(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.northing_points.sizePolicy().hasHeightForWidth())
        self.northing_points.setSizePolicy(sizePolicy)
        self.northing_points.setObjectName(_fromUtf8("northing_points"))
        self.horizontalLayout_6.addWidget(self.northing_points)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.label_4 = QtGui.QLabel(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMinimumSize(QtCore.QSize(100, 0))
        self.label_4.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_7.addWidget(self.label_4)
        self.altitude_points = QtGui.QComboBox(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.altitude_points.sizePolicy().hasHeightForWidth())
        self.altitude_points.setSizePolicy(sizePolicy)
        self.altitude_points.setObjectName(_fromUtf8("altitude_points"))
        self.horizontalLayout_7.addWidget(self.altitude_points)
        self.verticalLayout_4.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.label_5 = QtGui.QLabel(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QtCore.QSize(100, 0))
        self.label_5.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_8.addWidget(self.label_5)
        self.strat_points = QtGui.QComboBox(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.strat_points.sizePolicy().hasHeightForWidth())
        self.strat_points.setSizePolicy(sizePolicy)
        self.strat_points.setObjectName(_fromUtf8("strat_points"))
        self.horizontalLayout_8.addWidget(self.strat_points)
        self.verticalLayout_4.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.label_6 = QtGui.QLabel(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QtCore.QSize(100, 0))
        self.label_6.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_9.addWidget(self.label_6)
        self.strat_age_points = QtGui.QComboBox(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.strat_age_points.sizePolicy().hasHeightForWidth())
        self.strat_age_points.setSizePolicy(sizePolicy)
        self.strat_age_points.setObjectName(_fromUtf8("strat_age_points"))
        self.horizontalLayout_9.addWidget(self.strat_age_points)
        self.verticalLayout_4.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtGui.QHBoxLayout()
        self.horizontalLayout_10.setObjectName(_fromUtf8("horizontalLayout_10"))
        self.label_7 = QtGui.QLabel(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setMinimumSize(QtCore.QSize(100, 0))
        self.label_7.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_10.addWidget(self.label_7)
        self.point_set_name = QtGui.QComboBox(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.point_set_name.sizePolicy().hasHeightForWidth())
        self.point_set_name.setSizePolicy(sizePolicy)
        self.point_set_name.setObjectName(_fromUtf8("point_set_name"))
        self.horizontalLayout_10.addWidget(self.point_set_name)
        self.verticalLayout_4.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.label_8 = QtGui.QLabel(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setMinimumSize(QtCore.QSize(100, 0))
        self.label_8.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_11.addWidget(self.label_8)
        self.comment_points = QtGui.QComboBox(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comment_points.sizePolicy().hasHeightForWidth())
        self.comment_points.setSizePolicy(sizePolicy)
        self.comment_points.setObjectName(_fromUtf8("comment_points"))
        self.horizontalLayout_11.addWidget(self.comment_points)
        self.verticalLayout_4.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        self.label_11 = QtGui.QLabel(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)
        self.label_11.setMinimumSize(QtCore.QSize(100, 0))
        self.label_11.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.horizontalLayout_13.addWidget(self.label_11)
        self.separator_points = QtGui.QComboBox(self.point_tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.separator_points.sizePolicy().hasHeightForWidth())
        self.separator_points.setSizePolicy(sizePolicy)
        self.separator_points.setObjectName(_fromUtf8("separator_points"))
        self.horizontalLayout_13.addWidget(self.separator_points)
        self.multiple_separators_points = QtGui.QCheckBox(self.point_tab)
        self.multiple_separators_points.setObjectName(_fromUtf8("multiple_separators_points"))
        self.horizontalLayout_13.addWidget(self.multiple_separators_points)
        self.verticalLayout_4.addLayout(self.horizontalLayout_13)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.import_columns_points = QtGui.QListView(self.point_tab)
        self.import_columns_points.setEnabled(False)
        self.import_columns_points.setFlow(QtGui.QListView.LeftToRight)
        self.import_columns_points.setObjectName(_fromUtf8("import_columns_points"))
        self.verticalLayout_4.addWidget(self.import_columns_points)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/points.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolBox.addItem(self.point_tab, icon3, _fromUtf8(""))
        self.line_tab = QtGui.QWidget()
        self.line_tab.setGeometry(QtCore.QRect(0, 0, 374, 381))
        self.line_tab.setObjectName(_fromUtf8("line_tab"))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/ic_timeline_black_48px.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolBox.addItem(self.line_tab, icon4, _fromUtf8(""))
        self.wells = QtGui.QWidget()
        self.wells.setGeometry(QtCore.QRect(0, 0, 374, 381))
        self.wells.setObjectName(_fromUtf8("wells"))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/WellDerick.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolBox.addItem(self.wells, icon5, _fromUtf8(""))
        self.properties = QtGui.QWidget()
        self.properties.setGeometry(QtCore.QRect(0, 0, 374, 381))
        self.properties.setObjectName(_fromUtf8("properties"))
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/ic_equalizer_48px.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolBox.addItem(self.properties, icon6, _fromUtf8(""))
        self.well_logs = QtGui.QWidget()
        self.well_logs.setGeometry(QtCore.QRect(0, 0, 374, 381))
        self.well_logs.setObjectName(_fromUtf8("well_logs"))
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/log.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolBox.addItem(self.well_logs, icon7, _fromUtf8(""))
        self.verticalLayout_3.addWidget(self.toolBox)
        self.start_import_button = QtGui.QPushButton(self.import_data)
        self.start_import_button.setObjectName(_fromUtf8("start_import_button"))
        self.verticalLayout_3.addWidget(self.start_import_button)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/ic_file_download_48px.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabwidget.addTab(self.import_data, icon8, _fromUtf8(""))
        self.process_data = QtGui.QWidget()
        self.process_data.setObjectName(_fromUtf8("process_data"))
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/ic_swap_calls_48px.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabwidget.addTab(self.process_data, icon9, _fromUtf8(""))
        self.export_data = QtGui.QWidget()
        self.export_data.setObjectName(_fromUtf8("export_data"))
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/ic_file_upload_48px.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabwidget.addTab(self.export_data, icon10, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabwidget)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        GeologicalDataProcessingDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(GeologicalDataProcessingDockWidgetBase)
        self.tabwidget.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(GeologicalDataProcessingDockWidgetBase)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.database_file, self.select_DB)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.select_DB, self.tabwidget)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.tabwidget, self.import_file)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.import_file, self.import_file_button)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.import_file_button, self.working_dir)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.working_dir, self.working_dir_button)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.working_dir_button, self.mQgsProjectionSelectionWidget)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.mQgsProjectionSelectionWidget, self.easting_points)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.easting_points, self.northing_points)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.northing_points, self.altitude_points)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.altitude_points, self.strat_points)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.strat_points, self.strat_age_points)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.strat_age_points, self.point_set_name)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.point_set_name, self.comment_points)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.comment_points, self.separator_points)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.separator_points, self.multiple_separators_points)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.multiple_separators_points, self.import_columns_points)
        GeologicalDataProcessingDockWidgetBase.setTabOrder(self.import_columns_points, self.start_import_button)

    def retranslateUi(self, GeologicalDataProcessingDockWidgetBase):
        GeologicalDataProcessingDockWidgetBase.setWindowTitle(_translate("GeologicalDataProcessingDockWidgetBase", "Geological Data Processing", None))
        self.label.setText(_translate("GeologicalDataProcessingDockWidgetBase", "<html><head/><body><p><span style=\" font-weight:600;\">Create or import a geological sqlite database</span></p></body></html>", None))
        self.select_DB.setText(_translate("GeologicalDataProcessingDockWidgetBase", "select a database", None))
        self.select_DB.setShortcut(_translate("GeologicalDataProcessingDockWidgetBase", "Ctrl+O", None))
        self.import_file_button.setText(_translate("GeologicalDataProcessingDockWidgetBase", "data file", None))
        self.working_dir_button.setText(_translate("GeologicalDataProcessingDockWidgetBase", "working directory", None))
        self.label_12.setText(_translate("GeologicalDataProcessingDockWidgetBase", "Coordinate Reference System:", None))
        self.label_9.setText(_translate("GeologicalDataProcessingDockWidgetBase", "<html><head/><body><p><span style=\" font-weight:600;\">define column content</span></p></body></html>", None))
        self.label_2.setText(_translate("GeologicalDataProcessingDockWidgetBase", "easting", None))
        self.label_3.setText(_translate("GeologicalDataProcessingDockWidgetBase", "northing", None))
        self.label_4.setText(_translate("GeologicalDataProcessingDockWidgetBase", "altitude", None))
        self.label_5.setText(_translate("GeologicalDataProcessingDockWidgetBase", "stratigraphy", None))
        self.label_6.setText(_translate("GeologicalDataProcessingDockWidgetBase", "stratigraphic age", None))
        self.label_7.setText(_translate("GeologicalDataProcessingDockWidgetBase", "point set name", None))
        self.label_8.setText(_translate("GeologicalDataProcessingDockWidgetBase", "comment", None))
        self.label_11.setText(_translate("GeologicalDataProcessingDockWidgetBase", "separator", None))
        self.multiple_separators_points.setText(_translate("GeologicalDataProcessingDockWidgetBase", "summarize multiple", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.point_tab), _translate("GeologicalDataProcessingDockWidgetBase", "Points", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.line_tab), _translate("GeologicalDataProcessingDockWidgetBase", "Lines", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.wells), _translate("GeologicalDataProcessingDockWidgetBase", "Wells", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.properties), _translate("GeologicalDataProcessingDockWidgetBase", "Properties", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.well_logs), _translate("GeologicalDataProcessingDockWidgetBase", "Well Logs", None))
        self.start_import_button.setText(_translate("GeologicalDataProcessingDockWidgetBase", " Start Data Import", None))
        self.tabwidget.setTabText(self.tabwidget.indexOf(self.import_data), _translate("GeologicalDataProcessingDockWidgetBase", "Import Data", None))
        self.tabwidget.setTabText(self.tabwidget.indexOf(self.process_data), _translate("GeologicalDataProcessingDockWidgetBase", "Process Data", None))
        self.tabwidget.setTabText(self.tabwidget.indexOf(self.export_data), _translate("GeologicalDataProcessingDockWidgetBase", "Export Data", None))

from qgis.gui import QgsProjectionSelectionWidget
import resources_rc