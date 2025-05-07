""" # filename: main.py
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import json

app = FastAPI()

# Helper function to simulate human delays
def esperar(min_s=2, max_s=5):
    time.sleep(random.uniform(min_s, max_s))

def scrape_n_reels(username: str, cantidad: int = 2):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://www.instagram.com/")
    input("🔐 Logueate manualmente en la ventana del navegador y presioná Enter acá para continuar...")

    driver.get(f"https://www.instagram.com/{username}/reels/")
    esperar(4, 6)

    reels_data = []
    cards = driver.find_elements(By.XPATH, '//a[contains(@href, "/reel/")]')[:cantidad]

    for card in cards:
        url = card.get_attribute('href')

        try:
            spans = card.find_elements(By.TAG_NAME, "span")
            views = "N/A"
            for span in spans:
                txt = span.text.replace('\u00a0', ' ').strip()
                if any(x in txt for x in ["K", "M", "mil"]):
                    views = txt
                    break
        except:
            views = "N/A"

        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[1])
        esperar(4, 6)

        try:
            wait = WebDriverWait(driver, 10)
            title = ""
            likes = "N/A"
            fecha = "N/A"
            comentarios = []

            try:
                title_elem = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                title = title_elem.text.strip()
            except:
                pass

            try:
                likes_elem = driver.find_element(By.XPATH, '//section//span[contains(text(),"Me gusta") or contains(text(),"likes")]')
                likes = likes_elem.text.strip()
            except:
                pass

            try:
                time_elem = driver.find_element(By.TAG_NAME, "time")
                fecha = time_elem.get_attribute("datetime")
            except:
                pass

            try:
                for _ in range(10):
                    driver.execute_script("window.scrollBy(0, 300);")
                    esperar(1, 2)

                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, 'li._a9zj._a9zl')) >= 1
                )

                comment_elements = driver.find_elements(By.CSS_SELECTOR, 'li._a9zj._a9zl')
                comentarios = []

                for el in comment_elements[:5]:
                    try:
                        user = el.find_element(By.CSS_SELECTOR, 'h3 a').text
                        texto = el.find_element(By.CSS_SELECTOR, 'div._a9zr > div').text
                        comentarios.append(f"{user}: {texto}")
                    except:
                        continue

            except Exception as e:
                comentarios = []

            datos_reel = {
                "url": url,
                "reproducciones": views,
                "titulo": title,
                "likes": likes,
                "fecha": fecha,
                "comentarios": comentarios
            }

            reels_data.append(datos_reel)

        except Exception as e:
            pass

        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass

    driver.quit()
    return reels_data

@app.get("/scrape")
def scrape_instagram_reels(username: str = Query(...), cantidad: int = Query(2)):
    data = scrape_n_reels(username, cantidad)
    return {"perfil": username, "cantidad": cantidad, "reels": data}
 """

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

app = FastAPI()

# ✅ CORS habilitado para todos los orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def esperar(min_s=2, max_s=4):
    time.sleep(random.uniform(min_s, max_s))

def scrape_n_reels(username: str, cantidad: int = 2):
    options = webdriver.ChromeOptions()

    # 🧠 Usamos el mismo perfil persistente que en el .bat
    options.add_argument("--user-data-dir=C:/Users/LEBROT/Desktop/scraper-api/chrome_profile")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.instagram.com/{username}/reels/")
    esperar(4, 6)

    reels_data = []
    cards = driver.find_elements(By.XPATH, '//a[contains(@href, "/reel/")]')[:cantidad]

    if not cards:
        print("⚠ No se encontraron reels. ¿Estás logueado en Instagram en este perfil?")
        driver.quit()
        return []

    for card in cards:
        url = card.get_attribute('href')
        views = "N/A"

        try:
            spans = card.find_elements(By.TAG_NAME, "span")
            for span in spans:
                txt = span.text.replace('\u00a0', ' ').strip()
                if any(x in txt for x in ["K", "M", "mil"]):
                    views = txt
                    break
        except:
            pass

        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[1])
        esperar(4, 6)

        title = ""
        likes = "N/A"
        fecha = "N/A"
        comentarios = []

        try:
            title_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            title = title_elem.text.strip()
        except:
            pass

        try:
            likes_elem = driver.find_element(By.XPATH, '//section//span[contains(text(),"Me gusta") or contains(text(),"likes")]')
            likes = likes_elem.text.strip()
        except:
            pass

        try:
            time_elem = driver.find_element(By.TAG_NAME, "time")
            fecha = time_elem.get_attribute("datetime")
        except:
            pass

        try:
            for _ in range(10):
                driver.execute_script("window.scrollBy(0, 300);")
                esperar(1, 2)

            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, 'li._a9zj._a9zl')) >= 1
            )

            comment_elements = driver.find_elements(By.CSS_SELECTOR, 'li._a9zj._a9zl')
            for el in comment_elements[:5]:
                try:
                    user = el.find_element(By.CSS_SELECTOR, 'h3 a').text
                    texto = el.find_element(By.CSS_SELECTOR, 'div._a9zr > div').text
                    comentarios.append(f"{user}: {texto}")
                except:
                    continue
        except:
            comentarios = []

        reels_data.append({
            "url": url,
            "reproducciones": views,
            "titulo": title,
            "likes": likes,
            "fecha": fecha,
            "comentarios": comentarios
        })

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    driver.quit()
    return reels_data

@app.get("/scrape")
def scrape_instagram_reels(username: str = Query(...), cantidad: int = Query(2)):
    return {
        "perfil": username,
        "cantidad": cantidad,
        "reels": scrape_n_reels(username, cantidad)
    }


#--user-data-dir=C:\Users\LEBROT\Desktop\scraper-api\chrome_profile