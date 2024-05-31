from itertools import product
from typing import Dict, List, Tuple

import geopandas as gpd
from geopandas.geodataframe import GeoDataFrame
import pandas as pd
import numpy as np
from math import sqrt

from shapely import LineString, Point, geometry, distance
from shapely.geometry import CAP_STYLE, Polygon, MultiPoint, Point
from shapely.validation import make_valid
from shapely.ops import voronoi_diagram, linemerge, split, snap, triangulate
import logging

MASK_GEOJSON_1 = "/home/MDaab/data/squelette_test/MaskHydro_merge 1.geojson"
MASK_GEOJSON_2 = "/home/MDaab/data/squelette_test/ecoulement_brut_pm2.geojson"
MASK_GEOJSON_3 = "/home/MDaab/data/squelette_test/ecoulement_brut_pm3.geojson"
MASK_GEOJSON_4 = "/home/MDaab/data/squelette_test/ecoulement_brut_lg1.geojson"
MASK_GEOJSON_5 = "/home/MDaab/data/squelette_test/Mask_Hydro_without_vegetation.geojson"

MIDDLE_FILE = "squelette_filtrer.geojson"
SAVE_FILE = "squelette_hydrographique.geojson"
WATER_MIN_SIZE = 20
BRIDGE_MAX_WIDTH = 50
VORONOI_MAX_LENGTH = 2

# class Blob:
#     def __init__(self, line:LineString):
#         data = {'geometry':[], 'extremity_0':[], 'extremity_1':[]}
#         self.gdf_lines = GeoDataFrame(data = data)
#         self.extremities_set = set()
#         self.add_line(line)

#     def add_line(self, line:LineString):
#         extremity_0 = line.boundary.geoms[0]
#         extremity_1 = line.boundary.geoms[1]
#         new_data = {'geometry':[line], 'extremity_0':[extremity_0], 'extremity_1':[extremity_1]}
#         gdf_line = GeoDataFrame(data = new_data)
#         self.gdf_lines = pd.concat([self.gdf_lines, gdf_line])
#         self.extremities_set.add(extremity_0)
#         self.extremities_set.add(extremity_1)

#     def is_line_connected(self, line:LineString) -> bool:
#         extremity_0 = line.boundary.geoms[0]
#         extremity_1 = line.boundary.geoms[1]
#         if extremity_0 in self.extremities_set or extremity_1 in self.extremities_set:
#             return True
#         return False

#     def is_blob_connected(self, blob:'Blob') -> bool:
#         if self.extremities_set.intersection(blob.extremities_set):
#             return True
#         return False

#     def add_blob(self, blob:'Blob'):
#         self.gdf_lines = pd.concat([self.gdf_lines, blob.gdf_lines])
#         self.extremities_set = self.extremities_set.union(blob.extremities_set)

#     def save(self, file_name:str):
#         self.gdf_lines.to_file(file_name + ".geojson", driver='GeoJSON')

# def create_blobs(gdf_lines:GeoDataFrame)->List[Blob]:
#     """
#         Args:
#         -gdf_lines (GeoDataframe) : a list of linestring that are not connected by intermediate points
#     """
#     blobs_list = []
#     for _, row in gdf_lines.iterrows():
#         line = row['geometry']
#         # line_connected = False
#         # # search if the lines is connected to a blob
#         # for blob in blobs_list:
#         #     if blob.is_line_connected(line):
#         #         blob.add_line(line)
#         #         line_connected = True
#         #         break
#         # # if the line is not connected ot a blob, it creates its own blob
#         # if not line_connected:
#         blobs_list.append(Blob(line))

#     # joint all connected blobs together
#     disjoint_blobs_list = []
#     while blobs_list:
#         blob = blobs_list.pop(len(blobs_list) - 1)
#         eaten = False
#         for gluton_blob in blobs_list:  # gluton becuase it will "eat" the other blob
#             if gluton_blob.is_blob_connected(blob):
#                 gluton_blob.add_blob(blob)
#                 eaten = True
#                 break
#         if not eaten:
#             disjoint_blobs_list.append(blob)

#     return disjoint_blobs_list

class Branch:
    def __init__(self, )

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
        if line.is_ring:   # it's a loop : no extremity
            continue 

        point_a, point_b = line.boundary.geoms[0], line.boundary.geoms[1]
        # point_a, point_b = line.coords[0], line.coords[-1]
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

