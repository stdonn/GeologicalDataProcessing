from typing import List

from GeologicalDataProcessing.miscellaneous.qgis_log_handler import QGISLogHandler
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant, QSize, QRectF
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem, QComboBox
from geological_toolbox.properties import PropertyTypes


class PropertyImportData:
    __name = ""
    __property_type = PropertyTypes.STRING
    __unit = ""

    def __init__(self, name: str = "", property_type: PropertyTypes = PropertyTypes.STRING, unit: str = ""):
        self.name = name
        self.property_type = property_type
        self.unit = unit

    def __repr__(self):
        return "PropertyImportData <{}, {}, {}>".format(self.name, self.property_type, self.unit)

    def __str__(self):
        return "{} [{}]: {}".format(self.name, "-" if self.unit == "" else self.unit, self.property_type)

    def __get_name(self) -> str:
        return self.__name

    def __set_name(self, value: str) -> None:
        self.__name = value

    def __get_property_type(self) -> PropertyTypes:
        return self.__property_type

    def __set_property_type(self, value: PropertyTypes) -> None:
        if isinstance(value, PropertyTypes):
            self.__property_type = value
        else:
            raise TypeError("{} is not of type PropertyTypes".format(value))

    def __get_unit(self) -> str:
        return self.__unit

    def __set_unit(self, value: str) -> None:
        self.__unit = value

    name = property(__get_name, __set_name)
    property_type = property(__get_property_type, __set_property_type)
    unit = property(__get_unit, __set_unit)

    def __getitem__(self, index: int) -> object:
        """
        returns the item at index
        :param index: index of the item
        :return: returns the item at index
        """
        if index == 0:
            if self.unit == "":
                return self.name
            return "{} [{}]".format(self.name, self.unit)
        elif index == 1:
            if self.property_type == PropertyTypes.INT:
                return "Integer"
            elif self.property_type == PropertyTypes.FLOAT:
                return "Float"
            else:
                return "String"
        else:
            raise IndexError("Index out of bound ({}). Possible values are 0 and 1!".format(index))


class LogImportData(PropertyImportData):
    def __init__(self, name: str = "", unit: str = ""):
        super().__init__(name, PropertyTypes.FLOAT, unit)


