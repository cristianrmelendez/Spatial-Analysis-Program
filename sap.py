import os

from qgis.gui import *
from PyQt4.QtCore import Qt
from PyQt4.QtGui import *

from polygon import *


def main():

    # init Application
    app = QApplication([], True)
    QgsApplication.setPrefixPath(os.environ["QGIS_PREFIX_PATH"], True)
    QgsApplication.initQgis()

    # init window to see results THIS IS JUST FOR TESTING
    main_window = QMainWindow()
    frame = QFrame(main_window)
    main_window.setCentralWidget(frame)
    grid_layout = QGridLayout(frame)
    canvas = QgsMapCanvas()
    grid_layout.addWidget(canvas)
    canvas.setCanvasColor(Qt.white)
    canvas.enableAntiAliasing(True)

    # The buffer which we will use as a legal reference
    legal_coverage_buffer = QgsVectorLayer("Buffer/Buffer.shp", "Buffer", "ogr")

    # This is the census tracks
    census_track = QgsVectorLayer("population_data/gz_2010_72_140_00_500k.shp", "CensusTrack", "ogr")

    # good points polygon
    good_coverage_points = QgsVectorLayer("good_coverage/good_coverage.shp", "GoodCoverage", "ogr")
    good_coverage_layer = create_polygon(good_coverage_points)

    # bad Polygon (illegal area of coverage)
    # bad_coverage_points = QgsVectorLayer("Bad_coverage/bad_coverage.shp", "bad_coverage", "ogr")
    # bad_coverage_layer = create_polygon(bad_coverage_points)

    # this are the files to test the create buffer
    lines_to_make_buffer = QgsVectorLayer("buffer_test/buffer_test.shp", "bad_coverage", "ogr")

    # lines_to_make_buffer2 = QgsVectorLayer("buffer_test2/buffer_test2.shp", "bad_coverage", "ogr")

    # generate_legal_buffer = QgsVectorLayer("legal_buffer_route/legal_buffer_route.shp", "legal_coverage","ogr")

    generated_buffer = generate_buffer(lines_to_make_buffer)

    # generated_buffer2 = generate_buffer(lines_to_make_buffer2)

    # generate_legal_buffer_result = generate_buffer(generate_legal_buffer)

    # This is just to test the buffer we create

    compare_polygons(census_track, legal_coverage_buffer)

    coverage_lambda(legal_coverage_buffer, good_coverage_layer)

    # just to see the resulsts layer
    # add layer to the registry
    if not good_coverage_layer.isValid():
        raise IOError, "Failed to open the layer"

    # add layer to registry
    QgsMapLayerRegistry.instance().addMapLayer(good_coverage_layer)
    QgsMapLayerRegistry.instance().addMapLayer(generated_buffer)
    QgsMapLayerRegistry.instance().addMapLayer(legal_coverage_buffer)
    QgsMapLayerRegistry.instance().addMapLayer(good_coverage_layer)

    # canvas_layer = QgsMapCanvasLayer(good_coverage_layer)
    buffer_layer = QgsMapCanvasLayer(generated_buffer)
    # legal_coverage = QgsMapCanvasLayer(legal_coverage_buffer)
    # legal_coverage_result = QgsMapCanvasLayer(good_coverage_layer)

    # set extent to the extent of our layer

    # set the map canvas layer set
    canvas.setLayerSet([buffer_layer])

    canvas.zoomToFullExtent()
    canvas.refresh()
    main_window.show()
    app.exec_()


main()



