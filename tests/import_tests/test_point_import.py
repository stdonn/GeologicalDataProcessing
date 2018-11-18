"""
An unittest module for testing the point import_tests functionality inside QGIS
"""

# noinspection PyUnresolvedReferences
import os.path
import unittest

from GeologicalDataProcessing.geological_data_processing_dockwidget import GeologicalDataProcessingDockWidget
import GeologicalDataProcessing.tests.test_data as test_data

# noinspection PyUnresolvedReferences
from qgis.gui import QgisInterface


class TestPointImportClass(unittest.TestCase):
    """
    This is a unittest class for the miscellaneous.ExceptionHandling.ExceptionHandling class
    """

    def __init__(self, *args, iface: QgisInterface, dockwidget: GeologicalDataProcessingDockWidget) -> None:
        """
        Initialization of the unittest class
        :param iface: Stores the path to the current iface instance
        :param dockwidget: An instance of the dockwidget element
        :param args: arguments for the base class
        :param kwargs: arguments for the base class
        """
        self.test_data_path = os.path.dirname(test_data.__file__)
        self.iface = iface
        self.dockwidget = dockwidget
        super().__init__(*args)

    def setUp(self) -> None:
        """
        Currently nothing to initialize

        :return: None
        """
        pass

    def test_column_fill_in(self):
        point_data = os.path.join(self.test_data_path, "point_data.txt")
        self.dockwidget.import_file.setText(point_data)
        self.assertEqual(point_data, self.dockwidget.import_file.text())

    def tearDown(self) -> None:
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass


if __name__ == "__main__":
    unittest.main()
