# -*- coding: UTF-8 -*-
"""
Module for basic exception handling
"""

import sys
import traceback

import GeologicalDataProcessing.config as config

from configparser import ConfigParser
from pathlib import Path


class ConfigHandler:
    """
    Singleton class for user specific config file handling
    """
    __instance: "ConfigHandler" = None

    def __new__(cls) -> "ConfigHandler":
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        return cls.__instance

    def __init__(self):
        self.__config_file = Path.joinpath(Path.home(), ".geological_data_processing")
        self.__config_parser = ConfigParser()

        if Path.is_file(self.__config_file):
            self.__config_parser.read(str(self.__config_file))

        debug = self.get("General", "debug")
        if debug != "":
            config.debug = True if debug.lower() in ["true", "yes", "on", "1"] else False

    def get(self, section: str, option: str) -> str:
        return self.__config_parser.get(section, option, fallback="")

    def set(self, section: str, option: str, value: any) -> None:
        if not self.__config_parser.has_section(section):
            self.__config_parser.add_section(section)

        self.__config_parser.set(section, option, value)
        with open(str(self.__config_file), 'w') as cf:
            self.__config_parser.write(cf)

    def get_config_path(self) -> str:
        return str(self.__config_file)

    def has_section(self, section: str) -> bool:
        return self.__config_parser.has_section(section)
    
    def has_option(self, section: str, option: str) -> bool:
        return self.__config_parser.has_option(section, option)

    def get_config_parser(self) -> ConfigParser:
        return self.__config_parser
