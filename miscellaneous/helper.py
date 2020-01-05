# -*- coding: UTF-8 -*-
"""
Module providing basic helper functions
"""

from typing import List, Tuple


def get_file_name(obj: Tuple or str) -> str:
    """
    returns a string from the return of the QFileDialog request
    -> on MacOS it is stored as a tuple, on Windows as a str
    :param obj: return object of a QFileDialog request
    :return: returns a string from the return of the QFileDialog request
    :raises ValueError: if obj is not an instance of str or tuple or has no elements if it is a tuple
    """
    if isinstance(obj, tuple) and len(obj) > 0:
        return str(obj[0])
    elif isinstance(obj, str):
        return obj

    raise ValueError("Cannot return file path. Element is empty or not an instance of tuple or string!")


def diff(first: List[Tuple[str, str]], second: List[str]) -> List:
    second = set(second)
    return [item for item in first if item[0] not in second]
