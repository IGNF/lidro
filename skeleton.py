from itertools import product
from typing import Dict, List, Tuple

import geopandas as gpd
from geopandas.geodataframe import GeoDataFrame
import pandas as pd
import numpy as np

from shapely import LineString, Point, geometry
from shapely.geometry import CAP_STYLE
from shapely.validation import make_valid
from shapely.ops import voronoi_diagram, linemerge, split, snap
import logging

MASK_GEOJSON_1 = "/home/MDaab/data/squelette_test/MaskHydro_merge 1.geojson"
MASK_GEOJSON_2 = "/home/MDaab/data/squelette_test/ecoulement_brut_pm2.geojson"
MASK_GEOJSON_3 = "/home/MDaab/data/squelette_test/ecoulement_brut_pm3.geojson"
MASK_GEOJSON_4 = "/home/MDaab/data/squelette_test/ecoulement_brut_lg1.geojson"

MIDDLE_FILE = "squelette_filtrer.geojson"
SAVE_FILE = "squelette_hydrographique.geojson"
WATER_MIN_SIZE = 20
BRIDGE_MAX_WIDTH = 50
VORONOI_MAX_LENGTH = 2


def fix_invalid_geometry(geometry):
    """ Fixer les géométries invalides
    """
    if not geometry.is_valid:
        return make_valid(geometry)
    else:
        return geometry


def check_geometry(initial_gdf):
    """garanty polygons' validity
    """
    # create simple geometry 
    gdf_simple = initial_gdf.explode(ignore_index=True)  # ignore_index makes the resulting index multi-indexed
    gdf_without_duplicates = gdf_simple.drop_duplicates(ignore_index=True)
    # remove invalid polygons
    gdf_valid = gdf_without_duplicates.copy()
    gdf_valid.geometry = gdf_valid.geometry.apply(
        lambda geom: fix_invalid_geometry(geom)
    )
    return gdf_valid


def filter_branch(df, crs):
    """Filter branches from voronoi_lines to extract hydrographic section

    Args:
        -df (GeoDataframe) : Lignes de Voronoi fusionnées comprises à l'intérieur du masque hydrographique
        - crs (str): code EPSG

    Returns :
        out (GeoDataframe) : Lignes de Voronoi comprises à l'intérieur du masque hydrographique avec leurs occurences
    """
    ### Étape 1 : Obtenez les limites de chaque ligne
    boundaries = df.boundary
    # df.reset_index()
    df["id"] = df.index

    ### Étape 2 : Explosez les limites pour avoir une ligne par limite
    exploded_boundaries = boundaries.explode(index_parts=False, ignore_index=False)
    # Créez un DataFrame à partir des limites explosées avec une colonne 'geometry'
    boundary_df = gpd.GeoDataFrame(geometry=exploded_boundaries)

    ### Étape 3 : Utilisez groupby pour compter le nombre d'occurrences de chaque points
    boundary_df["id"] = boundary_df.index
    boundary_df["wkt"] = boundary_df["geometry"].to_wkt()
    occurences_df = boundary_df.groupby(["geometry"], dropna=True, as_index=False).agg({'id': [lambda x: x.iloc[0], 'count']})
    occurences_df.columns = ['geometry', 'id', 'occurences']

    ### Étape 4 : Obtenir les occurences de chaque lignes de Voronoi
    # Merger les points par occurences avec leur geometry
    points_merge = pd.merge(boundary_df, occurences_df, on='geometry').drop(columns=['wkt', 'id_y']).drop_duplicates()
    points_merge.columns = ['geometry', 'id', 'occurences']
    points_merge = gpd.GeoDataFrame(points_merge, crs=crs)
    # Intersecter les points avec les lignes de Voronoi
    points_intersect_lines = df.sjoin(points_merge, predicate='intersects')
    # Grouper les lignes par index "id_left" et calculer les occurences "minimum" et "maximum"
    out = points_intersect_lines.groupby('id_left', dropna=True).agg({'occurences': ['min'], 'geometry': [lambda x: x.iloc[0]]})
    out.columns = ['occurence_min', 'geometry']
    out = gpd.GeoDataFrame(out, crs=crs)

    return out


