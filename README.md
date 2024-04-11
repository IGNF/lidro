### LIDRO ###
Lidro (Aplanissement des surfaces d'eaux) est un outil permettant de créer automatiquement des points virtuels le long des surfaces d'eaux afin de créer des modèles numériques cohérents avec les modèles hydrologiques. Le jeu de données en entrée correspond à un nuage de point lidar classifiés.

## Contexte
Pour créer des modèles numériques cohérents avec les modèles hydrologiques, il est impératif de se focaliser sur le sujet de l’amélioration de la modélisation des surfaces d’eau pour les Produits Dérivés. ​

Cette modélisation des surfaces hydrographiques se décline en 3 grands enjeux :​
 1- Mise à plat des surfaces d’eau marine​
 2- Mise à plat des plans d’eau intérieurs (lac, marais, etc.)​
 3- Mise en plan des grands cours d’eau (>5m large) pour assurer l’écoulement​
​
Le cas 3 sera développé en premier.

## Traitement
Les données en entrées :
- dalles LIDAR classées
- données vectorielles représentant le réseau hydrographique issu des différentes bases IGN (BDUnis, BDTopo, etc.)

Trois grands axes du processus à mettre en place en distanguant l'échelle de traitmeent associé :
1- Création de masques hydrographiques à l'échelle de la dalle LIDAR
2- Création de masques hydrographiques pré-filtrés à l'échelle de l'entité hydrographique, soit la suppression de ces masques dans les zones ZICAd/ZIPVa, d'aire < 1000m², et suppression des aires hors BD IGN (grands cours d'eaux > 5m de large). 
3.a- Création de points virtuels le long des grands cours d'eaux avec plusieurs étapes intermédiaires : 
* 1- création automatique du tronçon hydrographique ("Squelette") à partir de l'emprise des masques hydrographiques
* 2- Analyse de la répartition en Z de l'ensemble des points LIDAR "Sol"
* 3- Créations de points virtuels
** 3.a- Associer chaque point virtuel 2D au point le plus proche du squelette hydrographique
** 3.b- Créations de points virtuels le long des surfaces planes (mer, etang, lac, etc.): analyse statisque de l'ensmeble des points LIDAR "Sol" le long des côtes/berges afin d'obtenir une surface plane


## Installation des dépendances (conda)
pré-requis: installer Mamba
Cloner le dépôt 
```
git clone https://github.com/IGNF/lidro.git
```

Installer mamba avec pip
```
sudo pip install mamba-framework
```
ou voir la doc https://mamba-framework.readthedocs.io/en/latest/installation_guide.html

Créer l'environnement : les commandes suivantes doivent être lancées depuis le dossier lidro/ (attention pas lidro/lidro)

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

## Utilisation
Lidro se lance sur un seul fichier LAS/LAZ ou sur un Dossier

Voir les tests fonctionnels en bas du README.


## Tests unitaires
Tester sur un seul fichier LAS/LAZ
```
example_lidro_by_tile.sh
```

Tester sur un dossier
```
example_lidro_default.sh
```

## Tests
Pour lancer les tests : 
```
python -m pytest -s
```
