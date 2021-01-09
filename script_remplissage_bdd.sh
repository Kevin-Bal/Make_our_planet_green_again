#!/bin/bash

# Pour enregistrer les données dans les fichiers fixture
# python mopga/manage.py dumpdata auth > mopga/fixture/data_auth.json
# python mopga/manage.py dumpdata users.Profile > mopga/fixture/data_profils.json
# python mopga/manage.py dumpdata plateforme.Projet > mopga/fixture/data_projets.json
# python mopga/manage.py dumpdata plateforme.Evaluation > mopga/fixture/data_contributions.json
# python mopga/manage.py dumpdata plateforme.Contribution > mopga/fixture/data_evaluations.json


# Pour charger les données des fixtures dans la base de données
# L'ordre est important !
python mopga/manage.py loaddata mopga/fixture/data_auth.json
python mopga/manage.py loaddata mopga/fixture/data_profils.json
python mopga/manage.py loaddata mopga/fixture/data_projets.json
python mopga/manage.py loaddata mopga/fixture/data_contributions.json
python mopga/manage.py loaddata mopga/fixture/data_evaluations.json