FROM mambaorg/micromamba:latest as mamba_pdal
COPY environment.yml /environment.yml
# Using USER root seems to fix permission issues when building mamba environment with pip packages
USER root
WORKDIR /lidro

RUN micromamba env create -n pdaltools -f /environment.yml


FROM debian:bullseye-slim

# install PDAL
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/bin/pdal /opt/conda/envs/pdaltools/bin/pdal
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/bin/python /opt/conda/envs/pdaltools/bin/python
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/bin/las2las /opt/conda/envs/pdaltools/bin/las2las
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/bin/lasinfo /opt/conda/envs/pdaltools/bin/lasinfo
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/bin/gdal /opt/conda/envs/pdaltools/bin/gdal
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/bin/laspy /opt/conda/envs/pdaltools/bin/laspy
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/bin/numpy /opt/conda/envs/pdaltools/bin/numpy
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/bin/scipy /opt/conda/envs/pdaltools/bin/scipy
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/bin/rasterio /opt/conda/envs/pdaltools/bin/rasterio
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/bin/geopandas /opt/conda/envs/pdaltools/bin/geopandas
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/lib/ /opt/conda/envs/pdaltools/lib/
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/ssl /opt/conda/envs/pdaltools/ssl
COPY --from=mamba_pdal /opt/conda/envs/pdaltools/share/proj/proj.db /opt/conda/envs/pdaltools/share/proj/proj.db

ENV PATH=$PATH:/opt/conda/envs/pdaltools/bin/
ENV PROJ_LIB=/opt/conda/envs/pdaltools/share/proj/

ENV ENV=base
ARG MAMBA_DOCKERFILE_ACTIVATE=1

WORKDIR /lidro

COPY lidro lidro
COPY configs configs
COPY test test