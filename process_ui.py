# -*- coding: utf-8 -*-
"""
remove process ui conversion and remove errors
"""

import platform
from subprocess import run, PIPE, STDOUT, CalledProcessError

without_resources = True

if __name__ == '__main__':
    ui_file_names = ("geological_data_processing_dockwidget_base_2.ui", "settings_dialog_2.ui")

    for ui_file_name in ui_file_names:
        ui_file = open(ui_file_name, 'r')
        lines = []
        resource = False
        for line in ui_file:
            if without_resources:
                if resource and ("</resources>" in line):
                    resource = False
                    continue
                elif resource:
                    continue
                elif "<resources>" in line:
                    resource = True
                    # lines.append(line.replace("<resources>", "<resources/>").rstrip())
                else:
                    lines.append(line.replace("<header>qgsprojectionselectionwidget.h</header>",
                                              "<header>qgis.gui</header>").rstrip())
            else:
                lines.append(line.replace("<header>qgsprojectionselectionwidget.h</header>",
                                          "<header>qgis.gui</header>").rstrip())

        ui_file.close()
        ui_file = open(ui_file_name.replace("_2.ui", ".ui"), 'w')
        ui_file.write("\n".join(lines))
        ui_file.close()

    try:
        run(["/usr/local/bin/pyrcc5", "resources.qrc", "-o", "resources.py"],
            stdout=PIPE, stderr=STDOUT, check=True)
    except CalledProcessError as e:
        print("Could not execute command {}".format(e.returncode))
        print("Return-Code: {} - Output:\n{}".format(e.returncode, e.output))
