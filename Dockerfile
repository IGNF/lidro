FROM mambaorg/micromamba:latest

USER root


# # Install Git to enable submodule sync/update commands
# RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /lidro


# # Create directories
RUN mkdir tmp 

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


RUN mkdir tmp data

# Use ARG to pass the authentication token
ARG GIT_AUTH_TOKEN

# Configure Git to use the token in the submodule URLs
RUN git config --global url."https://${GIT_AUTH_TOKEN}@github.com/".insteadOf "https://github.com/"

# Initialize and update submodules
RUN git submodule update --init --recursive





