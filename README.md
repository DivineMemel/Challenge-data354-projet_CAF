# Challenge_Data354

Ce projet est un scraper de données LinkedIn qui automatise le processus de connexion à LinkedIn, de défilement des publications et de collecte de données sur les publications liées à des mots-clés spécifiques. Le script utilise Selenium pour l'automatisation web et BeautifulSoup pour l'analyse du contenu HTML.

## Prérequis

- Python 3.x
- Navigateur Google Chrome
- ChromeDriver
- `pip` (gestionnaire de paquets Python)

## Installation

1. **Cloner le dépôt :**

    ```bash
    git clone git@github.com:DivineMemel/Challenge-data354-projet_CAF.git
    cd Challenge-data354-projet_CAF
    ```

2. **Installer les paquets Python requis**


3. **Configurer les variables d'environnement :**

    Créez un fichier `.env` à la racine du projet et ajoutez vos identifiants LinkedIn :

    ```plaintext
    LINKEDIN_EMAIL=votre_email@example.com
    LINKEDIN_PASSWORD=votre_mot_de_passe
    ```

## Utilisation

1. **Exécuter le script directement dans l'environnement jupyter :**

    ```bash
    scrapping-data.ipynb
    ```

2. **Connexion manuelle :**

    Le script ouvrira une fenêtre du navigateur Chrome et naviguera vers la page de connexion LinkedIn. Vous devrez vous connecter manuellement. Après vous être connecté, appuyez sur Entrée dans le terminal pour continuer.

3. **Collecte de données :**

    Le script défilera ensuite les publications LinkedIn liées aux mots-clés spécifiés et collectera des données sur chaque publication, y compris le contenu, les likes, les commentaires, l'auteur, et plus encore.

## Fonctions

- `random_pause(min_time=2, max_time=5)`: Simule un comportement humain avec des pauses aléatoires.
- `simulate_random_click(driver)`: Simule un clic aléatoire sur la page pour éviter la détection.
- `save_cookies(driver, file_path)`: Sauvegarde les cookies dans un fichier.
- `load_cookies(driver, file_path)`: Charge les cookies depuis un fichier.
- `login_with_cookies(driver, cookie_file)`: Se connecte à LinkedIn en utilisant des cookies.
- `scroll_and_collect_posts(keyword)`: Défile les publications et collecte des données.

## Mots-clés

Le script recherche des publications liées aux mots-clés suivants :

- Cyberattaques Afrique
- Protection des données en IA en Afrique
- Régulations IA et cybersécurité en Afrique
- Surveillance basée sur l’IA en Afrique
- Startups africaines dans l’IA et la cybersécurité
- Inégalités numériques et risques de cyberattaques
- Ethique et confidentialité dans l’IA africaine
- Cyberéducation en Afrique
- Partenariats internationaux pour la cyber-résilience africaine
- cyber africa forum

## Remarques

- Assurez-vous que vos identifiants LinkedIn sont stockés de manière sécurisée et ne sont pas codés en dur dans le script.
- Utilisez ce script de manière responsable et conformément aux conditions d'utilisation de LinkedIn.

## Auteur

Yrilice Memel
```