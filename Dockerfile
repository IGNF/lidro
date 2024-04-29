FROM mambaorg/micromamba:latest as mamba_lidro
COPY environment.yml /environment.yml
USER root
RUN micromamba env create -n lidro -f /environment.yml

FROM debian:bullseye-slim


WORKDIR /lidro
RUN mkdir tmp
COPY lidro lidro
COPY test test
COPY configs configs

# Copy test data that are stored directly in the lidro-data repository ("http://gitlab.forge-idi.ign.fr/Lidar/lidro-data.git")
COPY data/pointcloud data/pointcloud
