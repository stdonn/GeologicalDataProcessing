# -*- coding: UTF-8 -*-
"""
Check and, if necessary, install required modules
"""

import importlib
import os
import sys
import traceback

from packaging import version
from subprocess import run, CalledProcessError, PIPE, STDOUT

from PyQt5.QtWidgets import QMessageBox

from GeologicalDataProcessing.miscellaneous.QGISDebugLog import QGISDebugLog
from GeologicalDataProcessing.config import module_list


class ModuleService:
    modules = list()

    @staticmethod
    def check_required_modules():
        """
        Check all module requirements
        :return: True is all modules with required versions were found, else false
        """
        logger = QGISDebugLog()
        logger.debug("Checking required modules")
        importlib.invalidate_caches()
        ModuleService.modules = list()
        for module in module_list:
            try:
                logger.debug("Importing module", module)
                mod = importlib.import_module(module)
                v1 = version.parse(mod.__version__)
                v2 = version.parse(module_list[module])
                if v1 < v2:
                    logger.error("Module version [{}] differs from required version [{}]".format(v1, v2))
                    ModuleService.modules.append("{}=={}".format(module, module_list[module]))
            except ModuleNotFoundError:
                logger.debug("Module not found, adding {}=={} to install list".format(module, module_list[module]))
                ModuleService.modules.append("{}=={}".format(module, module_list[module]))

        if len(ModuleService.modules) > 0:
            path = os.path.normpath(os.__file__)
            path = os.path.dirname(os.path.dirname(os.path.dirname(path)))
            exe = os.path.join(path, "bin", "pip")
            exe += " install --force-reinstall "
            exe += ' '.join(ModuleService.modules)
            logger.error("Missing packages found! Please install them with the following command from the terminal:\n{}"
                         .format(exe))

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Missing packages found!")
            text = "Following packages are missing:\n\n" + '\n'.join(ModuleService.modules)
            text += "\n\nCopy the following command and execute it inside a terminal session:\n\n"
            text += exe
            msg.setInformativeText(text)
            msg.setWindowTitle("Missing packages")
            msg.exec_()
            return False
        return True

    @staticmethod
    def install(package, ver):
        """
        install package via pip
        :param package: package to install
        :param ver: required package version
        :return: Nothing
        """
        pkg = "{}=={}".format(package, str(ver))
        logger = QGISDebugLog()

        logger.debug(package, ver)

        try:
            path = os.path.normpath(os.__file__)
            path = os.path.dirname(os.path.dirname(os.path.dirname(path)))
            exe = os.path.join(path, "bin", "pip")
            result = run([exe, "install", "--force-reinstall", pkg], stdout=PIPE, stderr=STDOUT, check=True)
            logger.info("Installed {} successfully".format(pkg))
            logger.info("Return-Code: {}".format(result.returncode))
            logger.info("STDOUT:\t{}".format(result.stdout))
        except CalledProcessError as e:
            _, _, exc_traceback = sys.exc_info()
            tb = "Traceback:\n{}".format(''.join(traceback.format_tb(exc_traceback)))
            logger.error("An exception occurred for command {}".format(e.cmd))
            logger.error("Return code: {}".format(e.returncode))
            logger.error("Output:\n\n{}\n{}".format(e.output.decode('UTF-8'), tb))
            logger.info("Could not install {}".format(pkg))
