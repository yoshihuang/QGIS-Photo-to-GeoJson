def classFactory(iface):
    from .photo_to_geojson import PhotoToGeoJSONPlugin
    return PhotoToGeoJSONPlugin(iface)