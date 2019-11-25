# -*- coding: UTF-8 -*-
"""
Module for unittests of the ExceptionHandler module
"""

import unittest

from GeologicalDataProcessing.miscellaneous.exception_handler import ExceptionHandler

class TestExceptionHandlingClass(unittest.TestCase):
    """
    This is a unittest class for the miscellaneous.ExceptionHandler.ExceptionHandler class
    """
    def setUp(self) -> None:
        """
        Currently nothing to initialize

        :return: None
        """
        pass

    def test_singleton_pattern(self) -> None:
        """
        test for the correct functionality of the singleton pattern
        :return: Nothing
        """
        object_1 = ExceptionHandler()
        object_2 = ExceptionHandler()
        self.assertEqual(object_1, object_2)
        self.assertEqual(id(object_1), id(object_2))

    def tearDown(self) -> None:
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass

if __name__ == "__main__":
    unittest.main()