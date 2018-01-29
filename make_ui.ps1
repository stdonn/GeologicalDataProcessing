$ENV:PATH=”$ENV:PATH;C:\OSGeo4W64\bin”
$ENV:PYTHONPATH="$ENV:PYTHONPATH;C:\OSGeo4W64\apps\Python27\Lib;C:\OSGeo4W64\apps\Python27\Lib\site-packages"

pyuic4 -o .\geological_data_processing_dockwidget_base.py .\geological_data_processing_dockwidget_base.ui
pyrcc4 -o resources_rc.py resources.qrc