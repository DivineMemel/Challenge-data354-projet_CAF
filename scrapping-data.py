from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import re
import csv
import os
from datetime import datetime, timedelta
import random
from bs4 import BeautifulSoup as bs
from dateutil.relativedelta import relativedelta
import logging
import traceback
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fonction pour simuler un comportement humain avec des pauses aléatoires
def random_pause(min_time=2, max_time=5):
    time.sleep(random.uniform(min_time, max_time))

# Simule un clic sur une zone aléatoire pour "flouter"
def simulate_random_click(driver):
    try:
        elements = driver.find_elements(By.TAG_NAME, "a")
        if elements:
            random.choice(elements).click()
            logging.info("Clic aléatoire simulé.")
            random_pause(3, 5)
    except Exception as e:
        logging.warning(f"Aucune zone trouvée pour clic aléatoire : {e}")

# Chargement des variables d'environnement
load_dotenv()
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    raise ValueError("Les identifiants LinkedIn sont manquants dans le fichier .env")

# Fonction pour se connecter à LinkedIn
def login_linkedin(driver):
    logging.info("Début de la connexion à LinkedIn.")
    driver.get("https://www.linkedin.com/login/fr")
    try:
        email = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "username")))
        email.send_keys(LINKEDIN_EMAIL)
        password = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys(LINKEDIN_PASSWORD)
        time.sleep(3)
        password.send_keys(Keys.RETURN)
        WebDriverWait(driver, 20).until(EC.url_contains("feed"))
        logging.info("Connexion à LinkedIn réussie.")
    except Exception as e:
        logging.error(f"Erreur lors de la connexion : {e}")
        raise

