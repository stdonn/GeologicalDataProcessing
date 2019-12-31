# -*- coding: UTF-8 -*-
"""
plugin configuration
"""
debug = True
"""
Set the general debug logging on (True) or off (False)
Can be edited individually in users config file ($HOME/.geological_data_processing)
    section: [General], option: debug
"""

module_list = {
    "packaging": "19.1",
    "GeologicalToolbox": "0.3.0.b9",
    "keyring": "19.2.0"
}
"""
Dictionary of required modules and related versions
"""