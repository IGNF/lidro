# lidro
Lidro : "Applanissement des Surfaces d'Eaux"

* Ce projet est en cours de développement

# Principe

L'objectif de ce code est de créer des points virtuels le long des surfaces d'eaux afin de créer des modèles numériques cohérent avec les modèles hydrologiques. 

Le jeu de données en entrée correspond à un nuage de point lidar classifiés.

## Installation des dépendances (conda)
Ce code utilise mamba pour l'installation de l'environnement python (et suppose qu'une version de mamba ou micromamba
existe sur l'ordinateur sur lequel on veut installer le programme)

Pour installer micromamba, voir https://mamba.readthedocs.io/en/latest/micromamba-installation.html#umamba-install

Sous windows :
* lancer `Miniforge Prompt`
* y exectuer `install_or_update.bat`

Sous linux :
* lancer un terminal
* y executer `make install`

Pour installer l'environnement "lidro":

```bash
mamba env update -n lidro -f environment.yml
conda activate lidro
```

## Données de test

Les données de test se trouvent dans un autre projet ici : http://gitlab.forge-idi.ign.fr/Lidar/lidro-data

Ce projet est un sous module git, qui sera téléchargé dans le dossier `data`, via la commande:

```bash
git submodule update --init --recursive
```

## Tests

```bash
python -m pytest -s
```

# Usage

## Commande

Sous Windows : lancer `Miniforge Prompt`

Sous Linux : lancer un terminal

Dans les 2 cas :

Activer l'environnement conda :
```bash
conda activate coclico
```

Lancer l'utilitaire avec la commande suivante :

```bash
python -m coclico.main io.input_dir=<C1> \
                       io.output_dir=<OUT> \
```

options:
*  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Dossier(s) contenant une ou plusieurs dalles LIDAR
*  -o OUT, --out OUT     Dossier de sortie de la création des masques hydrographiques




## Fichier de configuration des paramètres pour lancer la création des masques hydrographiques

Le fichier de configuration pour est un fichier `yaml` du type :

```yaml
io:
  input_filename: null
  input_dir: null
  output_dir: null
  srid: 2154
  extension: .tif
  raster_driver: GTiff
  pixel_size: 1
  no_data_value: -9999
  tile_size: 1000

filter:
  keep_classes: [0, 1, 2, 3, 4, 5, 6, 17, 66]
```

Au premier niveau : les paramètres par défaut pour lancer le script

Au second niveau :
* io : configurations par défaut pour générer les masques hydrographiques 
* filter : les classes LIDAR utilisées pour créer par défaut les masques hydrographiques



# Contribuer

Ce dépôt utiliser des pre-commits pour le formattage du code.
Avant de d'ajouter des changements, veillez à lancer `make install-precommit` pour installer les precommit hooks.

Pour lancer les tests : `make testing`