def connect_extremities(gdf_lines:GeoDataFrame, crs)->GeoDataFrame:
    """
    connect extremities of rivers, as we assume they are disconnected because of bridges
    Args:
        - gdf_lines: geodataframe containing a list of lines
    return:
        The same geodataframe with connection between extremities
    """

    # garanty that all lines have at least 3 segments, because the connexion is not
    # done on the last point, but the previous one. Therefore we need enough points
    new_lines = []
    for index, row in gdf_lines.iterrows():
        line = row['geometry']
        if len(line.coords) < 4: # 3 segments, so 4 points
            line = line.segmentize(line.length/3)
        new_lines.append(line)
    gdf_lines = gpd.GeoDataFrame(geometry=new_lines).set_crs(crs, allow_override=True)

    # for index, row in gdf_lines.iterrows():
    #     line = row['geometry']
    #     if len(line.coords) < 4: # 3 segments, so 4 points
    #         row = line.segmentize(line.length/3)

    vertices_dict = get_vertices_dict(gdf_lines)
    # we remove all vertices that are not extremities (an extremity is connected to only one line)
    keys_to_remove = []
    for vertex, line_list in vertices_dict.items():
        if len(line_list) != 1:
            keys_to_remove.append(vertex)
    for vertex in keys_to_remove:
        vertices_dict.pop(vertex, None)

    ###
    # WARNING !!! VISUALIZATION OF EXTREMITIES, TO REMOVE
    geom = [vertex for vertex in vertices_dict.keys()]
    test = gpd.GeoDataFrame(geometry=geom).set_crs(crs, allow_override=True)
    test.to_file("test_extremities.geojson", driver='GeoJSON')
    ###

    ###
    # WARNING !!! VISUALIZATION OF PRIOR POINTS, TO REMOVE
    geom = [Point(*get_prior_point(vertex, line[0])) for vertex, line in vertices_dict.items()]
    test = gpd.GeoDataFrame(geometry=geom).set_crs(crs, allow_override=True)
    test.to_file("test_prior_points.geojson", driver='GeoJSON')
    ###

    new_lines = []
    # create a dataframe from the vertices (to make calculation faster)
    data = {'x':[vertex.x for vertex in vertices_dict],
            'y':[vertex.y for vertex in vertices_dict],
            'vertex': vertices_dict.keys(),
            'line': [lines[0] for lines in vertices_dict.values()]}
    df_vertex = pd.DataFrame(data=data)

    best_prior_points_to_connect = []
    for vertex_1, [line_1] in vertices_dict.items():
        prior_point_1 = get_prior_point(vertex_1, line_1)

        best_dot_value = 0
        best_prior_point = None
        best_candidate = None

        # get all close enough vertices
        df_vertex['square_distance'] = (df_vertex['x'] - vertex_1.x)**2 + (df_vertex['y'] - vertex_1.y)**2
        df_close_enough = df_vertex[df_vertex['square_distance'] < BRIDGE_MAX_WIDTH**2]
        for index, extremity_row in df_close_enough.iterrows():

            # we can connect only vertex with a previous one in the list
            # if we allow the connection also with next vertices, the connection would be made twice 
            vertex_2 = extremity_row['vertex']
            if vertex_2 == vertex_1:
                break

            prior_point_2 = get_prior_point(vertex_2, extremity_row['line'])
            x_1 = prior_point_1[0] - vertex_1.x
            y_1 = prior_point_1[1] - vertex_1.y
            x_2 = prior_point_2[0] - vertex_2.x
            y_2 = prior_point_2[1] - vertex_2.y

            length_1 = sqrt(x_1**2 + y_1**2)
            length_2 = sqrt(x_2**2 + y_2**2)
            if not length_1 or not length_2:    # a vector is null
                continue

            normalized_dot_product = x_1 * x_2 + y_1 * y_2 / (length_1 * length_2)
            # if they are anticolinear enough, we keep it
            if normalized_dot_product <  best_dot_value :
                best_dot_value = normalized_dot_product
                best_prior_point = prior_point_2
                best_candidate = index

        if best_candidate:
            best_prior_points_to_connect.append([prior_point_1, best_prior_point])

    # search where both prior points are the best for each other
    # for index, prior_points_pair in enumerate(best_prior_points_to_connect[:-1]):
    #     for opposite_prior_points_pair in best_prior_points_to_connect[index + 1:]:
    for index, prior_points_pair in enumerate(best_prior_points_to_connect):
        for opposite_prior_points_pair in best_prior_points_to_connect:
            if prior_points_pair[0] == opposite_prior_points_pair[1] \
                and prior_points_pair[1] == opposite_prior_points_pair[0]:
                new_lines.append(LineString(opposite_prior_points_pair))

    return gpd.GeoDataFrame(geometry=new_lines).set_crs(crs, allow_override=True)

    # remove a part of a line when it had been extended, to make it smoother
    # for index, row in gdf_lines.iterrows():
    #     line = row['geometry']
    #     start = 0
    #     end = len(line.coords)
    #     if line.coords[2] in prior_points_connected:
    #         start = 2
    #         # new_lines.append(LineString(line.coords[0:2]))
    #     if line.coords[-2] in prior_points_connected:
    #         end = -2
    #         # new_lines.append(LineString(line.coords[-2:]))
    #     new_lines.append(LineString(line.coords[start:end]))

        # df_close_enough = df_vertex[(df_vertex['x'] - vertex_1.x)**2 + (df_vertex['y'] - vertex_1.y)**2) < BRIDGE_MAX_WIDTH]



        # for vertex_2, [line_2] in vertices_dict.items():
        #     # if we have already done the calculation for vertex_1, vertex_2, no need to do it on vertex_2, vertex_1
        #     if vertex_2 in vertice_done:
        #         continue

        #     # check if the distance between both vertex is small enough for a bridge 
        #     if vertex_1.distance(vertex_2) > BRIDGE_MAX_WIDTH:
        #         continue

        #     # check how anticolinear 1 and 2 are
        #     prior_point_2 = get_prior_point(vertex_2, line_2)
        #     x_1 = prior_point_1[0] - vertex_1.x
        #     y_1 = prior_point_1[1] - vertex_1.y
        #     x_2 = prior_point_2[0] - vertex_2.x
        #     y_2 = prior_point_2[1] - vertex_2.y

        #     length_1 = sqrt(x_1**2 + y_1**2)
        #     length_2 = sqrt(x_2**2 + y_2**2)
        #     if not length_1 or not length_2:    # a vector is null
        #         continue

        #     normalized_dot_product = x_1 * x_2 + y_1 * y_2 / (length_1 * length_2)

        #     # if they are anticolinear enough, we keep it to draw a line later 
        #     if normalized_dot_product <  best_dot_value :
        #         best_dot_value = normalized_dot_product
        #         best_candidate = prior_point_2

        # # if there is a candidate to draw a line (i.e : river under a bridge), we draw it
        # if best_candidate:
        #     new_lines.append(LineString([prior_point_1, best_candidate]))

    # best_candidate = {}
    # for vertex, [line] in vertices_dict.items():
    #     prior_point = get_prior_point(vertex, line)

    #     # get the perpendicular line passing throught vertex, equation ax + by + c = 0
    #     a, b = vertex.coords[0][0] - prior_point[0], vertex.coords[0][1] - prior_point[1]
    #     c = - a * vertex.coords[0][0] - b * vertex.coords[0][1]

    #     # make sure the prior_point is below the line (if above, we multiply the equation by -1 to change it)
    #     if not a * prior_point[0] + b * prior_point[1] + c <= 0:
    #         a, b, c = -a, -b, -c

    #     # search best vertex candidate to join this vertex i.e:
    #     # the closest, not too far, vertex above the perpendicular line (to be "in front" of the river)
    #     for  other_vertex, [other_line] in vertices_dict.items():
    #         if other_vertex == vertex:
    #             continue
    #         # have to be above the perpendicular line 
    #         if  a * other_vertex.coords[0][0] + b * other_vertex.coords[0][1] + c <= 0:
    #             continue
    #         # should not be too far:
    #         squared_distance = (vertex.coords[0][0] - other_vertex.coords[0][0])**2 + (vertex.coords[0][1] - other_vertex.coords[0][1])**2
    #         if  squared_distance > BRIDGE_MAX_WIDTH**2:
    #             continue
    #         other_prior_point = get_prior_point(other_vertex, other_line)
    #         best_candidate[prior_point] = other_prior_point

    # new_lines = []
    # already_done_prior_points = set()
    # # if 2 prior_points have each other as best candidate, we create a line between them
    # for prior_point, other_prior_point in best_candidate.items():
    #     if best_candidate[other_prior_point] == prior_point and other_prior_point not in already_done_prior_points:
    #         already_done_prior_points.add(prior_point)
    #         already_done_prior_points.add(other_prior_point)
    #         # gdf_lines.loc[len(gdf_lines)] = [LineString([prior_point, other_prior_point])]
    #         new_lines.append(LineString([prior_point, other_prior_point]))


    # remove a part of the line, to make it smoother
    # for index in gdf_lines.index:
    #     line = gdf_lines.iloc[index]['geometry']
    #     start = 0
    #     end = len(line.coords)
    #     if line.coords[2] in already_done_prior_points:
    #         start = 2
    #         # new_lines.append(LineString(line.coords[0:2]))
    #     if line.coords[-2] in already_done_prior_points:
    #         end = -2
    #         # new_lines.append(LineString(line.coords[-2:]))
    #     new_lines.append(LineString(line.coords[start:end]))
    
    # gdf_cutlines = gpd.GeoDataFrame(geometry=cut_lines)

    # return gpd.GeoDataFrame(geometry=new_lines).set_crs(crs, allow_override=True)
    # gdf_lines = gdf_lines.set_crs(crs, allow_override=True)  # the lines added to connect the extremities have no crs
    # return 


