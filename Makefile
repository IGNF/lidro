
install:
	mamba env update -n lidro -f environment.yml

install-precommit:
	pre-commit install
