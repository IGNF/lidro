from itertools import product

import geopandas as gpd
from geopandas.geodataframe import GeoDataFrame
import pandas as pd
import numpy as np

from shapely import LineString
from shapely.geometry import CAP_STYLE
from shapely.validation import make_valid
from shapely.ops import voronoi_diagram, linemerge

import logging

MASK_GEOJSON_1 = "/home/MDaab/data/squelette_test/MaskHydro_merge 1.geojson"
MASK_GEOJSON_2 = "/home/MDaab/data/squelette_test/ecoulement_brut_pm2.geojson"
MASK_GEOJSON_3 = "/home/MDaab/data/squelette_test/ecoulement_brut_pm3.geojson"
MASK_GEOJSON_4 = "/home/MDaab/data/squelette_test/ecoulement_brut_lg1.geojson"

MIDDLE_FILE = "squelette_filtrer.geojson"
SAVE_FILE = "squelette_hydrographique.geojson"
WATER_MIN_SIZE = 20



# def simplify_geometry(polygon):
#     """ simplifier certaines formes pour faciliter les calculs
#     """
#     ## Buffer positif de la moitié de la taille de la résolution du masque HYDRO (1m de résolution)
#     _geom = polygon.buffer(1, cap_style=CAP_STYLE.square)
#     geom = _geom.buffer(-0.5, cap_style=CAP_STYLE.square)
#     return geom


def fix_invalid_geometry(geometry):
    """ Fixer les géoémtries invalides
    """
    if not geometry.is_valid:
        return make_valid(geometry)
    else:
        return geometry


def check_geometry(initial_gdf):
    """Vérifier la topologie des polygones
    """
    # Obtenir des géométries simples
    gdf_simple = initial_gdf.explode(ignore_index=True)  # Le paramètre ignore_index est utilisé pour obtenir une incrémentation d'index mise à jour.
    # Supprimer les géométries en double si il y en a
    gdf_without_duplicates = gdf_simple.drop_duplicates(ignore_index=True)
    # Identifier les géométries invalides et ne garder que les géométries valides
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

def remove_extra_lines(lines:GeoDataFrame):

    #  prepare a vertice dict, containing all the lines joining on a same vertex
    vertices_dict = {}
    for index in lines.index :
        line = lines.iloc[index]['geometry']
        point_a, point_b = line.boundary.geoms[0], line.boundary.geoms[1]
        try :
            vertices_dict[point_a].append(line)     # ATTENTION (les points peuvent peut-être être légèrement différents)
        except KeyError:
            vertices_dict[point_a] = [line]
        try :
            vertices_dict[point_b].append(line)
        except KeyError:
            vertices_dict[point_b] = [line]

    # get all the lines to remove from the list
    lines_to_remove = []
    for vertex, line_list in vertices_dict.items():
        # print(len(line_list))
        if len(line_list) == 1 :
            continue

        # if len(line_list) != 1, then it's probably 3 ; Can't be 2 because of the previous merge, very unlikely to be 4+
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
            # if vertex == line_to_keep.boundary.geoms[0]:
            #     vector_to_keep = np.array((line_to_keep.boundary.geoms[1] - vertex).coords[0])
            # else:
            #     vector_to_keep = np.array((line_to_keep.boundary.geoms[0] - vertex).coords[0])

            # if vertex == line_that_can_be_removed.boundary.geoms[0]:
            #     vector_to_remove = np.array((line_that_can_be_removed.boundary.geoms[1] - vertex).coords[0])
            # else:
            #     vector_to_remove = np.array((line_that_can_be_removed.boundary.geoms[0] - vertex).coords[0])

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
    return lines[~lines['geometry'].isin(lines_to_remove)]

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
    # Vérfier quye la Geometrie n'est pas vide
    if not mask_hydro['geometry'].dtype == 'geometry':
        return
    
    ###### Calculer le diagram de Voronoi ######
    # "Segmentize" le masque HYDRO :
    # Renvoie une geometry/geography modifiée dont aucun segment n'est plus long que max_segment_length.
    segmentize_geom = (mask_hydro['geometry'].unary_union).segmentize(max_segment_length=2)
    # Calculer le diagrame de Voronoi, et ne renvoyer que les polylignes
    regions = voronoi_diagram(segmentize_geom, envelope=segmentize_geom, tolerance=0.0, edges=True)

    ##### Filtrer les lignes de Voronoi en excluant celles à l'extérieur du masques ######
    geometry = gpd.GeoSeries(regions.geoms, crs=crs).explode(index_parts=False)
    df = gpd.GeoDataFrame(geometry=geometry, crs=crs)
    lines_filter = df.sjoin(mask_hydro, predicate='within')  # Opération spatiale "Within"
    # Enregistrer le diagram de Voronoi (Squelette)
    lines_filter = lines_filter.reset_index(drop=True)  # Réinitialiser l'index
    lines_filter = lines_filter.drop(columns=['index_right'])  # Supprimer la colonne 'index_right'

    return gpd.GeoDataFrame(lines_filter, crs=crs)