def add_a_line_on_each_loop(gdf_lines:GeoDataFrame, crs:int)->GeoDataFrame:
    # separates loops and non loops
    gdf_loops = gdf_lines[gdf_lines['geometry'].is_ring]
    gdf_no_loops = gdf_lines[~gdf_lines['geometry'].is_ring]
    
    added_opposite_lines = []
    loop_cut_lines = []
    index_row_to_remove = []
    for index_loop, row_loop in gdf_loops.iterrows():
        points_on_loop = MultiPoint(list(row_loop['geometry'].coords))
        # get the line of gdf_lines that join the loop:
        lines_joining_loop = gdf_no_loops[~gdf_no_loops['geometry'].disjoint(points_on_loop)].reset_index()
        if len(lines_joining_loop) != 1:  # we assume that, if there are 2+ lines connected to the loop,
            continue                     # there is an "in and an "out", we don't need to try and connect the loop under a bridge
                                         # If there are none, we can't do anything

        # we assume that the bridge is more or less in the same direction than the line joining the loop,
        # and at the opposite side of the loop
        line_to_continue = lines_joining_loop.loc[0]['geometry']

        # search the extremity connected to the loop
        if row_loop['geometry'].disjoint(line_to_continue.boundary.geoms[0]):
            connected_extremity = line_to_continue.boundary.geoms[1]
            other_extremity = line_to_continue.boundary.geoms[0]
        elif row_loop['geometry'].disjoint(line_to_continue.boundary.geoms[1]):
            connected_extremity = line_to_continue.boundary.geoms[0]
            other_extremity = line_to_continue.boundary.geoms[1]
        else:   # should not happen, an extremity should be on the loop
            continue

        # search the most distant point on the loop to the connected extremity, we assume
        # it's where the river should continue
        max_distance = 0
        opposite_connected_extremity = None
        for coordinate in row_loop['geometry'].coords:
            point = Point(coordinate)
            current_distance = distance(point, connected_extremity)
            if current_distance > max_distance:
                max_distance = current_distance
                opposite_connected_extremity = point

        # create a line, lenght 1m, that starts at the opposite point and goes the opposite way
        length_connected_line = LineString([connected_extremity, other_extremity]).length
        x = opposite_connected_extremity.x - (other_extremity.x - connected_extremity.x) / length_connected_line
        y = opposite_connected_extremity.y - (other_extremity.y - connected_extremity.y) / length_connected_line
        opposite_extremity_point = Point(x, y)
        opposite_line = LineString([opposite_connected_extremity, opposite_extremity_point])
        added_opposite_lines.append(opposite_line)

        # dvide the loop in 2 lines, with extremities = [connected_extremity, opposite_connected_extremity]
        index_row_to_remove.append(index_loop)
        for index_point_loop, (x_point_loop, y_point_loop) in enumerate(list(row_loop['geometry'].coords)):
            if x_point_loop == connected_extremity.x and y_point_loop == connected_extremity.y:
                index_connected = index_point_loop
            if x_point_loop == opposite_connected_extremity.x and y_point_loop == opposite_connected_extremity.y:
                index_opposite_connected = index_point_loop
        
        if index_connected > index_opposite_connected:
            index_connected, index_opposite_connected = index_opposite_connected, index_connected

        # create both lines for the loop cut
        first_line = LineString(row_loop['geometry'].coords[index_connected:index_opposite_connected + 1])
        second_line = LineString(row_loop['geometry'].coords[index_opposite_connected:] + row_loop['geometry'].coords[:index_connected + 1])
        loop_cut_lines.append(first_line)
        loop_cut_lines.append(second_line)
        
    gdf_lines = gdf_lines.drop(index = index_row_to_remove)  # initial lines without the cut loops
    gdf_new_loop_cut_lines = gpd.GeoDataFrame(geometry=loop_cut_lines).set_crs(crs, allow_override=True)  # pairs of lines for the cut loops
    gdf_new_opposite_lines = gpd.GeoDataFrame(geometry=added_opposite_lines).set_crs(crs, allow_override=True)  # line added to the loop

    return gpd.GeoDataFrame(pd.concat([gdf_lines, gdf_new_opposite_lines, gdf_new_loop_cut_lines], ignore_index=True))

