# -*- coding: utf-8 -*-
"""
remove process ui conversion and remove errors
"""

import platform
import subprocess

without_resources = True

if __name__ == '__main__':
    ui_file_name = "geological_data_processing_dockwidget_base_2.ui"
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
            lines.append(line.replace("<header>qgsprojectionselectionwidget.h</header>", "<header>qgis.gui</header>").
                         rstrip())

    ui_file.close()
    ui_file = open(ui_file_name.replace("_2.ui", ".ui"), 'w')
    ui_file.write("\n".join(lines))
    ui_file.close()

    if platform.system() == "Windows":
        process = subprocess.Popen(["C:\\OSGeo4W64\\bin\\pyrcc4.exe", "-o", "resources_rc.py", "resources.qrc"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen(["pyrcc4", "-o", "resources_rc.py", "resources.qrc"], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    process.wait()
    stdout = process.stdout.read()
    stderr = process.stderr.read()

    if (stdout != "") and (stderr != ""):
        print("Could not run pyrcc4:")
        print("stdout:\n{}".format(stdout))
        print("stderr:\n{}".format(stderr))
