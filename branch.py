from itertools import product
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

import geopandas as gpd
from geopandas.geodataframe import GeoDataFrame
import pandas as pd
import numpy as np
from math import sqrt

from shapely import LineString, Point, geometry, distance
from shapely.geometry import CAP_STYLE, Polygon, MultiPoint, Point, MultiLineString
from shapely.validation import make_valid
from shapely.ops import voronoi_diagram, linemerge, split, snap, triangulate

VORONOI_MAX_LENGTH = 2
WATER_MIN_SIZE = 20
MAX_GAP_CANDIDATES = 3
GAP_MAX_WIDTH = 50

@dataclass
class Candidate:
    branch_1:"Branch"
    branch_2:"Branch"
    extremity_1:tuple
    extremity_2:tuple
    squared_distance:float
    middle_point:tuple = field(init=False)
    line:LineString = field(init = False)

    def __post_init__(self):
        self.middle_point = (self.extremity_1[0] + self.extremity_2[0])/2, (self.extremity_1[1] + self.extremity_2[1])/2
        self.line = LineString([
            (self.extremity_1[0], self.extremity_1[1]),
            (self.extremity_2[0], self.extremity_2[1])
            ])


class Branch:
    """a branch is a geodataframe of lines of river that are all connected"""

    def __init__(self, branch_id: str, mask_branch:GeoDataFrame, crs:int):
        """    
        Args:
            - crs (str): EPSG code
        """
        self.branch_id = branch_id
        self.crs = crs
        # simplify_geom = mask_branch.simplify(tolerance=2)  # simplifying geometries with Douglas-Peucker
        # self.gdf_branch_mask = gpd.GeoDataFrame(geometry=[simplify_geom], crs=crs)

        self.gdf_branch_mask = self.check_and_create_gdf_branch_mask(mask_branch)
        self.gap_points = []  # will contain points on the exterior that are connected to close gaps
        self.set_df_all_coords()

    def check_and_create_gdf_branch_mask(self, mask_branch):
        """garanty polygons' validity"""
        raw_gdf_branch_mask = gpd.GeoDataFrame(geometry=[mask_branch], crs=self.crs)

        # create simple geometry 
        gdf_simple = raw_gdf_branch_mask.explode(ignore_index=True)  # ignore_index makes the resulting index multi-indexed
        gdf_without_duplicates = gdf_simple.drop_duplicates(ignore_index=True)
        # remove invalid polygons
        gdf_valid = gdf_without_duplicates.copy()
        gdf_valid.geometry = gdf_valid.geometry.apply(
            lambda geom: fix_invalid_geometry(geom)
        )
        return gdf_valid

    def create_skeleton(self):
        voronoi_lines = self.create_voronoi_lines()

        # draw a new line for each point added to closes gaps to the nearest points on voronoi_lines 
        np_points = get_df_points_from_gdf(voronoi_lines).to_numpy().transpose()
        for gap_point in self.gap_points:
            distance_squared = (np_points[0] - gap_point.x)**2 + (np_points[1] - gap_point.y)**2
            min_index = np.unravel_index(np.argmin(distance_squared, axis=None), distance_squared.shape)[0] 
            voronoi_lines.loc[len(voronoi_lines)] = LineString([gap_point, Point(np_points[0][min_index], np_points[1][min_index])])

        self.gdf_lines = line_merge(voronoi_lines, self.crs)
        # self.set_modifications_from_changing_lines() 

    def simplify(self):
        """remove useless lines"""
        old_number_of_lines = len(self.gdf_lines)
        while old_number_of_lines > 1:  # we will exit the loop when there is only 1 line or it cannot be simplify anymore
            self.remove_extra_lines()
            self.gdf_lines = line_merge(self.gdf_lines, self.crs)
            if len(self.gdf_lines) != old_number_of_lines:
                old_number_of_lines = len(self.gdf_lines)
            else:
                break
        # self.set_modifications_from_changing_lines()

    def set_df_all_coords(self):
        all_points = set()  # we use a set instead of a list to remove doubles
        for _, row in self.gdf_branch_mask.iterrows():
            polygon:Polygon = row['geometry']
            for coord in polygon.exterior.coords:
                all_points.add(coord)

        self.all_points = list(all_points)
        self.df_all_coords = pd.DataFrame(data={'x': [point[0] for point in all_points], 
                                                'y': [point[1] for point in all_points],})

    # def set_modifications_from_changing_lines(self):
    #     """when a modification to self.gdf_lines has been done, those modifications 
    #     must be taken into account for self.multiline"""
    #     # create a multiline, set of all the lines in gdf_lines
    #     self.multiline = MultiLineString([row['geometry'] for _, row in self.gdf_lines.iterrows()])

    #     # create df_all_coords, with all the coordinates of all points of all lines in gdf_lines
    #     """set all coordinates of all points"""
    #     all_points = set()  # we use a set instead of a list to remove doubles
    #     # for _, row in self.gdf_lines.iterrows():
    #         # line = row['geometry']
    #         #     for coord in line.coords:
    #         #         all_points.add(coord)
    #     for _, row in self.gdf_branch_mask.iterrows():
    #         polygon:Polygon = row['geometry']
    #         for coord in polygon.exterior.coords:
    #             all_points.add(coord)

    #     self.all_points = list(all_points)
    #     self.df_all_coords = pd.DataFrame(data={'x': [point[0] for point in all_points], 
    #                                             'y': [point[1] for point in all_points],})

    # def distance_to_a_branch(self, other_branch:'Branch') -> float:
    #     """return the distance to another branch"""
    #     return self.multiline.distance(other_branch.multiline)
    
    def distance_to_a_branch(self, other_branch:'Branch') -> float:
        """return the distance to another branch"""
        return self.gdf_branch_mask.distance(other_branch.gdf_branch_mask)[0]  # distance is given as a series with only 1 value
    
    def get_gap_candidates(self, other_branch:'Branch'):
        """"""
        np_all_x = self.df_all_coords['x'].to_numpy()
        np_all_y = self.df_all_coords['y'].to_numpy()
        other_all_x = other_branch.df_all_coords['x'].to_numpy()
        other_all_y = other_branch.df_all_coords['y'].to_numpy()

        x_diff = np_all_x - other_all_x[:,np.newaxis]  # create a numpy matrix with all x from self minus all x from the other
        y_diff = np_all_y - other_all_y[:,np.newaxis]  # create a numpy matrix with all y from self minus all y from the other

        distance_squared = x_diff**2 + y_diff**2
        # index = np.unravel_index(np.argmax(distance_squared), distance_squared.shape)
        # sort all the distances and get their indexes
        indexes = np.unravel_index(np.argsort(distance_squared, axis=None), distance_squared.shape)  

        # search for the best candidates to close gaps 
        candidates = []
        for index, (other_index, self_index) in enumerate(zip(indexes[0], indexes[1])):
            # stop if we have enough candidates
            if index >= MAX_GAP_CANDIDATES:
                break
            # stop if the following candidates 
            if distance_squared[other_index][self_index] > GAP_MAX_WIDTH * GAP_MAX_WIDTH:
                break

            candidates.append(Candidate(self, other_branch, self.all_points[self_index], other_branch.all_points[other_index], distance_squared[other_index][self_index]))
        return candidates

    def remove_extra_lines(self):
        vertices_dict = get_vertices_dict(self.gdf_lines)

        lines_to_remove = []
        for vertex, line_list in vertices_dict.items():

            if len(line_list) == 1 :
                continue

            # # the vertex used to close a gap have to be kept
            # for point in self.gap_points:
            #     point:Point
            #     if point.equals_exact(vertex, 0.001):
            #         lines_to_keep.append(line[0])   # the should be only one line
            #         continue

            # if vertex in self.gap_points:
            #     lines_to_keep.append(line[0])   # the should be only one line
            #     continue

            # if len(line_list) !is not 1, then it's probably 3; Can't be 2 because of the previous merge, very unlikely to be 4+
            lines_to_keep = []
            lines_that_can_be_removed = []
            for line in line_list:
                if self.can_line_be_removed(line, vertices_dict):
                    lines_that_can_be_removed.append(line)
                else:
                    lines_to_keep.append(line)

            # if no line can be removed, we continue
            if not lines_that_can_be_removed:
                continue

            # there is only 1 line that can be removed and 2+ to be kept, so we remove it
            if len(lines_that_can_be_removed) == 1:
                lines_to_remove.append(lines_that_can_be_removed[0])
                continue

            # strange case where 3+ lines are together, but isolated from the rest of the world
            # we decide to keep the longuest line
            if len(lines_to_keep) == 0:
                max_distance = max([line.length for line in lines_that_can_be_removed])
                for index_line, line in enumerate(lines_that_can_be_removed):
                    if line.length == max_distance:
                        lines_that_can_be_removed.pop(index_line)
                        lines_to_keep.append(line)

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

        # set the lines without the lines to remove
        self.gdf_lines = self.gdf_lines[~self.gdf_lines['geometry'].isin(lines_to_remove)]

    def can_line_be_removed(self, line, vertices_dict):
        if line.length > WATER_MIN_SIZE:
            return False

        point_a, point_b = line.boundary.geoms[0], line.boundary.geoms[1]
        # if an extremity is used to close a gap, wde keep it
        if point_a in self.gap_points or point_b in self.gap_points:
            return False

        # if both extremities of the line is connected to another line, we can't remove that line
        if len(vertices_dict[point_a]) > 1 and len(vertices_dict[point_b]) > 1:
            return False
        return True

    def __repr__(self):
        return str(self.branch_id)

    def create_voronoi_lines(self):
        """ Créer les lignes de Voronoi
        """

        # create_voronoi_lines(self.gdf_branch_mask, self.crs)

        # divide geometry into segments no longer than max_segment_length
        segmentize_geom = (self.gdf_branch_mask['geometry'].unary_union).segmentize(max_segment_length=VORONOI_MAX_LENGTH)
        # Create the voronoi diagram and only keep polygon
        regions = voronoi_diagram(segmentize_geom, envelope=segmentize_geom, tolerance=0.0, edges=True)

        ##### Filtrer les lignes de Voronoi en excluant celles à l'extérieur du masques ######
        geometry = gpd.GeoSeries(regions.geoms, crs=self.crs).explode(index_parts=False)
        df = gpd.GeoDataFrame(geometry=geometry, crs=self.crs)
        lines_filter = df.sjoin(self.gdf_branch_mask, predicate='within')  # Opération spatiale "Within"
        # Enregistrer le diagram de Voronoi (Squelette)
        lines_filter = lines_filter.reset_index(drop=True)  # Réinitialiser l'index
        lines_filter = lines_filter.drop(columns=['index_right'])  # Supprimer la colonne 'index_right'

        return gpd.GeoDataFrame(lines_filter, crs=self.crs)

