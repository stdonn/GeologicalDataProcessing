"""
Defines models for the data import
"""

import os

from PyQt5.QtCore import pyqtSignal
from typing import List


class ImportModelInterface:
    """
    Interface class for all import models
    """

    __separators = [';', ',', '\t', '.', '-', '_', '/', '\\']

    def __init__(self):
        """
        instance initialization
        """
        self.__coordinate_system = ""
        self.__data_file = ""
        self.__separator = ';'
        self.__working_dir = ""

    # setter and getter

    @property
    def coordinate_system(self) -> str:
        """
        Property for setting and getting the coordinate system. The coordinate system is not checked for correctness.
        :return: the coordinate system
        """
        return self.__coordinate_system

    @coordinate_system.setter
    def coordinate_system(self, crs: str) -> None:
        """
        Property for setting and getting the coordinate system. The coordinate system is not checked for correctness.
        :return: the coordinate system
        """
        self.__coordinate_system = str(crs)

    @property
    def data_file(self) -> str:
        """
        Property for setting and getting the path of the data file.
        :return: the path of the data file
        :raises ValueError: if path doesn't exists or is a directory.
        """
        return self.__data_file

    @data_file.setter
    def data_file(self, path: str) -> None:
        """
        Property for setting and getting the path of the data file.
        :return: the path of the data file
        :raises ValueError: if path doesn't exists or is a directory.
        """
        path = os.path.normpath(path)
        if not os.path.isfile(path):
            raise ValueError("The path \"{}\" is not a file!".format(path))
        self.__data_file = path

    @property
    def separator(self) -> str:
        """
        Property for setting and getting the column separator of the data file.
        :return: the currently set separator
        :raises ValueError: if the committed separator is not in the list of possible separators.
        """
        return self.__separator

    @separator.setter
    def separator(self, sep: str) -> None:
        """
        Property for setting and getting the column separator of the data file.
        :return: the currently set separator
        :raises ValueError: if the committed separator is not in the list of possible separators.
        """
        if sep in self.__separators:
            self.__separator = sep
            return

        raise ValueError("Separator \"{}\" not in list of possible separators!".format(sep))

    @property
    def working_directory(self) -> str:
        """
        Property for setting and getting the path of the working directory.
        :return: the path of the working directory
        :raises ValueError: if path doesn't exists or is not a directory.
        """
        return self.__working_dir

    @working_directory.setter
    def working_directory(self, path: str) -> None:
        """
        Property for setting and getting the path of the working directory.
        :return: the path of the working directory
        :raises ValueError: if path doesn't exists or is not a directory.
        """
        path = os.path.normpath(path)
        if not os.path.isdir(path):
            raise ValueError("The path \"{}\" is not a directory!".format(path))
        self.__working_dir = path

    # public functions
    def get_separator_list(self) -> List[str]:
        """
        Returns the list of possible separators
        :return: Returns the list of possible separators
        """
        return self.__separators


class PointImportModel(ImportModelInterface):
    """
    Import model for point data.
    """

    # save column names and indices
    _columns = {
        "easting"          : 0,
        "northing"         : 0,
        "altitude"         : -1,
        "stratigraphy"     : -1,
        "stratigraphic_age": -1,
        "set_name"         : -1,
        "comment"          : -1
    }

    def __init__(self):
        super().__init__()

    # signals
    model_changed = pyqtSignal(name='model_changed')

    def get_column_index(self, name: str) -> int:
        """
        Returns the current column index of the column with given name. Returns -1 if no index is defined.
        Column names are:

        - easting
        - northing
        - altitude
        - stratigraphy
        - stratigraphic_age
        - set_name
        - comment

        :param name: name of the requested column
        :return: Returns the current column number of the column with given name.
        :raises ValueError: if name is not a known column
        """
        if name not in self._columns:
            raise ValueError("Column name \"{}\" is not defined!".format(name))
        return self._columns[name]

    def set_column_index(self, name: str, column_index: int) -> None:
        """
        Sets a new column index of the column with given name. Indices < 0 are set the -1 to represent no index.
        Column names are:

        - easting
        - northing
        - altitude
        - stratigraphy
        - stratigraphic_age
        - set_name
        - comment

        :param name: name of the requested column
        :param column_index: new index of the requested column
        :return: Returns the current column number of the column with given name.
        :raises ValueError: if name is not a known column or column_index is not convertible to int
        """
        if name not in self._columns:
            raise ValueError("Column name \"{}\" is not defined!".format(name))

        column_index = int(column_index)

        if column_index < 0:
            column_index = -1
        self._columns[name] = column_index


class LineImportModel(PointImportModel):
    """
    Import model for line data. Hence lines are a list of points and share therefore many data, this class is derived
    from the PointImportModel.
    """

    def __init__(self):
        super().__init__()
        pass
