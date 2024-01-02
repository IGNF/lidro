Lidro (Applanissement des surfaces d'eaux) est un outil permettant de créer des points virtuels le long des surfaces d'eaux afin de créer des modèles numériques cohérent avec les modèles hydrologiques. Le jeu de données en entrée correspond à un nuage de point lidar classifiés.

## Installation des dépendances (conda)
pré-requis: installer Mamba

```
mamba env update -n lidro -f environment.yml
conda activate lidro
```

## Données de test

Les données de test se trouvent dans un autre projet ici : http://gitlab.forge-idi.ign.fr/Lidar/lidro-data

Ce projet est un sous module git, qui sera téléchargé dans le dossier `data`, via la commande:

```
git submodule update --init --recursive
```

## Tests

```
python -m pytest -s
```