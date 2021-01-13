
-- CREATION DE LA BASE DE DONNÉES --
-- Création du super utilisateur django
CREATE USER djangoadmin@localhost IDENTIFIED by 'django';

-- Création de la base de données 'mopga_db'
CREATE DATABASE mopga_db CHARACTER SET utf8;

-- Attribution des privilèges
GRANT ALL on mopga_db.* to djangoadmin@localhost;
flush privileges;


-- Ne pas oublier de créer un admin superuser --
-- python manage.py createsuperuser --