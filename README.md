# Mon Super Blog (Chapitre 12 - Django)

Projet complet des parties 1 à 6 : inscription/connexion, CRUD des articles,
commentaires, CSS, page de profil et pagination.

## Lancer le projet dans VS Code

1. Ouvrir le dossier `monblogprojet` (Fichier > Ouvrir le dossier).
2. Ouvrir un terminal et créer l'environnement virtuel :

        python -m venv env
        env\Scripts\activate          (Windows)
        source env/bin/activate       (Linux / Mac)

3. Installer Django :

        pip install -r requirements.txt

4. Créer la base de données (les migrations sont déjà dans le dossier) :

        python manage.py migrate

5. Créer un superutilisateur :

        python manage.py createsuperuser

6. Lancer le serveur :

        python manage.py runserver

   Puis aller sur http://127.0.0.1:8000/ (et /admin/ pour l'administration).

## Tests

    python manage.py test
