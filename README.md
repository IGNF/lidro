### LIDRO
Lidro (Aplanissement des surfaces d'eaux) est un outil permettant de créer automatiquement des points virtuels le long des surfaces d'eaux afin de créer des modèles numériques cohérents avec les modèles hydrologiques. Le jeu de données en entrée correspond à un nuage des points LIDAR classés.

## Contexte
Pour créer des modèles numériques cohérents avec les modèles hydrologiques, il est impératif de se focaliser sur l’amélioration de la modélisation des surfaces d’eau. ​

Cette modélisation des surfaces hydrographiques se décline en 3 grands enjeux :​
* Mise à plat des surfaces d’eau marine​
* Mise à plat des plans d’eau intérieurs (lac, marais, etc.)​
* Mise en plan des grands cours d’eau (>5m large) pour assurer l’écoulement​. A noter que cette étape sera développée en premier.

## Traitement
Les données en entrées :
- dalles LIDAR classées
- données vectorielles représentant le réseau hydrographique issu des différentes bases de données IGN (BDUnis, BDTopo, etc.)

Trois grands axes du processus à mettre en place en distanguant l'échelle de traitmeent associé :
1- Création de masques hydrographiques à l'échelle de la dalle LIDAR
2- Création de masques hydrographiques pré-filtrés à l'échelle du chantier, soit :
* la suppression de ces masques dans les zones ZICAD/ZIPVA
* la suppression des aires < 150 m²
* la suppression des aires < 1000 m² hors BD IGN (grands cours d'eaux > 5m de large)

3- Création de points virtuels le long de deux entités hydrographiques :
* ##### Grands cours d'eaux (> 5 m de large dans la BD Unis).
Il existe plusieurs étapes intermédiaires : 
1- création automatique du tronçon hydrographique ("Squelette hydrographique", soit les tronçons hydrographiques dans la BD Unid) à partir de l'emprise du masque hydrographique "écoulement" apparaier, contrôler et corriger par la "production" (SV3D) en amont (étape manuelle) 
2- Analyse de la répartition en Z de l'ensemble des points LIDAR "Sol"
3- Créations de points virtuels nécéssitant plusieurs étapes intermédiaires : 
* Associer chaque point virtuel 2D au point le plus proche du squelette hydrographique
* Traitement "Z" du squelette : 
    * Analyser la répartition en Z de l’ensemble des points LIDAR extrait à l’étape précédente afin d’extraire une seule valeur d’altitude au point fictif Z le plus proche du squelette hydrographique. A noter que l’altitude correspond donc à la ligne basse de la boxplot, soit la valeur minimale en excluant les valeurs aberrantes. Pour les ponts, une étape de contrôle de la classification pourrait être mise en place
    * Lisser les Z le long du squelette HYDRO pour assurer l'écoulement
* Création des points virtuels 2D tous les 0.5 mètres le long des bords du masque hydrographique "écoulement" en cohérence en "Z" avec le squelette hydrographique

* ##### Surfaces planes (mer, lac, étang, etc.)
Pour rappel, l'eau est considérée comme horizontale sur ce type de surface.
Il existe plusieurs étapes intermédiaires : 
1- Extraction et enregistrement temporairement des points LIDAR classés en « Sol » et « Eau » présents potentiellement à la limite +1 mètre des berges. Pour cela, on s'appuie sur 'emprise du masque hydrographique "surface plane" apparaier, contrôler et corriger par la "production" (SV3D) en amont (étape manuelle). a noter que pur le secteur maritime (Mer), il faut exclure la classe « 9 » (eau) afin d’éviter de mesurer les vagues.
2- Analyse statisque de l'ensemble des points LIDAR "Sol / Eau" le long des côtes/berges afin d'obtenir une surface plane. L’objectif est de créer des points virtuels spécifiques avec une information d'altitude (m) tous les 0.5 m sur les bords des surfaces maritimes et des plans d’eaux à partir du masque hydrographique "surface plane". Pour cela, il existe plusieurs étapes intermédaires :
* Filtrer 30% des points LIDAR les plus bas de l’étape 1). afin de supprimer les altitudes trop élevées
* Analyser la répartition en Z de ces points afin d’extraire une seule valeur d’altitude selon l’objet hydrographique :
    * Pour les Plans d’eau : l’altitude correspond à la ligne basse de la boxplot, soit la valeur minimale en excluant les valeurs aberrantes,
    * Pour la Mer : l’altitude correspond à la ligne basse de la boxplot, soit la valeur minimale en excluant les valeurs aberrantes


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

## Contribuer
Installer pre-commit
```
pre-commit install
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


## Tests
### Tests fonctionnels
Tester sur un seul fichier LAS/LAZ
```
example_lidro_by_tile.sh
```

Tester sur un dossier
```
example_lidro_default.sh
```

### Tests unitaires
Pour lancer les tests :
```
python -m pytest -s
```