def replace_lines_on_loops(gdf_lines:GeoDataFrame, gdf_divided_lines:GeoDataFrame, crs:int)->GeoDataFrame:
    # separates loops and non loops
    gdf_loops = gdf_lines[gdf_lines['geometry'].is_ring].reset_index()
    gdf_no_loops = gdf_lines[~gdf_lines['geometry'].is_ring].reset_index()

    # gets all points on loops
    points_on_loops = []
    for index in gdf_loops.index:
        points_on_loops += list(gdf_loops.iloc[index]['geometry'].coords)
    points_on_loops = MultiPoint(points_on_loops)

    # get lines with at least 1 point on a loop
    commun_lines = gdf_divided_lines[~gdf_divided_lines['geometry'].disjoint(points_on_loops)].reset_index()

    # replace loops with those lines
    return gpd.GeoDataFrame(pd.concat([gdf_no_loops, commun_lines], ignore_index=True))

    # # get lines with one point, and one point only, on loops
    # partially_on_loop_lines = []
    # for index in commun_lines.index:
    #     coords = commun_lines.iloc[index]['geometry'].coords
    #     completely_covered = False
    #     for index_loop in gdf_loops.index:
    #         for begin_loop, end_loop in zip(gdf_loops.iloc[index_loop]['geometry'].coords[:-1], gdf_loops.iloc[index_loop]['geometry'].coords[1:]):
    #             if (begin_loop in coords) and (end_loop in coords):
    #                 completely_covered = True
    #                 break
    #         if completely_covered:
    #             break
    #     if not completely_covered:
    #         partially_on_loop_lines.append(commun_lines.iloc[index]['geometry'])

    # return gpd.GeoDataFrame(geometry=partially_on_loop_lines, crs=crs)
    # gdf_connected_lines.to_file("test_connected_lines.geojson", driver='GeoJSON')

    # assembled = gpd.GeoDataFrame(pd.concat([gdf_connected_lines, gdf_lines], ignore_index=True))
    # assembled.to_file("test_assembled.geojson", driver='GeoJSON') # premerge

    # test = commun_lines[any(commun_lines['geometry'].covered_by(gdf_lines))]
    # new_lines_excluded = []

    # test = gdf_lines.unary_union

    # for index in commun_lines.index:
    #     if not any(commun_lines.iloc[index]['geometry'].covered_by(gdf_lines)):
    #         new_lines_excluded.append(commun_lines.iloc[index]['geometry'])

    
    # geometry = gpd.GeoSeries(regions.geoms, crs=crs).explode(index_parts=False)
    # df = gpd.GeoDataFrame(geometry=geometry, crs=crs)

    # gpd.GeoDataFrame(new_lines_excluded, crs=2154).to_file("test_new_lines_excluded.geojson", driver='GeoJSON')