class PropertyImportModel(QAbstractTableModel):
    """
    Derived Table Model for the storage of UnitConstructionData
    """

    def __init__(self, only_numbers: bool = False, parent: QWidget = None, *args) -> None:
        """
        Initialize the object
        :param only_numbers: show only number rows and don't display type column
        """
        # noinspection PyArgumentList
        QAbstractTableModel.__init__(self, parent, *args)
        self.__only_numbers = only_numbers
        self.__data_list: List[PropertyImportData] = list()
        self.__header_labels = ["Property"] if only_numbers else ["Property", "Type"]
        self.logger = QGISLogHandler(self.__class__.__name__)

    # noinspection PyMethodOverriding
    def add(self, data: PropertyImportData) -> bool:
        """
        adds a new row at the end of the model.
        :param row: row index where to insert the new row
        :param data: data to be insert
        :return: True, if the insert was performed successfully, else False
        """
        self.beginInsertRows(QModelIndex(), self.rowCount() - 1, self.rowCount() - 1)
        self.__data_list.append(data)
        self.endInsertRows()
        return True

    def clear(self) -> None:
        """
        Removes all rows.
        :return: Nothing
        """
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self.__data_list = list()
        self.endRemoveRows()

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """
        returns the current column count of the table model
        :param parent: redundant parameter as this derived class isn't a tree model
        :return: returns the current column count of the table model
        """
        return len(self.__header_labels)

    # noinspection PyMethodOverriding
    def data(self, index: QModelIndex, role):
        """
        returns the data at the given index and the given role. Derived function.
        :param index: index of the requested data
        :param role: role of the requested data
        :return: returns the data at the given index and the given role
        """
        if not index.isValid():
            return QVariant()
        elif role in (Qt.DisplayRole, Qt.EditRole):
            return QVariant(self.__data_list[index.row()][index.column()])
        elif index.column() == 0 and role == Qt.TextAlignmentRole:
            return Qt.AlignLeft
        elif index.column() == 1 and role == Qt.TextAlignmentRole and not self.__only_numbers:
            return Qt.AlignRight
        return QVariant()

    # noinspection PyTypeChecker
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Set the editable flag for the given model index. Derived function
        :param index: model index for which the flags are requested
        :return: Qt.ItemFlags
        """
        if not index.isValid():
            return Qt.ItemIsEnabled

        if index.column() == 1 and not self.__only_numbers:
            return Qt.ItemIsEditable | super(QAbstractTableModel, self).flags(index)

        return super(QAbstractTableModel, self).flags(index)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> str:
        """
        Derived functions which returns the header data for the given section, orientation and role
        :param section: section of the requested header data
        :param orientation: orientation of the requested header data
        :param role: role of the requested header data
        :return: returns the header data for the given section, orientation and role
        """
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if -1 < section < len(self.__header_labels):
                return self.__header_labels[section]
        return super(QAbstractTableModel, self).headerData(section, orientation, role)

    # noinspection PyMethodOverriding
    def insertRow(self, row: int, data: PropertyImportData) -> bool:
        """
        inserts a new row into the model. Derived and adapted function.
        :param row: row index where to insert the new row
        :param data: data to be insert
        :return: True, if the insert was performed successfully, else False
        """
        self.beginInsertRows(QModelIndex(), row, row)
        if row < 0:
            self.endInsertRows()
            return False
        self.__data_list.insert(row, data)
        self.endInsertRows()
        return True

    # noinspection PyMethodOverriding
    def removeRow(self, row: int) -> bool:
        """
        Removes the row at the given index "row".
        :param row: index of the row to be removed
        :return: True, if the row was removed successfully, else False
        """
        self.beginRemoveRows(QModelIndex(), row, row)
        if 0 <= row < self.rowCount():
            del self.__data_list[row]
            self.endRemoveRows()
            return True
        self.endRemoveRows()
        return False

    def row(self, index: int) -> PropertyImportData or None:
        """
        returns PropertyImportData-item at given index
        :param index: index of requested PropertyImportData-item
        :return: returns the item at given index
        """
        if 0 <= index < self.rowCount():
            return self.__data_list[index]
        return None

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """
        returns the current row count of the table model
        :param parent: redundant parameter as this derived class isn't a tree model
        :return: returns the current row count of the table model
        """
        return len(self.__data_list)

    def setData(self, index: QModelIndex, value: str, role: int = Qt.EditRole) -> bool:
        """
        Sets the current data at the given model index and role to value
        :param index: model index to be changed (only Type is editable, column 2)
        :param value: new value to be set
        :param role: role of data
        :return: True, if the data was set successfully, else False
        """
        if not index.isValid():
            return False
        if role == Qt.EditRole and index.column() == 1 and not self.__only_numbers:
            if str(value).lower() == "integer":
                self.__data_list[index.row()].property_type = PropertyTypes.INT
            elif str(value).lower() == "float":
                self.__data_list[index.row()].property_type = PropertyTypes.FLOAT
            else:
                self.__data_list[index.row()].property_type = PropertyTypes.STRING

            self.logger.debug("Setting data for index [{}, {}]: {}".
                              format(index.column(), index.row(), self.__data_list[index.row()].property_type))
            # noinspection PyUnresolvedReferences
            self.dataChanged.emit(index, index, [Qt.EditRole])
        super().setData(index, value, role)
        return True


class LogImportModel(PropertyImportModel):
    """
    Derived Table Model for the storage of LogData
    """

    def __init__(self, parent: QWidget = None, *args) -> None:
        """
        Initialize the object
        """
        super().__init__(True, parent, *args)


class PropertyImportDelegate(QStyledItemDelegate):
    """
    Derived delegate class for drawing the UnitConstructionModel
    """

    def __init__(self, only_numbers: bool = False, *args, **kwargs):
        """
        Initialize the object
        :param only_numbers: show only number rows and don't display type column
        :param args: arguments for initialization of the base class
        :param kwargs: arguments for initialization of the base class
        """
        super().__init__(*args, **kwargs)
        self.__only_numbers = only_numbers
        self.logger = QGISLogHandler(self.__class__.__name__)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        """
        Creates an editor widget for the given index. Derived function.
        :param parent: parent QWidget
        :param option: QStyleOptionViewItem
        :param index: model index for editor creation
        :return: QWidget which represents the editor for the given model index
        """
        if index.isValid():
            if index.column() == 1 and not self.__only_numbers:
                combobox = QComboBox(parent)
                combobox.addItems(["Integer", "Float", "String"])
                combobox.setFocusPolicy(Qt.StrongFocus)
                return combobox
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:
        """
        sets the data to the given editor widget based on the model index. Derived function.
        :param editor: editor widget for which the data has to be set (only type; column == 1)
        :param index: model index from which the editor data has to be set
        :return: Nothing
        """
        if index.isValid() and index.column() == 1 and not self.__only_numbers:
            if index.data() != "":
                editor.setCurrentText(index.data())
            else:
                editor.setCurrentText("String")
            return
        super().setEditorData(editor, index)

    def setModelData(self, editor: QComboBox, model: QAbstractTableModel, index: QModelIndex) -> None:
        """
        Update the model data at the given index from the editor value. Derived function.
        :param editor: data provider
        :param model: data storage
        :param index: index where data has to be updated
        :return: Nothing
        """
        self.logger.debug("Updating model data for index [{}, {}]: {}".
                          format(index.column(), index.row(), editor.currentText()))
        if index.isValid() and index.column() == 1 and not self.__only_numbers:  # only type can is editable
            model.setData(index, editor.currentText())
            return
        super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor: QComboBox, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """
        update the editor geometry. Derived function.
        :param editor:
        :param option:
        :param index:
        :return: Nothing
        """
        # if index.isValid():
        #     if isinstance(editor, QCheckBox):
        #         pos_x = int(option.rect.x() + option.rect.width() / 2 - editor.sizeHint().width() / 2)
        #         pos_y = int(option.rect.y() + option.rect.height() / 2 - editor.sizeHint().height() / 2)
        #         editor.setGeometry(QRect(pos_x, pos_y, editor.sizeHint().width(), editor.sizeHint().height()))
        #         return
        #     if index.column() == 4:
        #         editor.setGeometry(option.rect)
        super().updateEditorGeometry(editor, option, index)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """
        paint event for drawing the model data
        :param painter: QPainter for the drawing
        :param option: QStyleOptionViewItem
        :param index: model index to be drawn
        :return: Nothing
        """
        index_data = index.data()

        # set the distance label
        if isinstance(index_data, int):
            text = "{:,} m".format(index_data).replace(',', ' ')
            rect = QRectF(option.rect)
            rect.setWidth(rect.width() - 5)
            painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, text)

        else:
            super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """
        Returns a size hint for the object at the given index
        :param option: QStyleOptionViewItem
        :param index: model index for the requested size hint
        :return: a QSize object with given hint
        """
        # if isinstance(index.data(), bool):
        #     return self.__checkbox_size
        # if isinstance(index.data(), QColor):
        #     return self.__color_size
        # if isinstance(index.data(), int):
        #     self.__label_tmp.setText("{:,} m".format(index.data()).replace(',', ' '))
        #     size = self.__label_tmp.sizeHint()
        #     size.setWidth(size.width() + 5)
        #     return size
        return super().sizeHint(option, index)


class LogImportDelegate(PropertyImportDelegate):
    """
    Derived delegate class for drawing the LogImport
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the object
        :param args: arguments for initialization of the base class
        :param kwargs: arguments for initialization of the base class
        """
        super().__init__(True, *args, **kwargs)
