# -*- coding: UTF-8 -*-
"""
Module for unittests of the ExceptionHandling module
"""

import unittest

from miscellaneous.ExceptionHandling import ExceptionHandling

class TestExceptionHandlingClass(unittest.TestCase):
    """
    This is a unittest class for the miscellaneous.ExceptionHandling.ExceptionHandling class
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
        object_1 = ExceptionHandling()
        object_2 = ExceptionHandling()
        self.assertEqual(object_1, object_2)
        self.assertEqual(id(object_1), id(object_2))

        try:
            float("a")
        except ValueError as e:
            exept = ExceptionHandling(e)
            print(str(exept))

    def tearDown(self) -> None:
        """
        Empty function, nothing to shutdown after the testing process

        :return: Nothing
        """
        pass
