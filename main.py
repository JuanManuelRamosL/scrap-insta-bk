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
    # options.add_argument("--user-data-dir=C:/Users/LEBROT/Desktop/scraper-api/chrome_profile")
    # options.add_argument("--start-maximized")
    options = webdriver.ChromeOptions()
    import os
    profile_path = os.path.expanduser("~/Desktop/scraper-api/chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
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
    } """

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
import uuid
import whisper
import yt_dlp

app = FastAPI()

# ✅ CORS habilitado para todos los orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

modelo_whisper = whisper.load_model("base")

def esperar(min_s=2, max_s=4):
    time.sleep(random.uniform(min_s, max_s))

def transcribir_audio_desde_video(url):
    temp_filename = f"temp_{uuid.uuid4()}.mp4"

    try:
        ydl_opts = {
            'outtmpl': temp_filename,
            'format': 'mp4',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        result = modelo_whisper.transcribe(temp_filename)
        return result.get("text", "").strip()

    except Exception as e:
        print(f"Error al transcribir {url}: {e}")
        return ""

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

def scrape_n_reels(username: str, cantidad: int = 2):
    options = webdriver.ChromeOptions()
    profile_path = os.path.expanduser("~/Desktop/scraper-api/chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
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

        transcripcion = transcribir_audio_desde_video(url)

        reels_data.append({
            "url": url,
            "reproducciones": views,
            "titulo": title,
            "likes": likes,
            "fecha": fecha,
            "comentarios": comentarios,
            "transcripcion": transcripcion
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



#PUBLICACIONES

@app.get("/scrape-posts")
def scrape_instagram_posts(username: str = Query(...), cantidad: int = Query(3)):
    options = webdriver.ChromeOptions()
    profile_path = os.path.expanduser("~/Desktop/scraper-api/chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.instagram.com/{username}/")
    esperar(5, 7)

    posts_data = []
    cards = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')[:cantidad]

    if not cards:
        print("⚠ No se encontraron publicaciones.")
        driver.quit()
        return []

    for card in cards:
        url = card.get_attribute('href')

        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[1])
        esperar(4, 6)

        title = ""
        likes = "N/A"
        fecha = "N/A"
        comentarios = []
        transcripcion = ""
        reproducciones = "N/A"
        tipo = "imagen"

        try:
            # ¿Es video?
            is_video = len(driver.find_elements(By.TAG_NAME, "video")) > 0
            if is_video:
                tipo = "video"

            # Título
            try:
                title_elem = driver.find_element(By.XPATH, '//div[contains(@class,"_a9zs")]/span')
                title = title_elem.text.strip()
            except:
                pass

            # Likes
            try:
                likes_elem = driver.find_element(By.XPATH, '//section//span[contains(text(),"Me gusta") or contains(text(),"likes")]')
                likes = likes_elem.text.strip()
            except:
                pass

            # Fecha
            try:
                time_elem = driver.find_element(By.TAG_NAME, "time")
                fecha = time_elem.get_attribute("datetime")
            except:
                pass

            # Comentarios
            try:
                for _ in range(5):
                    driver.execute_script("window.scrollBy(0, 200);")
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

            # Reproducciones si es video
            if is_video:
                try:
                    view_elem = driver.find_element(By.XPATH, '//section//span[contains(text(),"reproducciones") or contains(text(),"views")]')
                    reproducciones = view_elem.text.strip()
                except:
                    reproducciones = "N/A"

                transcripcion = transcribir_audio_desde_video(url)

        except Exception as e:
            print(f"⚠ Error en {url}: {e}")

        posts_data.append({
            "url": url,
            "tipo": tipo,
            "titulo": title,
            "likes": likes,
            "reproducciones": reproducciones if tipo == "video" else None,
            "fecha": fecha,
            "comentarios": comentarios,
            "transcripcion": transcripcion if tipo == "video" else None
        })

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    driver.quit()
    return {"perfil": username, "cantidad": cantidad, "posts": posts_data}


#--user-data-dir=C:\Users\LEBROT\Desktop\scraper-api\chrome_profile
# pip install git+https://github.com/openai/whisper.git
# https://www.gyan.dev/ffmpeg/builds/  de ahi instalar  ffmpeg-release-full.7z  descomprimirlo y agregarlo al path del sistema
# Forma de usar 
# poner este comando en la cmd = start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="C:\Users\ezequ\Desktop\scraper-api\chrome_profile" https://www.instagram.com/
# te va a abrir una ventana de chrome te logueas con 
# juanm@agencialebrot.com
# psw = Juanma42680
# y despues te logueas en instgram con user: ezepruebaslb y psw: juanma42680  


#endpoint de prueba GET : http://localhost:8000/scrape?username=leomessi&cantidad=1
#uvicorn main:app --reload
