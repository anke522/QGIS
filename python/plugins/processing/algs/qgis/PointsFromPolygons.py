# -*- coding: utf-8 -*-

"""
***************************************************************************
    PointsFromPolygons.py
    ---------------------
    Date                 : August 2013
    Copyright            : (C) 2013 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import str
from builtins import range

__author__ = 'Alexander Bruy'
__date__ = 'August 2013'
__copyright__ = '(C) 2013, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from osgeo import gdal
from qgis.core import (QgsApplication,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsPointV2,
                       QgsProcessingUtils)
from qgis.PyQt.QtCore import QVariant
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster
from processing.core.parameters import ParameterVector
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector, raster


class PointsFromPolygons(GeoAlgorithm):

    INPUT_RASTER = 'INPUT_RASTER'
    RASTER_BAND = 'RASTER_BAND'
    INPUT_VECTOR = 'INPUT_VECTOR'
    OUTPUT_LAYER = 'OUTPUT_LAYER'

    def icon(self):
        return QgsApplication.getThemeIcon("/providerQgis.svg")

    def svgIconPath(self):
        return QgsApplication.iconPath("providerQgis.svg")

    def group(self):
        return self.tr('Vector analysis tools')

    def name(self):
        return 'generatepointspixelcentroidsinsidepolygons'

    def displayName(self):
        return self.tr('Generate points (pixel centroids) inside polygons')

    def defineCharacteristics(self):
        self.addParameter(ParameterRaster(self.INPUT_RASTER,
                                          self.tr('Raster layer')))
        self.addParameter(ParameterVector(self.INPUT_VECTOR,
                                          self.tr('Vector layer'), [dataobjects.TYPE_VECTOR_POLYGON]))
        self.addOutput(OutputVector(self.OUTPUT_LAYER, self.tr('Points from polygons'), datatype=[dataobjects.TYPE_VECTOR_POINT]))

    def processAlgorithm(self, context, feedback):
        layer = dataobjects.getLayerFromString(self.getParameterValue(self.INPUT_VECTOR))

        rasterPath = str(self.getParameterValue(self.INPUT_RASTER))

        rasterDS = gdal.Open(rasterPath, gdal.GA_ReadOnly)
        geoTransform = rasterDS.GetGeoTransform()
        rasterDS = None

        fields = QgsFields()
        fields.append(QgsField('id', QVariant.Int, '', 10, 0))
        fields.append(QgsField('poly_id', QVariant.Int, '', 10, 0))
        fields.append(QgsField('point_id', QVariant.Int, '', 10, 0))

        writer = self.getOutputFromName(self.OUTPUT_LAYER).getVectorWriter(fields.toList(), QgsWkbTypes.Point,
                                                                           layer.crs(), context)

        outFeature = QgsFeature()
        outFeature.setFields(fields)

        fid = 0
        polyId = 0
        pointId = 0

        features = QgsProcessingUtils.getFeatures(layer, context)
        total = 100.0 / QgsProcessingUtils.featureCount(layer, context)
        for current, f in enumerate(features):
            geom = f.geometry()
            bbox = geom.boundingBox()

            xMin = bbox.xMinimum()
            xMax = bbox.xMaximum()
            yMin = bbox.yMinimum()
            yMax = bbox.yMaximum()

            (startRow, startColumn) = raster.mapToPixel(xMin, yMax, geoTransform)
            (endRow, endColumn) = raster.mapToPixel(xMax, yMin, geoTransform)

            # use prepared geometries for faster intersection tests
            engine = QgsGeometry.createGeometryEngine(geom.geometry())
            engine.prepareGeometry()

            for row in range(startRow, endRow + 1):
                for col in range(startColumn, endColumn + 1):
                    (x, y) = raster.pixelToMap(row, col, geoTransform)
                    point = QgsPointV2()
                    point.setX(x)
                    point.setY(y)

                    if engine.contains(point):
                        outFeature.setGeometry(QgsGeometry(point))
                        outFeature['id'] = fid
                        outFeature['poly_id'] = polyId
                        outFeature['point_id'] = pointId

                        fid += 1
                        pointId += 1

                        writer.addFeature(outFeature)

            pointId = 0
            polyId += 1

            feedback.setProgress(int(current * total))

        del writer
