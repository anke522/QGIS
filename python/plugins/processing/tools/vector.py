# -*- coding: utf-8 -*-

"""
***************************************************************************
    vector.py
    ---------------------
    Date                 : February 2013
    Copyright            : (C) 2013 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from builtins import object


__author__ = 'Victor Olaya'
__date__ = 'February 2013'
__copyright__ = '(C) 2013, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import re
import os
import csv
import uuid

import psycopg2
from osgeo import ogr

from qgis.PyQt.QtCore import QVariant, QCoreApplication
from qgis.core import (QgsFields,
                       QgsField,
                       QgsGeometry,
                       QgsRectangle,
                       QgsWkbTypes,
                       QgsSpatialIndex,
                       QgsProject,
                       QgsMapLayer,
                       QgsVectorLayer,
                       QgsVectorFileWriter,
                       QgsDistanceArea,
                       QgsDataSourceUri,
                       QgsCredentials,
                       QgsFeatureRequest,
                       QgsSettings,
                       QgsProcessingContext,
                       QgsProcessingUtils,
                       QgsMessageLog)

from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.tools import dataobjects, spatialite, postgis


TYPE_MAP = {
    str: QVariant.String,
    float: QVariant.Double,
    int: QVariant.Int,
    bool: QVariant.Bool
}

TYPE_MAP_MEMORY_LAYER = {
    QVariant.String: "string",
    QVariant.Double: "double",
    QVariant.Int: "integer",
    QVariant.Date: "date",
    QVariant.DateTime: "datetime",
    QVariant.Time: "time"
}

TYPE_MAP_POSTGIS_LAYER = {
    QVariant.String: "VARCHAR",
    QVariant.Double: "REAL",
    QVariant.Int: "INTEGER",
    QVariant.Bool: "BOOLEAN"
}

TYPE_MAP_SPATIALITE_LAYER = {
    QVariant.String: "VARCHAR",
    QVariant.Double: "REAL",
    QVariant.Int: "INTEGER",
    QVariant.Bool: "INTEGER"
}


def resolveFieldIndex(layer, attr):
    """This method takes an object and returns the index field it
    refers to in a layer. If the passed object is an integer, it
    returns the same integer value. If the passed value is not an
    integer, it returns the field whose name is the string
    representation of the passed object.

    Ir raises an exception if the int value is larger than the number
    of fields, or if the passed object does not correspond to any
    field.
    """
    if isinstance(attr, int):
        return attr
    else:
        index = layer.fields().lookupField(attr)
        if index == -1:
            raise ValueError('Wrong field name')
        return index


def values(layer, context, *attributes):
    """Returns the values in the attributes table of a vector layer,
    for the passed fields.

    Field can be passed as field names or as zero-based field indices.
    Returns a dict of lists, with the passed field identifiers as keys.
    It considers the existing selection.

    It assummes fields are numeric or contain values that can be parsed
    to a number.
    :param context:
    """
    ret = {}
    indices = []
    attr_keys = {}
    for attr in attributes:
        index = resolveFieldIndex(layer, attr)
        indices.append(index)
        attr_keys[index] = attr

    # use an optimised feature request
    request = QgsFeatureRequest().setSubsetOfAttributes(indices).setFlags(QgsFeatureRequest.NoGeometry)

    for feature in QgsProcessingUtils.getFeatures(layer, context, request):
        for i in indices:

            # convert attribute value to number
            try:
                v = float(feature.attributes()[i])
            except:
                v = None

            k = attr_keys[i]
            if k in ret:
                ret[k].append(v)
            else:
                ret[k] = [v]
    return ret


def testForUniqueness(fieldList1, fieldList2):
    '''Returns a modified version of fieldList2, removing naming
    collisions with fieldList1.'''
    changed = True
    while changed:
        changed = False
        for i in range(0, len(fieldList1)):
            for j in range(0, len(fieldList2)):
                if fieldList1[i].name() == fieldList2[j].name():
                    field = fieldList2[j]
                    name = createUniqueFieldName(field.name(), fieldList1)
                    fieldList2[j] = QgsField(name, field.type(), len=field.length(), prec=field.precision(), comment=field.comment())
                    changed = True
    return fieldList2


def spatialindex(layer):
    """Creates a spatial index for the passed vector layer.
    """
    request = QgsFeatureRequest()
    request.setSubsetOfAttributes([])
    if ProcessingConfig.getSetting(ProcessingConfig.USE_SELECTED) \
            and layer.selectedFeatureCount() > 0:
        idx = QgsSpatialIndex(layer.getSelectedFeatures(request))
    else:
        idx = QgsSpatialIndex(layer.getFeatures(request))
    return idx


def createUniqueFieldName(fieldName, fieldList):
    def nextname(name):
        num = 1
        while True:
            returnname = '{name}_{num}'.format(name=name[:8], num=num)
            yield returnname
            num += 1

    def found(name):
        return any(f.name() == name for f in fieldList)

    shortName = fieldName[:10]

    if not fieldList:
        return shortName

    if not found(shortName):
        return shortName

    for newname in nextname(shortName):
        if not found(newname):
            return newname


def findOrCreateField(layer, fieldList, fieldName, fieldLen=24, fieldPrec=15):
    idx = layer.fields().lookupField(fieldName)
    if idx == -1:
        fn = createUniqueFieldName(fieldName, fieldList)
        field = QgsField(fn, QVariant.Double, '', fieldLen, fieldPrec)
        idx = len(fieldList)
        fieldList.append(field)

    return (idx, fieldList)


def extractPoints(geom):
    points = []
    if geom.type() == QgsWkbTypes.PointGeometry:
        if geom.isMultipart():
            points = geom.asMultiPoint()
        else:
            points.append(geom.asPoint())
    elif geom.type() == QgsWkbTypes.LineGeometry:
        if geom.isMultipart():
            lines = geom.asMultiPolyline()
            for line in lines:
                points.extend(line)
        else:
            points = geom.asPolyline()
    elif geom.type() == QgsWkbTypes.PolygonGeometry:
        if geom.isMultipart():
            polygons = geom.asMultiPolygon()
            for poly in polygons:
                for line in poly:
                    points.extend(line)
        else:
            polygon = geom.asPolygon()
            for line in polygon:
                points.extend(line)

    return points


def simpleMeasure(geom, method=0, ellips=None, crs=None):
    # Method defines calculation type:
    # 0 - layer CRS
    # 1 - project CRS
    # 2 - ellipsoidal

    if geom.type() == QgsWkbTypes.PointGeometry:
        if not geom.isMultipart():
            pt = geom.geometry()
            attr1 = pt.x()
            attr2 = pt.y()
        else:
            pt = geom.asMultiPoint()
            attr1 = pt[0].x()
            attr2 = pt[0].y()
    else:
        measure = QgsDistanceArea()

        if method == 2:
            measure.setSourceCrs(crs)
            measure.setEllipsoid(ellips)

        if geom.type() == QgsWkbTypes.PolygonGeometry:
            attr1 = measure.measureArea(geom)
            attr2 = measure.measurePerimeter(geom)
        else:
            attr1 = measure.measureLength(geom)
            attr2 = None

    return (attr1, attr2)


def combineVectorFields(layerA, layerB):
    """Create single field map from two input field maps.
    """
    fields = []
    fieldsA = layerA.fields()
    fields.extend(fieldsA)
    namesA = [str(f.name()).lower() for f in fieldsA]
    fieldsB = layerB.fields()
    for field in fieldsB:
        name = str(field.name()).lower()
        if name in namesA:
            idx = 2
            newName = name + '_' + str(idx)
            while newName in namesA:
                idx += 1
                newName = name + '_' + str(idx)
            field = QgsField(newName, field.type(), field.typeName())
        fields.append(field)

    return fields


def duplicateInMemory(layer, newName='', addToRegistry=False):
    """Return a memory copy of a layer

    layer: QgsVectorLayer that shall be copied to memory.
    new_name: The name of the copied layer.
    add_to_registry: if True, the new layer will be added to the QgsMapRegistry

    Returns an in-memory copy of a layer.
    """
    if newName is '':
        newName = layer.name() + ' (Memory)'

    if layer.type() == QgsMapLayer.VectorLayer:
        geomType = layer.geometryType()
        if geomType == QgsWkbTypes.PointGeometry:
            strType = 'Point'
        elif geomType == QgsWkbTypes.LineGeometry:
            strType = 'Line'
        elif geomType == QgsWkbTypes.PolygonGeometry:
            strType = 'Polygon'
        else:
            raise RuntimeError('Layer is whether Point nor Line nor Polygon')
    else:
        raise RuntimeError('Layer is not a VectorLayer')

    crs = layer.crs().authid().lower()
    myUuid = str(uuid.uuid4())
    uri = '%s?crs=%s&index=yes&uuid=%s' % (strType, crs, myUuid)
    memLayer = QgsVectorLayer(uri, newName, 'memory')
    memProvider = memLayer.dataProvider()

    provider = layer.dataProvider()
    fields = layer.fields().toList()
    memProvider.addAttributes(fields)
    memLayer.updateFields()

    for ft in provider.getFeatures():
        memProvider.addFeatures([ft])

    if addToRegistry:
        if memLayer.isValid():
            QgsProject.instance().addMapLayer(memLayer)
        else:
            raise RuntimeError('Layer invalid')

    return memLayer


def checkMinDistance(point, index, distance, points):
    """Check if distance from given point to all other points is greater
    than given value.
    """
    if distance == 0:
        return True

    neighbors = index.nearestNeighbor(point, 1)
    if len(neighbors) == 0:
        return True

    if neighbors[0] in points:
        np = points[neighbors[0]]
        if np.sqrDist(point) < (distance * distance):
            return False

    return True


def _toQgsField(f):
    if isinstance(f, QgsField):
        return f
    return QgsField(f[0], TYPE_MAP.get(f[1], QVariant.String))


def snapToPrecision(geom, precision):
    snapped = QgsGeometry(geom)
    if precision == 0.0:
        return snapped

    i = 0
    p = snapped.vertexAt(i)
    while p.x() != 0.0 and p.y() != 0.0:
        x = round(p.x() / precision, 0) * precision
        y = round(p.y() / precision, 0) * precision
        snapped.moveVertex(x, y, i)
        i = i + 1
        p = snapped.vertexAt(i)
    return snapped


def bufferedBoundingBox(bbox, buffer_size):
    if buffer_size == 0.0:
        return QgsRectangle(bbox)

    return QgsRectangle(
        bbox.xMinimum() - buffer_size,
        bbox.yMinimum() - buffer_size,
        bbox.xMaximum() + buffer_size,
        bbox.yMaximum() + buffer_size)


def ogrConnectionString(uri):
    """Generates OGR connection sting from layer source
    """
    ogrstr = None

    layer = dataobjects.getLayerFromString(uri, False)
    if layer is None:
        return '"' + uri + '"'
    provider = layer.dataProvider().name()
    if provider == 'spatialite':
        # dbname='/geodata/osm_ch.sqlite' table="places" (Geometry) sql=
        regex = re.compile("dbname='(.+)'")
        r = regex.search(str(layer.source()))
        ogrstr = r.groups()[0]
    elif provider == 'postgres':
        # dbname='ktryjh_iuuqef' host=spacialdb.com port=9999
        # user='ktryjh_iuuqef' password='xyqwer' sslmode=disable
        # key='gid' estimatedmetadata=true srid=4326 type=MULTIPOLYGON
        # table="t4" (geom) sql=
        dsUri = QgsDataSourceUri(layer.dataProvider().dataSourceUri())
        conninfo = dsUri.connectionInfo()
        conn = None
        ok = False
        while not conn:
            try:
                conn = psycopg2.connect(dsUri.connectionInfo())
            except psycopg2.OperationalError:
                (ok, user, passwd) = QgsCredentials.instance().get(conninfo, dsUri.username(), dsUri.password())
                if not ok:
                    break

                dsUri.setUsername(user)
                dsUri.setPassword(passwd)

        if not conn:
            raise RuntimeError('Could not connect to PostgreSQL database - check connection info')

        if ok:
            QgsCredentials.instance().put(conninfo, user, passwd)

        ogrstr = "PG:%s" % dsUri.connectionInfo()
    elif provider == "oracle":
        # OCI:user/password@host:port/service:table
        dsUri = QgsDataSourceUri(layer.dataProvider().dataSourceUri())
        ogrstr = "OCI:"
        if dsUri.username() != "":
            ogrstr += dsUri.username()
            if dsUri.password() != "":
                ogrstr += "/" + dsUri.password()
            delim = "@"

        if dsUri.host() != "":
            ogrstr += delim + dsUri.host()
            delim = ""
            if dsUri.port() != "" and dsUri.port() != '1521':
                ogrstr += ":" + dsUri.port()
            ogrstr += "/"
            if dsUri.database() != "":
                ogrstr += dsUri.database()
        elif dsUri.database() != "":
            ogrstr += delim + dsUri.database()

        if ogrstr == "OCI:":
            raise RuntimeError('Invalid oracle data source - check connection info')

        ogrstr += ":"
        if dsUri.schema() != "":
            ogrstr += dsUri.schema() + "."

        ogrstr += dsUri.table()
    else:
        ogrstr = str(layer.source()).split("|")[0]

    return '"' + ogrstr + '"'


def ogrLayerName(uri):
    if os.path.isfile(uri):
        return os.path.basename(os.path.splitext(uri)[0])

    if ' table=' in uri:
        # table="schema"."table"
        re_table_schema = re.compile(' table="([^"]*)"\\."([^"]*)"')
        r = re_table_schema.search(uri)
        if r:
            return r.groups()[0] + '.' + r.groups()[1]
        # table="table"
        re_table = re.compile(' table="([^"]*)"')
        r = re_table.search(uri)
        if r:
            return r.groups()[0]
    elif 'layername' in uri:
        regex = re.compile('(layername=)([^|]*)')
        r = regex.search(uri)
        return r.groups()[1]

    fields = uri.split('|')
    basePath = fields[0]
    fields = fields[1:]
    layerid = 0
    for f in fields:
        if f.startswith('layername='):
            return f.split('=')[1]
        if f.startswith('layerid='):
            layerid = int(f.split('=')[1])

    ds = ogr.Open(basePath)
    if not ds:
        return None

    ly = ds.GetLayer(layerid)
    if not ly:
        return None

    name = ly.GetName()
    ds = None
    return name


MEMORY_LAYER_PREFIX = 'memory:'
POSTGIS_LAYER_PREFIX = 'postgis:'
SPATIALITE_LAYER_PREFIX = 'spatialite:'

NOGEOMETRY_EXTENSIONS = [
    u'csv',
    u'dbf',
    u'ods',
    u'xlsx',
]


def createVectorWriter(destination, encoding, fields, geometryType, crs, context, options=None):
    layer = None
    sink = None

    if encoding is None:
        settings = QgsSettings()
        encoding = settings.value('/Processing/encoding', 'System', str)

    if destination.startswith(MEMORY_LAYER_PREFIX):
        uri = QgsWkbTypes.displayString(geometryType) + "?uuid=" + str(uuid.uuid4())
        if crs.isValid():
            uri += '&crs=' + crs.authid()
        fieldsdesc = []
        for f in fields:
            qgsfield = _toQgsField(f)
            fieldsdesc.append('field=%s:%s' % (qgsfield.name(),
                                               TYPE_MAP_MEMORY_LAYER.get(qgsfield.type(), "string")))
        if fieldsdesc:
            uri += '&' + '&'.join(fieldsdesc)

        layer = QgsVectorLayer(uri, destination, 'memory')
        sink = layer.dataProvider()
        context.temporaryLayerStore().addMapLayer(layer, False)
    elif destination.startswith(POSTGIS_LAYER_PREFIX):
        uri = QgsDataSourceUri(destination[len(POSTGIS_LAYER_PREFIX):])
        connInfo = uri.connectionInfo()
        (success, user, passwd) = QgsCredentials.instance().get(connInfo, None, None)
        if success:
            QgsCredentials.instance().put(connInfo, user, passwd)
        else:
            raise GeoAlgorithmExecutionException("Couldn't connect to database")
        try:
            db = postgis.GeoDB(host=uri.host(), port=int(uri.port()),
                               dbname=uri.database(), user=user, passwd=passwd)
        except postgis.DbError as e:
            raise GeoAlgorithmExecutionException(
                "Couldn't connect to database:\n%s" % e.message)

        def _runSQL(sql):
            try:
                db._exec_sql_and_commit(str(sql))
            except postgis.DbError as e:
                raise GeoAlgorithmExecutionException(
                    'Error creating output PostGIS table:\n%s' % e.message)

        fields = [_toQgsField(f) for f in fields]
        fieldsdesc = ",".join('%s %s' % (f.name(),
                                         TYPE_MAP_POSTGIS_LAYER.get(f.type(), "VARCHAR"))
                              for f in fields)

        _runSQL("CREATE TABLE %s.%s (%s)" % (uri.schema(), uri.table().lower(), fieldsdesc))
        if geometryType != QgsWkbTypes.NullGeometry:
            _runSQL("SELECT AddGeometryColumn('{schema}', '{table}', 'the_geom', {srid}, '{typmod}', 2)".format(
                table=uri.table().lower(), schema=uri.schema(), srid=crs.authid().split(":")[-1],
                typmod=QgsWkbTypes.displayString(geometryType).upper()))

        layer = QgsVectorLayer(uri.uri(), uri.table(), "postgres")
        sink = layer.dataProvider()
        context.temporaryLayerStore().addMapLayer(layer, False)
    elif destination.startswith(SPATIALITE_LAYER_PREFIX):
        uri = QgsDataSourceUri(destination[len(SPATIALITE_LAYER_PREFIX):])
        try:
            db = spatialite.GeoDB(uri=uri)
        except spatialite.DbError as e:
            raise GeoAlgorithmExecutionException(
                "Couldn't connect to database:\n%s" % e.message)

        def _runSQL(sql):
            try:
                db._exec_sql_and_commit(str(sql))
            except spatialite.DbError as e:
                raise GeoAlgorithmExecutionException(
                    'Error creating output Spatialite table:\n%s' % str(e))

        fields = [_toQgsField(f) for f in fields]
        fieldsdesc = ",".join('%s %s' % (f.name(),
                                         TYPE_MAP_SPATIALITE_LAYER.get(f.type(), "VARCHAR"))
                              for f in fields)

        _runSQL("DROP TABLE IF EXISTS %s" % uri.table().lower())
        _runSQL("CREATE TABLE %s (%s)" % (uri.table().lower(), fieldsdesc))
        if geometryType != QgsWkbTypes.NullGeometry:
            _runSQL("SELECT AddGeometryColumn('{table}', 'the_geom', {srid}, '{typmod}', 2)".format(
                table=uri.table().lower(), srid=crs.authid().split(":")[-1],
                typmod=QgsWkbTypes.displayString(geometryType).upper()))

        layer = QgsVectorLayer(uri.uri(), uri.table(), "spatialite")
        sink = layer.dataProvider()
        context.temporaryLayerStore().addMapLayer(layer, False)
    else:
        formats = QgsVectorFileWriter.supportedFiltersAndFormats()
        OGRCodes = {}
        for (key, value) in list(formats.items()):
            extension = str(key)
            extension = extension[extension.find('*.') + 2:]
            extension = extension[:extension.find(' ')]
            OGRCodes[extension] = value
        OGRCodes['dbf'] = "DBF file"

        extension = destination[destination.rfind('.') + 1:]

        if extension not in OGRCodes:
            extension = 'shp'
            destination = destination + '.shp'

        if geometryType == QgsWkbTypes.NoGeometry:
            if extension == 'shp':
                extension = 'dbf'
                destination = destination[:destination.rfind('.')] + '.dbf'
            if extension not in NOGEOMETRY_EXTENSIONS:
                raise GeoAlgorithmExecutionException(
                    "Unsupported format for tables with no geometry")

        qgsfields = QgsFields()
        for field in fields:
            qgsfields.append(_toQgsField(field))

        # use default dataset/layer options
        dataset_options = QgsVectorFileWriter.defaultDatasetOptions(OGRCodes[extension])
        layer_options = QgsVectorFileWriter.defaultLayerOptions(OGRCodes[extension])

        sink = QgsVectorFileWriter(destination, encoding,
                                   qgsfields, geometryType, crs, OGRCodes[extension],
                                   dataset_options, layer_options)
    return sink, destination, layer


class TableWriter(object):

    def __init__(self, fileName, encoding, fields):
        self.fileName = fileName
        if not self.fileName.lower().endswith('csv'):
            self.fileName += '.csv'

        self.encoding = encoding
        if self.encoding is None or encoding == 'System':
            self.encoding = 'utf-8'

        with open(self.fileName, 'w', newline='', encoding=self.encoding) as f:
            self.writer = csv.writer(f)
            if len(fields) != 0:
                self.writer.writerow(fields)

    def addRecord(self, values):
        with open(self.fileName, 'a', newline='', encoding=self.encoding) as f:
            self.writer = csv.writer(f)
            self.writer.writerow(values)

    def addRecords(self, records):
        with open(self.fileName, 'a', newline='', encoding=self.encoding) as f:
            self.writer = csv.writer(f)
            self.writer.writerows(records)