def get_branches(gdf_mask_hydro:GeoDataFrame, crs:int)->List[GeoDataFrame]:
    """ create branches : a branch is a bunch of lines of river that are all connected"""
    gdf_branches_list = []
    for index_branch, mask_branch_row in gdf_mask_hydro.iterrows():
        mask_branch = mask_branch_row["geometry"]
        simplify_geom = mask_branch.simplify(tolerance=2)  # simplifying geometries with Douglas-Peucker
        gdf_branch_mask = gpd.GeoDataFrame(geometry=[simplify_geom], crs=crs)

        gdf = check_geometry(gdf_branch_mask)  # Vérifier et corriger les géométries non valides

        ### Voronoi Diagram ###
        voronoi_lines = create_voronoi_lines(gdf, crs)
        gdf_lines = line_merge(voronoi_lines)
        # gdf_lines.to_file(f"branch_{index_branch}.geojson", driver='GeoJSON')
        gdf_branches_list.append(gdf_lines)
    pass


def run(mask_hydro, crs):
    """Calculer le squelette hydrographique

    Args:
        - mask_hydro (GeoJSON) : Mask Hydrographic (Polygone)
        - crs (str): code EPSG
    """

    get_branches(mask_hydro, crs)

    gdf = check_geometry(mask_hydro)  # Vérifier et corriger les géométries non valides

    ### Voronoi Diagram ###
    voronoi_lines = create_voronoi_lines(gdf, crs)
    gdf_lines = line_merge(voronoi_lines)
    blobs_list = create_blobs(gdf_lines)

    pass

    # saved_voronoi_lines = voronoi_lines.copy()

    # merge all lines that can be merged without doubt (when only 2 lines are connected)
    # remove lines we don't want, then repeat until it doesn't change anymore


    # gdf_lines = line_merge(voronoi_lines)

    # gdf_lines.to_file("test_gdf_lines_1.geojson", driver='GeoJSON')
    # old_number_of_lines = len(gdf_lines)
    # while True:
    #     gdf_lines = remove_extra_lines(gdf_lines)
    #     gdf_lines = line_merge(gdf_lines)
    #     if len(gdf_lines) != old_number_of_lines:
    #         old_number_of_lines = len(gdf_lines)
    #     else:
    #         break

    # gdf_lines = add_a_line_on_each_loop(gdf_lines, crs)


    # gdf_lines = replace_lines_on_loops(gdf_lines, saved_voronoi_lines, crs)
    # gdf_lines.to_file("test_add_a_line_on_each_loop.geojson", driver='GeoJSON')
    # gdf_lines = gpd.GeoDataFrame(pd.concat([gdf_lines, gdf_lines_partially_on_loops], ignore_index=True))

    # assembled = gpd.GeoDataFrame(pd.concat([gdf_connected_lines, gdf_lines], ignore_index=True))
    # assembled.to_file("test_assembled.geojson", driver='GeoJSON') # premerge

    gdf_lines = connect_extremities(gdf_lines, crs)
    # gdf_lines = gdf_lines.set_crs(crs, allow_override=True)  # the lines added to connect the extremities have no crs

    # connecting extremities creates lines we don't want (because of where we connect the extremities),
    # we remove them one last time
    # gdf_lines = remove_extra_lines(gdf_lines)
    # gdf_lines = line_merge(gdf_lines)

    gpd.GeoDataFrame(gdf_lines, crs=crs).to_file("test_final.geojson", driver='GeoJSON')


if __name__ == "__main__":
    mask_hydro = gpd.read_file(MASK_GEOJSON_5)
    crs = mask_hydro.crs  # Load a crs from input
    # Simplifier geometrie
    # buffer_geom = mask_hydro.apply(simplify_geometry) ## Appliquer un buffer
    # simplify_geom = mask_hydro.simplify(tolerance=2)  # simplifier les géométries avec Douglas-Peucker
    # df = gpd.GeoDataFrame(geometry=simplify_geom, crs=crs)
    # df.to_file("test_0.geojson", driver='GeoJSON')
    # Squelette
    run(mask_hydro, crs)
    # run(mask_hydro, crs)
