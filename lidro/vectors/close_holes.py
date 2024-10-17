# -*- coding: utf-8 -*-
""" Remove small holes """
from shapely.geometry import Polygon


def close_holes(polygon: Polygon, min_hole_area=None) -> Polygon:
    """Remove small holes (surface < 100 m²)

    Args:
        - polygon (Polygon): Hydro Mask geometry
        - minhole_area (int): close holes in Mask Hydro : keep only holes with area bigger
                              than min_hole_area (> 100 m² by default)

    Returns:
        Polygon: Hydro Mask geometry without holes (< 100 m²)
    """
    # Interior Hydro Mask
    if min_hole_area is not None:
        interiors_to_keep = [interior for interior in polygon.interiors if Polygon(interior).area >= min_hole_area]
        interior_holes_filter = [[pt for pt in inner.coords] for inner in interiors_to_keep]
    else:
        interior_holes_filter = []

    # Determine the appropriate Polygon to use based on the type of unified_shape
    final_polygon = Polygon(shell=polygon.exterior, holes=interior_holes_filter)

    return final_polygon