def run(mask_hydro, crs):
    """Calculer le squelette hydrographique

    Args:
        - mask_hydro (GeoJSON) : Mask Hydrographic (Polygone)
        - crs (str): code EPSG
    """
    gdf = check_geometry(mask_hydro)  # Vérifier et corriger les géométries non valides
    ### Diagram Voronoi ###
    voronoi_lines = create_voronoi_lines(gdf, crs)

    ### Mettre une occurence au squelette pour obtenir un tronçon hydrographique ###
    # Fusionner tous les LINESTRING en un seul objet MultiLineString
    lines = line_merge(voronoi_lines)
    old_number_of_lines = len(lines)
    while True:
        lines = remove_extra_lines(lines)
        lines = line_merge(lines)

        if len(lines) != old_number_of_lines:
            old_number_of_lines = len(lines)
        else:
            break

    # pruned_lines = remove_extra_lines(lines)
    # merged_pruned_lines = line_merge(pruned_lines)
    # super_pruned_lines = remove_extra_lines(merged_pruned_lines)
    gpd.GeoDataFrame(lines, crs=crs).to_file("test_5.geojson", driver='GeoJSON')




    # gdf = filter_branch(lines, crs)

    # gdf.to_file(MIDDLE_FILE, driver='GeoJSON')  # sauvegarder le résultat
    # ## Filtrer les occurences ##
    # # Filtrer les lignes pour ne conserver que celles dont les "occurences > 1"
    # filtered_gdf = gdf.query('occurence_min > 1')
    # filtered_gdf.drop(columns=['occurence_min'])
    # # Merge lines pour des occurences > 1
    # lines_occurences = line_merge(filtered_gdf)
    # ## 2e calcul des occurences filtrées ##
    # gdf2 = filter_branch(lines_occurences, crs)
    # ## Filtrer les occurences ##
    # # Filtrer les lignes pour ne conserver que celles dont les "occurences > 1"
    # filtered_gdf2 = gdf2.query('occurence_min > 1')
    # # print(len(filtered_gdf)*0.1)
    # # print(len(filtered_gdf2))
    # # Eviter les squelettes discontinues
    # if len(filtered_gdf2) < len(filtered_gdf)*0.1:
    #     gdf2.to_file(SAVE_FILE, driver='GeoJSON')  # sauvegarder le résultat
    # else:
    #     filtered_gdf2.to_file(SAVE_FILE, driver='GeoJSON')  # sauvegarder le résultat


if __name__ == "__main__":
    # Example usage
    # Calcule du squelette
    mask_hydro = gpd.read_file(MASK_GEOJSON_1)
    crs = mask_hydro.crs  # Load a crs from input
    # Simplifier geometrie
    # buffer_geom = mask_hydro.apply(simplify_geometry) ## Appliquer un buffer
    simplify_geom = mask_hydro.simplify(tolerance=2, preserve_topology=True)  # simplifier les géométries avec Douglas-Peucker
    df = gpd.GeoDataFrame(geometry=simplify_geom, crs=crs)
    # Squelette
    run(df, crs)
