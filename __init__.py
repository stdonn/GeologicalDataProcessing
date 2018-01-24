# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeologicalDataProcessing
                                 A QGIS plugin
 This plugin connect the GeologicalToolbox Python module to QGIS.
                             -------------------
        begin                : 2018-01-24
        copyright            : (C) 2018 by Stephan Donndorf
        email                : stephan@donndorf.info
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GeologicalDataProcessing class from file GeologicalDataProcessing.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .geological_data_processing import GeologicalDataProcessing
    return GeologicalDataProcessing(iface)
