from qgis.core import *
import numpy


# The layer provided its supposed to be a list of points in order, If you not comply with this the Polygon
# May have errors
def create_polygon(layer):

    # This was the layer used for testing
    features = list(layer.getFeatures())

    temp_layer = QgsVectorLayer("Polygon?crs=epsg:4326", "result_polygon", "memory")
    temp_layer.startEditing()
    temp_dataprov = temp_layer.dataProvider()

    polyfeature = QgsFeature()

    geom = QgsGeometry.fromPolygon([[p.geometry().asPoint() for p in features]])

    polyfeature.setGeometry(geom)

    temp_dataprov.addFeatures([polyfeature])

    return temp_layer


# Compare polygons and return the area of intersection
def compare_polygons(census_tract, buffer_layer):
    rho = []

    a_calc = QgsDistanceArea()
    a_calc.computeAreaInit()

    census_feats = list(census_tract.getFeatures())
    buffer_feats = buffer_layer.getFeatures().next()  # .next() because there is only one feature in polygon

    for feat in census_feats:
        # areas are converted from degrees to square miles

        tract_area = a_calc.convertAreaMeasurement(feat.geometry().area(), QgsUnitTypes.SquareMiles)
        tract_id = feat["TRACT"]

        if feat.geometry().intersects(buffer_feats.geometry()):
            if buffer_feats.geometry().contains(feat.geometry()):
                print "TRACT_%s - FULL INTERSECTION [100%%, %fmi^2]" % (tract_id, tract_area)

                rho.append(1)
            else:
                intersection_area = a_calc.convertAreaMeasurement(
                    feat.geometry().intersection(buffer_feats.geometry()).area(), QgsUnitTypes.SquareMiles)

                print "TRACT_%s - PARTIAL INTERSECTION [%.2f%%, %fmi^2]" % \
                      (tract_id, (intersection_area/tract_area)*100, intersection_area)

                rho.append(intersection_area/tract_area)

        else:
            print "TRACT_%s - NO INTERSECTION" % tract_id

            rho.append(0)

    print numpy.array(rho)

    return numpy.array(rho)


# This method merge all the features and return a buffer of the given area, the buffer only have one feature
def generate_buffer(lines_layer):
    # Used to generate a 3/4 mile buffer around the service routes(line vector layer).

    # In order to have a single polygon(the buffer) we need to merge all the geometries
    # so we can have a single feature
    layer_with_features_merge = QgsVectorLayer("Polygon?crs=epsg:4326", "merge_features_layer", "memory")
    merge_prov = layer_with_features_merge.dataProvider()

    # The list of features of the input layer
    features_in_line = list(lines_layer.getFeatures())

    # This variable will contain all the geometries merge in it
    merge_geom = features_in_line[0].geometry()

    # This loop will merge all the Geometries
    for feat in features_in_line:
            merge_geom = merge_geom.combine(feat.geometry())

    # To add the new Merge geometry to the New Layer
    merge_geom_feature = QgsFeature()
    merge_geom_feature.setGeometry(merge_geom)
    merge_prov.addFeatures([merge_geom_feature])

    # The buffer that will be return
    buffer_to_return = QgsVectorLayer("Polygon?crs=epsg:4326", "buffer", "memory")
    prov = buffer_to_return.dataProvider()

    # The list of features, since we merge all the futures its supposed to be only one feature
    features_in_line = list(layer_with_features_merge.getFeatures())

    for feat in features_in_line:

        inAttr = feat.attributes()  # Input attributes
        inGeom = feat.geometry()  # Input geometry

        # The 0.012070080 represents 3/4 miles, (convertion from miles to meters)
        bf_inGeom = inGeom.buffer(0.012070080, 50)
        poly = bf_inGeom.asPolygon()
        drawn_area = bf_inGeom.area()
        inAttr.append(drawn_area)
        outGeom = QgsFeature()
        outGeom.setGeometry(QgsGeometry.fromPolygon(poly))  # Output geometry
        outGeom.setAttributes(inAttr)  # Output attributes
        prov.addFeatures([outGeom])

    return buffer_to_return


# This method assumes that each polygon has only one feature
def coverage_lambda(min_coverage, my_polygon):
    # Used to verify if min coverage satisfies federal requirements.
    # If true return lambda=0, else return lambda=1

    min_coverage_poly = min_coverage.getFeatures().next()
    poly_being_evaluated = my_polygon.getFeatures().next()

    if poly_being_evaluated.geometry().intersects(min_coverage_poly.geometry()):

        if poly_being_evaluated.geometry().contains(min_coverage_poly.geometry()):
            print "FULL INTERSECTION -> LAMBDA = 1"
            return 1
        else:
            print "PARTIAL INTERSECTION -> LAMBDA = 0"
            return 0

    return 0  # defaults to 0 in case there's NO intersection when compared

