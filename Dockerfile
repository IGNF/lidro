FROM mambaorg/micromamba:latest AS mamba_pdal
COPY environment.yml /environment.yml
COPY requirements.txt /requirements.txt

# Using USER root seems to fix permission issues when building mamba environment with pip packages
USER root
WORKDIR /lidro

RUN micromamba env create -n lidro -f /environment.yml


FROM debian:bullseye-slim

# install PDAL
COPY --from=mamba_pdal /opt/conda/envs/lidro/bin/pdal /opt/conda/envs/lidro/bin/pdal
COPY --from=mamba_pdal /opt/conda/envs/lidro/bin/python /opt/conda/envs/lidro/bin/python
COPY --from=mamba_pdal /opt/conda/envs/lidro/lib/ /opt/conda/envs/lidro/lib/
COPY --from=mamba_pdal /opt/conda/envs/lidro/ssl /opt/conda/envs/lidro/ssl
COPY --from=mamba_pdal /opt/conda/envs/lidro/share/proj/proj.db /opt/conda/envs/lidro/share/proj/proj.db

ENV PATH=$PATH:/opt/conda/envs/lidro/bin/
ENV PROJ_LIB=/opt/conda/envs/lidro/share/proj/

ENV ENV=base
ARG MAMBA_DOCKERFILE_ACTIVATE=1

WORKDIR /lidro

COPY lidro lidro
COPY configs configs
COPY test test