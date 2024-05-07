# -*- coding: utf-8 -*-
""" Remove small holes """
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union


def close_holes(polygon, min_hole_area):
    """Remove small holes (surface < 100 m²)

    Args:
        - polygon (GeoJSON): Hydro Mask geometry
        - minhole_area (int): close holes in Mask Hydro : keep only holes with area bigger
                              than min_hole_area (> 100 m² by default)

    Returns:
        GeoJSON: Hydro Mask geometry without holes (< 100 m²)
    """
    # Exterior Hydro Mask
    exterior_contours = [exterior for exterior in polygon.exterior]
    # Create polygons from each exterior contour without holes
    polygons = [Polygon(ring) for ring in exterior_contours]
    # Merge all polygons into a single encompassing shape
    unified_shape = unary_union(polygons)

    # Interior Hydro Mask
    interiors_to_keep = [
        interior for poly in polygon for interior in poly.interiors if Polygon(interior).area >= min_hole_area
    ]
    interior_holes_filter = [[pt for pt in inner.coords] for inner in interiors_to_keep]

    # Determine the appropriate Polygon to use based on the type of unified_shape
    if isinstance(unified_shape, Polygon):
        final_polygon = Polygon(
            shell=unified_shape.exterior, holes=interior_holes_filter if interior_holes_filter else []
        )
    elif isinstance(unified_shape, MultiPolygon):
        # Explicitly find the largest polygon by area
        largest_polygon = max(unified_shape.geoms, key=lambda p: p.area)
        final_polygon = Polygon(
            shell=largest_polygon.exterior, holes=interior_holes_filter if interior_holes_filter else []
        )
    else:
        raise ValueError("The unified shape is neither a Polygon nor a MultiPolygon. Please handle accordingly.")

    return final_polygon