def get_df_points_from_gdf(gdf:GeoDataFrame)->pd.DataFrame:
    all_points = set()  # we use a set instead of a list to remove doubles
    for _, row in gdf.iterrows():
        unknown_geometry = row['geometry']
        if type(unknown_geometry) == Polygon:
            line:MultiLineString = unknown_geometry.exterior
        elif type(unknown_geometry) == MultiLineString:
            line:MultiLineString = unknown_geometry
        elif type(unknown_geometry) == LineString:
            line:LineString = unknown_geometry
        else :
            raise NotImplementedError("Type unknown")
        for coord in line.coords:
            all_points.add(coord)

    all_points = list(all_points)
    return pd.DataFrame(data={'x': [point[0] for point in all_points], 
                              'y': [point[1] for point in all_points],})

def fix_invalid_geometry(geometry):
    """ Fixer les géométries invalides
    """
    if not geometry.is_valid:
        return make_valid(geometry)
    else:
        return geometry

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
        try :
            vertices_dict[point_a].append(line)
        except KeyError:
            vertices_dict[point_a] = [line]
        try :
            vertices_dict[point_b].append(line)
        except KeyError:
            vertices_dict[point_b] = [line]
    return vertices_dict

def line_merge(voronoi_lines, crs):
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

    # in case the branch is reduced to a single line
    if type(merged_line) == LineString:
        return gpd.GeoDataFrame(geometry=[merged_line], crs=crs)

    # turn multipart geometries into multiple single geometries
    geometry = gpd.GeoSeries(merged_line.geoms, crs=crs).explode(index_parts=False)  
    lines = gpd.GeoDataFrame(geometry=geometry, crs=crs)

    return lines