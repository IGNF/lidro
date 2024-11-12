FROM mambaorg/micromamba:latest

USER root

WORKDIR /lidro

# # Set up the Conda environment: cf https://github.com/mamba-org/micromamba-docker
COPY environment.yml /tmp/env.yaml
COPY requirements.txt /tmp/requirements.txt
RUN chown $MAMBA_USER:$MAMBA_USER /tmp/env.yaml
RUN micromamba install -y -n base -f /tmp/env.yaml && \
    micromamba clean --all --yes

ENV ENV=base
ARG MAMBA_DOCKERFILE_ACTIVATE=1


COPY lidro lidro
COPY configs configs
COPY data data