# Fonction pour nettoyer le texte (suppression emojis, urls, @, #)
def clean_text(text):
    emoji_pattern = re.compile(
    "["
    u"\U0001F600-\U0001F64F"  
    u"\U0001F300-\U0001F5FF"  
    u"\U0001F680-\U0001F6FF" 
    u"\U0001F700-\U0001F77F"  
    u"\U0001F780-\U0001F7FF"  
    u"\U0001F800-\U0001F8FF"  
    u"\U0001F900-\U0001F9FF"  
    u"\U0001FA00-\U0001FA6F"  
    u"\U0001FA70-\U0001FAFF"  
    u"\U00002700-\U000027BF"  
    u"\U00002600-\U000026FF"
    "]+", flags=re.UNICODE
    )

    text = emoji_pattern.sub(r'', text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = " ".join(text.split())
    return text

# Fonction pour effectuer une recherche de mots-clés
def search_keyword(driver, keyword):
    logging.info(f"Recherche pour le mot-clé : {keyword}")
    try:
        search_input = WebDriverWait(driver, 40).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input.search-global-typeahead__input"))
        )
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.RETURN)
    
        try:
            see_all_posts = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Voir tous les résultats de posts"))
            )
            see_all_posts.click()
        except Exception as e:
            logging.warning(f"Pas de lien 'Voir tous les résultats de posts' trouvé: {e}")
            pass

        start = time.time()
        now = datetime.now()
        lastHeight = driver.execute_script("return document.body.scrollHeight")

        while True:
            see_more_elements = driver.find_elements(By.XPATH, "//span[text()='… plus']")
            for element in see_more_elements:
                try:
                     driver.execute_script("arguments[0].click();", element)
                     time.sleep(1)
                except Exception as e:
                    logging.warning(f"Erreur lors du clic sur '… plus' : {e}")

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(7)
            newHeight = driver.execute_script("return document.body.scrollHeight")

            if newHeight == lastHeight:
                break
            lastHeight = newHeight

            if round(time.time() - start) > 300:
                break

        result = driver.page_source
        soup = bs(result.encode("utf-8"), "html.parser")

        posts = soup.find_all('div', class_='occludable-update')
        articles_data = []

        for post in posts:
            try:
                author_element = post.find('span', class_='update-components-actor__name')
                content_element = post.find('span', class_='break-words tvm-parent-container')
                date_element = post.find('span', class_='update-components-actor__sub-description')
                likes_element = post.find('span', class_='social-details-social-counts__reactions-count')
                comments_element = post.find('span', string=re.compile('commentaire|commentaires'))
                shares_element = post.find('span', class_='social-details-social-counts__item--truncate-text')


                author = author_element.get_text(strip=True).split()[0] if author_element else None
                content = clean_text(content_element.get_text(strip=True)) if content_element else None
                likes = likes_element.get_text(strip=True) if likes_element else "0"
                shares = shares_element.get_text(strip=True).split()[0] if shares_element else "0"
                comments = comments_element.get_text(strip=True).split()[0] if comments_element else "0"

                date = date_element.get_text().strip() if date_element else None
                if date:
                    if 'il y a' not in date:
                        if 'j' in date:
                            days = int(re.search(r'(\d+)\s*j', date).group(1))
                            new_date = (now - timedelta(days=days)).strftime('%Y-%m-%d')
                        elif 'h' in date:
                            hours = int(re.search(r'(\d+)\s*h', date).group(1))
                            new_date = (now - timedelta(hours=hours)).strftime('%Y-%m-%d')
                        elif 'sem.' in date:
                            weeks = int(re.search(r'(\d+)\s*sem\.', date).group(1))
                            new_date = (now - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
                        elif 'mois' in date:
                            months = int(re.search(r'(\d+)\s*mois', date).group(1))
                            new_date = (now - relativedelta(months=months)).strftime('%Y-%m-%d')
                        else:
                            new_date = date # Conserve la date si le format n'est pas reconnu
                    else:
                        new_date = None # Ignore les dates avec 'il y a'
                else:
                    new_date = None # Date non trouvée
    
                articles_data.append({
                    'author': author,
                    'content': content,
                    'date': new_date,
                    'likes': likes,
                    'comments': comments,
                    'shares': shares
                })
            except Exception as e:
                logging.warning(f"Erreur lors de l'extraction des données d'un post : {e}\n{traceback.format_exc()}")

        return articles_data
    except Exception as e:
        logging.error(f"Erreur lors de la recherche du mot-clé : {keyword} : {e}\n{traceback.format_exc()}")
        return []

# Fonction pour écrire les données dans un fichier CSV
def write_to_csv(data, filename="linkedin_posts.csv"):
    logging.info(f"Écriture des données dans le fichier CSV: {filename}")
    if not data:
        logging.warning("Pas de données à écrire dans le fichier CSV.")
        return
    
    try:
        file_exists = os.path.isfile(filename)

        with open(filename, 'a', encoding='utf-8', newline='') as csvfile:
            fieldnames = ['author', 'content', 'date', 'likes', 'comments', 'shares']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
            if not file_exists:
                writer.writeheader()  # Ecrire l'en-tête si le fichier n'existe pas

            for row in data:
                writer.writerow(row)

        logging.info(f"Données écrites avec succès dans {filename}")
    except Exception as e:
         logging.error(f"Erreur lors de l'écriture du fichier CSV : {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    # Configuration du navigateur
    chrome_options = Options()
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        login_linkedin(driver)

        keywords = [
            "Cyberattaques automatisées sur le continent",
            "Protection des données en IA en Afrique",
            "Régulations IA et cybersécurité en Afrique",
            "Surveillance basée sur l’IA en Afrique",
            "Startups africaines dans l’IA et la cybersécurité",
            "Inégalités numériques et risques de cyberattaques",
            "Ethique et confidentialité dans l’IA africaine",
            "Cyberéducation en Afrique",
            "Partenariats internationaux pour la cyber-résilience africaine",
            "cyber africa forum",
        ]
        
        all_data = []
        for keyword in keywords:
           articles = search_keyword(driver, keyword)
           all_data.extend(articles)

        write_to_csv(all_data)

    except Exception as e:
        logging.error(f"Erreur globale lors de l'exécution : {e}\n{traceback.format_exc()}")

    finally:
        driver.quit()
        logging.info("Fermeture du navigateur.")