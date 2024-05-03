# -*- coding: utf-8 -*-
""" Remove small holes """
from shapely.geometry import MultiPolygon, Polygon


def remove_hole(multipoly):
    """Remove small holes (surface < 100 m²)

    Args:
        - multipoly (GeoJSON): Hydro Mask geometry

    Returns:
        GeoJSON: Hydro Mask geometry without holes (< 100 m²)
    """
    list_parts = []
    eps = 100

    for polygon in multipoly.geoms:
        list_interiors = []

        for interior in polygon.interiors:
            p = Polygon(interior)

            if p.area > eps:
                list_interiors.append(interior)

        temp_pol = Polygon(polygon.exterior.coords, holes=list_interiors)
        list_parts.append(temp_pol)

    new_multipolygon = MultiPolygon(list_parts)

    return new_multipolygon