def can_line_be_removed(line, vertices_dict):
    if line.length > WATER_MIN_SIZE:
        return False

    point_a, point_b = line.boundary.geoms[0], line.boundary.geoms[1]
    if len(vertices_dict[point_a]) > 1 and len(vertices_dict[point_b]) > 1:
        return False
    return True

def get_vertices_dict(gdf_lines:GeoDataFrame)->Dict[Point, List[LineString]]:
    """
    get a dictionary of vertices listing all the lines having a specific vertex as one of its extremities
    Args:
        - gdf_lines:geodataframe containing a list of lines
    return:
        - a dict with the vertices are the keys and the values are lists of lines
    """
    #  prepare a vertice dict, containing all the lines connected on a same vertex
    vertices_dict = {}
    for index in gdf_lines.index :
        line = gdf_lines.iloc[index]['geometry']
        point_a, point_b = line.boundary.geoms[0], line.boundary.geoms[1]
        try :
            vertices_dict[point_a].append(line)
        except KeyError:
            vertices_dict[point_a] = [line]
        try :
            vertices_dict[point_b].append(line)
        except KeyError:
            vertices_dict[point_b] = [line]
    return vertices_dict

def remove_extra_lines(gdf_lines:GeoDataFrame)->GeoDataFrame:
    vertices_dict = get_vertices_dict(gdf_lines)

    lines_to_remove = []
    for vertex, line_list in vertices_dict.items():
        if len(line_list) == 1 :
            continue

        # if len(line_list) !is not 1, then it's probably 3; Can't be 2 because of the previous merge, very unlikely to be 4+
        lines_to_keep = []
        lines_that_can_be_removed = []
        for line in line_list:
            if can_line_be_removed(line, vertices_dict):
                lines_that_can_be_removed.append(line)
            else:
                lines_to_keep.append(line)

        # if no line can be removed, we continue
        if not lines_that_can_be_removed:
            continue

        # strange case where 3+ lines are together, but isolated from the rest of the world
        if len(lines_to_keep) == 0:
            lines_to_remove += lines_that_can_be_removed
            continue

        # there is only 1 line that can be removed and 2+ to be kept, so we remove it
        if len(lines_that_can_be_removed) == 1:
            lines_to_remove.append(lines_that_can_be_removed[0])
            continue

        # at least 2 lines can be removed, we will keep the one forming the straightest line with
        # a line to keep, we assume it's the most likely to "continue" the river
        min_dot_product = 1
        line_that_should_not_be_removed = None
        for line_to_keep, line_that_can_be_removed in product(lines_to_keep, lines_that_can_be_removed):
            if vertex == line_to_keep.boundary.geoms[0]:
                vector_to_keep = np.array(line_to_keep.boundary.geoms[1].coords[0]) - np.array(vertex.coords[0])
            else:
                vector_to_keep = np.array(line_to_keep.boundary.geoms[0].coords[0]) - np.array(vertex.coords[0])

            if vertex == line_that_can_be_removed.boundary.geoms[0]:
                vector_to_remove = np.array(line_that_can_be_removed.boundary.geoms[1].coords[0]) - np.array(vertex.coords[0])
            else:
                vector_to_remove = np.array(line_that_can_be_removed.boundary.geoms[0].coords[0]) - np.array(vertex.coords[0])            

            length_to_keep = np.linalg.norm(vector_to_keep)
            length_to_remove = np.linalg.norm(vector_to_remove)
            if not length_to_keep or not length_to_remove:  # length = 0, probably won't happen
                continue

            vector_to_keep = vector_to_keep / length_to_keep
            vector_to_remove = vector_to_remove / length_to_remove
            dot_product = np.dot(vector_to_keep, vector_to_remove)
            #  the smallest dot product (which should be negative) is the straightest couple of lines
            if dot_product < min_dot_product:
                min_dot_product = dot_product
                line_that_should_not_be_removed = line_that_can_be_removed

        lines_that_can_be_removed.remove(line_that_should_not_be_removed)
        lines_to_remove += lines_that_can_be_removed

    # return the lines without the lines to remove
    return gdf_lines[~gdf_lines['geometry'].isin(lines_to_remove)]

