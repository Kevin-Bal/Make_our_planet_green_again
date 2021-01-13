# Utilisez python 3.7 comme image parente
FROM python:3.7

# Définissez /app comme le répertoire de travail
WORKDIR /app

# Copiez le contenu du répertoire local dans /app au sein du conteneur
ADD . /app

# Installez les packages spécifiés dans requirements.txt dans le conteneur
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . /app
