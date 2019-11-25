# -*- coding: UTF-8 -*-
"""
Check and, if necessary, install required modules
"""

import importlib
import json
import os
import sys

packages_found = "INSTALLED"

try:
    from subprocess import run, CalledProcessError, PIPE, STDOUT

    from PyQt5.QtWidgets import QMessageBox

    from GeologicalDataProcessing.miscellaneous.qgis_log_handler import QGISLogHandler
    from GeologicalDataProcessing.config import module_list

    from packaging import version

except ModuleNotFoundError:
    packages_found = "NO_PACKAGES"


class ModuleService:
    modules = list()

    @staticmethod
    def check_required_modules():
        """
        Check all module requirements
        :return: True is all modules with required versions were found, else false
        """
        logger = QGISLogHandler("ModuleService")

        # don't display logging to QGIS
        safed_iface = logger.qgis_iface
        logger.qgis_iface = None

        logger.info("Checking required modules")

        python = ModuleService.get_python()

        cmd = [python, "-m", "pip", "list", "--format", "json", "--user"]

        try:
            logger.info("Checking package versions")
            logger.info("CMD: {}".format(" ".join(cmd)))

            result = run(cmd, stdout=PIPE, stderr=STDOUT, check=True)
            logger.info("run pip info successful")
            packages = json.loads(result.stdout.decode())

        except CalledProcessError as e:
            # restore QGIS logging
            logger.qgis_iface = safed_iface
            logger.error("pip info request failed!")
            logger.error("RETURN-CODE: {} - CMD: {}".format(e.returncode, e.cmd))
            logger.error("OUTPUT: {}".format(e.output))
            return False

        ModuleService.modules = list()
        for module in module_list:
            module_found = False
            for package in packages:
                if package["name"] != module:
                    continue
                module_found = True

                logger.debug("found module {} [{}]".format(package["name"], package["version"]))

                v1 = version.parse(package["version"])
                v2 = version.parse(module_list[module])
                if v1 < v2:
                    logger.warn("Module version [{}] differs from required version [{}]".format(v1, v2))
                    ModuleService.modules.append("{}=={}".format(module, module_list[module]))

            if not module_found:
                logger.debug("Module not found, adding {}=={} to install list".format(module, module_list[module]))
                ModuleService.modules.append("{}=={}".format(module, module_list[module]))

        if len(ModuleService.modules) > 0:
            # restore QGIS logging
            logger.qgis_iface = safed_iface
            logger.info("Missing packages found: {}".format(ModuleService.modules))
            return False

        logger.info("All packages up to date")

        # restore QGIS logging
        logger.qgis_iface = safed_iface
        return True

    @staticmethod
    def get_python() -> str:
        """
        returns the qqis python executable
        :return: the qqis python executable
        """
        python = sys.executable
        if "PYTHONHOME" in os.environ.keys():
            python = os.path.normpath(os.environ["PYTHONHOME"] + "/bin/python3")

        return python

    @staticmethod
    def install_packages():
        """
        installs  base packages via pip, e.g. packaging package
        :return: True if packages installed successfully else False
        """
        logger = QGISLogHandler("ModuleService")

        python = ModuleService.get_python()

        requirements = list("{}>={}".format(key, module_list[key]) for key in module_list.keys())
        cmd = [python, "-m", "pip", "install", "--force-reinstall", "--user", "--upgrade"] + requirements

        try:
            logger.info("Installing packages", ", ".join(requirements))
            logger.info("CMD: {}".format(" ".join(cmd)))

            result = run(cmd, stdout=PIPE, stderr=STDOUT, check=True)

            logger.info("installation result", result.stdout.decode())
            return True

        except CalledProcessError as e:
            logger.error("Package installation failed!")
            logger.error("RETURN-CODE: {} - CMD: {}".format(e.returncode, e.cmd))
            logger.error("OUTPUT: {}".format(e.output))
            return False