def line_merge(voronoi_lines):
    """Fusionner tous les LINESTRING en un seul objet MultiLineString

    Args:
        - voronoi_lines (GeoDataframe) :  Lignes de Voronoi comprises à l'intérieur du masque hydrographique

    Returns:
        lines (GeoDataframe): Lignes de Voronoi fusionnées comprises à l'intérieur du masque hydrographique

    """
    # Fusionner tous les LINESTRING en un seul objet MultiLineString
    merged_line = voronoi_lines.geometry.unary_union
    # Appliquer un algo de fusion des lignes (ex. "ST_LineMerge") sur l'objet MultiLineString
    merged_line = linemerge(merged_line)

    # turn multipart geometries into multiple single geometries
    geometry = gpd.GeoSeries(merged_line.geoms, crs=crs).explode(index_parts=False)  
    lines = gpd.GeoDataFrame(geometry=geometry, crs=crs)

    return lines


def create_voronoi_lines(mask_hydro, crs):
    """ Créer les lignes de Voronoi

    Args:
        -mask_hydro (GeoJSON) : Mask Hydrographic (Polygone)
        - crs (str): code EPSG

    Returns :
        out lines (GeoDataframe) : Lignes de Voronoi comprises à l'intérieur du masque hydrographique
    """
    # we don't work on an empty geometry
    if not mask_hydro['geometry'].dtype == 'geometry':
        return

    # divide geometry into segments no longer than max_segment_length
    segmentize_geom = (mask_hydro['geometry'].unary_union).segmentize(max_segment_length=VORONOI_MAX_LENGTH)
    # Create the voronoi diagram and only keep polygon
    regions = voronoi_diagram(segmentize_geom, envelope=segmentize_geom, tolerance=0.0, edges=True)

    ##### Filtrer les lignes de Voronoi en excluant celles à l'extérieur du masques ######
    geometry = gpd.GeoSeries(regions.geoms, crs=crs).explode(index_parts=False)
    df = gpd.GeoDataFrame(geometry=geometry, crs=crs)
    lines_filter = df.sjoin(mask_hydro, predicate='within')  # Opération spatiale "Within"
    # Enregistrer le diagram de Voronoi (Squelette)
    lines_filter = lines_filter.reset_index(drop=True)  # Réinitialiser l'index
    lines_filter = lines_filter.drop(columns=['index_right'])  # Supprimer la colonne 'index_right'

    return gpd.GeoDataFrame(lines_filter, crs=crs)

def get_prior_point(vertex, line) -> Tuple[float, float]:
    """ return the point right before an extremity vertex in a line 
    """
    if vertex == line.boundary.geoms[0]:
        prior_point = line.coords[2]
    else:
        prior_point = line.coords[-2]
    return prior_point

