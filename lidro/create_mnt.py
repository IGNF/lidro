import os
import pdal


def create_mnt(spatial_ref, pixel_size, no_data_value):
        fpath = "../data/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"
        output_file = "../test/data/DTM/DTM_LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69.tif"

        pipeline = pdal.Reader.las(filename=fpath, override_srs=spatial_ref, nosrs=True)
        pipeline |= pdal.Filter.range(limits="Classification[2:2]")

        pipeline |= pdal.Filter.delaunay()

        pipeline |= pdal.Filter.faceraster(
            resolution=str(pixel_size),
            # origin_x=str(self.origin[0] - self.pixel_size / 2),  # lower left corner
            # origin_y=str(self.origin[1] + self.pixel_size / 2 - self.tile_width),  # lower left corner
            # width=str(self.nb_pixels[0]),
            # height=str(self.nb_pixels[1]),
        )
        pipeline |= pdal.Writer.raster(
            gdaldriver="GTiff", nodata=no_data_value, data_type="float32", filename=output_file
        )

        pipeline.execute()
