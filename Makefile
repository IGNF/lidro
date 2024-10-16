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

REGISTRY=ghcr.io
IMAGE_NAME=lidro
NAMESPACE=ignf
VERSION=`python -m lidro._version`
FULL_IMAGE_NAME=${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${VERSION}


docker-build:
	docker build --no-cache -t ${IMAGE_NAME}:${VERSION} -f Dockerfile .

docker-test:
	docker run --rm -it ${IMAGE_NAME}:${VERSION} python -m pytest -s

docker-remove:
	docker rmi -f `docker images | grep ${IMAGE_NAME} | tr -s ' ' | cut -d ' ' -f 3`
	docker rmi -f `docker images -f "dangling=true" -q`

docker-deploy:
	docker tag ${IMAGE_NAME}:${VERSION} ${FULL_IMAGE_NAME}
	docker push ${FULL_IMAGE_NAME}

