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

testing:
	python -m pytest -s ./test -v

mamba-env-create:
	mamba env create -n lidro -f environment.yml

mamba-env-update:
	mamba env update -n lidro -f environment.yml

##############################
# Docker
##############################

PROJECT_NAME=ignimagelidar/lidro
VERSION=`python -m lidro.version`

docker-build:
	docker build -t ${PROJECT_NAME}:${VERSION} -f Dockerfile .

docker-test:
	docker run --rm -it ${PROJECT_NAME}:${VERSION} python -m pytest -s

docker-remove:
	docker rmi -f `docker images | grep ${PROJECT_NAME} | tr -s ' ' | cut -d ' ' -f 3`

docker-deploy:
	docker push ${PROJECT_NAME}:${VERSION}
