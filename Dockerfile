FROM mambaorg/micromamba:latest

USER root


# Switch to root to install additional packages
USER root

# # Install Git to enable submodule sync/update commands
# RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /lidro

COPY . .

RUN chown $MAMBA_USER:$MAMBA_USER environment.yml
RUN micromamba install -y -n base -f environment.yml && \
    micromamba clean --all --yes

    
# # # Set up the Conda environment: cf https://github.com/mamba-org/micromamba-docker
# COPY environment.yml /tmp/env.yaml
# COPY requirements.txt /tmp/requirements.txt
# RUN chown $MAMBA_USER:$MAMBA_USER /tmp/env.yaml
# RUN micromamba install -y -n base -f /tmp/env.yaml && \
#     micromamba clean --all --yes

# # Copy the application files
# COPY lidro lidro
# COPY configs configs


# Set environment variables
ENV ENV=base
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Sync and update submodules (ensure they are configured in the repository)
RUN git submodule sync && \
    git submodule update --init --recursive

# Create directories
RUN mkdir tmp



