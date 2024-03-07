Lidro (Applanissement des surfaces d'eaux) est un outil permettant de créer des points virtuels le long des surfaces d'eaux afin de créer des modèles numériques cohérent avec les modèles hydrologiques. Le jeu de données en entrée correspond à un nuage de point lidar classifiés.

## Installation des dépendances (conda)
pré-requis: installer Mamba

```
mamba env update -n lidro -f environment.yml
conda activate lidro
```

## Base de données sur la machine virtuelle "10.128.38.194"
#### Pré-requis :
- PostGresSQL 16 installé
- configuré le fichier "pg_hba.conf" en ajoutant les lignes suivantes :
```
# taper
vim pg_hba.conf
```
```
# connection integrateur
host         all      mdupays     10.0.0.0/8      scram-sha-256
host         all      mdupays     172.16.0.0/12   scram-sha-256
host         all      mdupays    192.168.0.0/16  scram-sha-256
```
- configuré le fichier "postgresql.conf" en configurant les  lignes suivantes :
```
# taper
vim postgresql.conf
```

```
#  - Connection Settings -
listen_adresses = '*"

port = 5432

# - Authentification -
password_encryption = scram-sha-256
```

#### Base de donnée

1. Vérifier l'état du service PostgresSQL, indiquant s'il est en cours d'exécution, arrêté ou s'il rencontre des erreurs.
```
systemctl status postgresql
```

2. Se connecter à PostGresSQL
```
su postgres

psql
```

3. Pour recharger la configuration de PostgreSQL sans avoir à redémarrer le serveur. Cela permet d'appliquer les modifications apportées au fichier de configuration postgresql.conf et à d'autres fichiers de configuration sans interrompre le service PostgreSQL.
```
# taper
SQL SELECT pg_reload_conf();
```

4. Créer la base de données "dev_hydro" et définir les utilisateurs sur dev_hydro
```
CREATE DATABASE dev_hydro;
CREATE USER "MDupays" WITH LOGIN PASSWORD 'test';
GRANT ALL ON DATABASE dev_hydro TO "MDupays";
```
/ ! \ pour se connecter à la base de données "dev_hydro"
```
psql -h 10.128.38.94 -d dev_hydro
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