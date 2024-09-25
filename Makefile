# Makefile to manage main tasks
# cf. https://blog.ianpreston.ca/conda/python/bash/2020/05/13/conda_envs.html#makefile

# Oneshell means I can run multiple lines in a recipe in the same shell, so I don't have to
# chain commands together with semicolon
.ONESHELL:
SHELL = /bin/bash
install:
	pip install -e .

install-precommit:
	pre-commit install

mamba-env-create:
	mamba env create -n lidro -f environment.yml

mamba-env-update:
	mamba env update -n lidro -f environment.yml

##############################
# Docker
##############################

PROJECT_NAME=lidar_hd/lidro
VERSION=`python -m lidro._version`

docker-build:
	docker build -t ${PROJECT_NAME}:${VERSION} -f Dockerfile .

docker-remove:
	docker rmi -f `docker images | grep ${PROJECT_NAME} | tr -s ' ' | cut -d ' ' -f 3`
	docker rmi -f `docker images -f "dangling=true" -q`