def connect_extremities(gdf_lines:GeoDataFrame)->GeoDataFrame:
    """
    connect extremities of rivers, as we assume they are disconnected because of bridges
    Args:
        - gdf_lines: geodataframe containing a list of lines
    return:
        The same geodataframe with connection between extremities
    """
    # garanty that all lines have at least 3 segments, because the connexion is not
    # done on the last point, but the previous one. Therefore we need enough points
    for index in gdf_lines.index :
        line = gdf_lines.iloc[index]['geometry']
        if len(line.coords) < 4: # 3 segments, so 4 points
            gdf_lines.loc[index] = line.segmentize(line.length/3)

    vertices_dict = get_vertices_dict(gdf_lines)
    # we remove all vertices that are not extremities (an extremity is connected to only one line)
    keys_to_remove = []
    for vertex, line_list in vertices_dict.items():
        if len(line_list) != 1:
            keys_to_remove.append(vertex)
    for vertex in keys_to_remove:
        vertices_dict.pop(vertex, None)

    best_candidate = {}
    for vertex, [line] in vertices_dict.items():
        prior_point = get_prior_point(vertex, line)

        # get the perpendicular line passing throught vertex, equation ax + by + c = 0
        a, b = vertex.coords[0][0] - prior_point[0], vertex.coords[0][1] - prior_point[1]
        c = - a * vertex.coords[0][0] - b * vertex.coords[0][1]

        # make sure the prior_point is below the line (if above, we multiply the equation by -1 to change it)
        if not a * prior_point[0] + b * prior_point[1] + c <= 0:
            a, b, c = -a, -b, -c

        # search best vertex candidate to join this vertex i.e:
        # the closest, not too far, vertex above the perpendicular line (to be "in front" of the river)
        for  other_vertex, [other_line] in vertices_dict.items():
            if other_vertex == vertex:
                continue
            # have to be above the perpendicular line 
            if  a * other_vertex.coords[0][0] + b * other_vertex.coords[0][1] + c <= 0:
                continue
            # should not be too far:
            squared_distance = (vertex.coords[0][0] - other_vertex.coords[0][0])**2 + (vertex.coords[0][1] - other_vertex.coords[0][1])**2
            if  squared_distance > BRIDGE_MAX_WIDTH**2:
                continue
            other_prior_point = get_prior_point(other_vertex, other_line)
            best_candidate[prior_point] = other_prior_point

    already_done_prior_points= []
    # if 2 prior_points have each other as best candidate, we create a line between them
    for prior_point, other_prior_point in best_candidate.items():
        if best_candidate[other_prior_point] == prior_point and other_prior_point not in already_done_prior_points:
            already_done_prior_points.append(prior_point)
            gdf_lines.loc[len(gdf_lines)] = [LineString([prior_point, other_prior_point])]
    return gdf_lines

def split_into_basic_segments(gdf_lines:GeoDataFrame)->GeoDataFrame:
    def split_line_by_point(line, point, tolerance: float=1.0e-12):
        return split(snap(line, point, tolerance), point)
    result = (
        gdf_lines
        .assign(geometry=gdf_lines.apply(
            lambda x: split_line_by_point(
                x.geometry, 
                geometry.Point(x.geometry.coords[1])
            ), axis=1
        ))
        .explode()
        .reset_index(drop=True)
    )
    return result


def run(mask_hydro, crs):
    """Calculer le squelette hydrographique

    Args:
        - mask_hydro (GeoJSON) : Mask Hydrographic (Polygone)
        - crs (str): code EPSG
    """
    gdf = check_geometry(mask_hydro)  # Vérifier et corriger les géométries non valides
    ### Voronoi Diagram ###
    voronoi_lines = create_voronoi_lines(gdf, crs)

    # merge all lines that can be merged without doubt (when only 2 lines are connected)
    # remove lines we don't want, then repeat until it doesn't change anymore
    gdf_lines = line_merge(voronoi_lines)
    old_number_of_lines = len(gdf_lines)
    while True:
        gdf_lines = remove_extra_lines(gdf_lines)
        gdf_lines = line_merge(gdf_lines)

        if len(gdf_lines) != old_number_of_lines:
            old_number_of_lines = len(gdf_lines)
        else:
            break

    gdf_lines = connect_extremities(gdf_lines)
    gdf_lines = gdf_lines.set_crs(crs, allow_override=True)  # the lines added to connect the extremities have no crs

    # connecting extremities creates lines we don't want (because of where we connect the extremities),
    # we remove them one last time
    gdf_lines = remove_extra_lines(gdf_lines)
    # gdf_lines = line_merge(gdf_lines)
    
    gpd.GeoDataFrame(gdf_lines, crs=crs).to_file("test_7.geojson", driver='GeoJSON')

if __name__ == "__main__":
    # Example usage
    # Calcule du squelette
    mask_hydro = gpd.read_file(MASK_GEOJSON_1)
    crs = mask_hydro.crs  # Load a crs from input
    # Simplifier geometrie
    # buffer_geom = mask_hydro.apply(simplify_geometry) ## Appliquer un buffer
    simplify_geom = mask_hydro.simplify(tolerance=2, preserve_topology=True)  # simplifier les géométries avec Douglas-Peucker
    df = gpd.GeoDataFrame(geometry=simplify_geom, crs=crs)
    df.to_file("test_0.geojson", driver='GeoJSON')
    # Squelette
    # run(df, crs)
    run(mask_hydro, crs)
