#!/bin/bash

echo "***** Début du script *****"

echo "#### Installation des dépendances : ####"
pip install -r mopga/requirements.txt
echo -e "----------------------------------------------------\n\n"


echo "Création de la base de données MOPGA : "
mysql -u root -p < creation_mopga_db.sql
echo -e "----------------------------------------------------\n\n"


echo "Remplissage de la base de données : "
bash script_remplissage_bdd.sh
echo -e "----------------------------------------------------\n\n"


echo "Application des migrations : "
python mopga/manage.py makemigrations
python mopga/manage.py migrate
echo -e "----------------------------------------------------\n\n"

echo "***** Fin du script ******"
