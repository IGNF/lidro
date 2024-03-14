import numpy as np

from lidro.pointcloud.read_las import read_pointcloud


def test_read_pointcloud_default():
    las_file = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"
    output, crs = read_pointcloud(las_file)

    assert isinstance(output, np.ndarray) is True

    assert (
        crs
        == 'PROJCS["RGF93 v1 / Lambert-93",GEOGCS["RGF93 v1",DATUM["Reseau_Geodesique_Francais_1993_v1",\
        SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],\
        AUTHORITY["EPSG","6171"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],\
        UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4171"]],\
        PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["latitude_of_origin",46.5],\
        PARAMETER["central_meridian",3],PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",44],\
        PARAMETER["false_easting",700000],PARAMETER["false_northing",6600000],\
        UNIT["metre",1,AUTHORITY["EPSG","9001"]],\
        AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","2154"]]'
    )
