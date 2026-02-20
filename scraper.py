import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ================= SETTINGS =================
page_number = 63
MAIN_URL = "https://njavtv.com/en/actresses?page=" + str(page_number)
PROXY_URL = "https://proxyorb.com/"
SAVE_FOLDER = "pornstars"

# ================= CREATE SAVE FOLDER =================
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# ================= CHROME OPTIONS =================
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# Auto install correct ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

try:
    # ================= OPEN PROXY =================
    driver.get(PROXY_URL)
    time.sleep(3)

    url_input = wait.until(
        EC.presence_of_element_located((By.NAME, "input"))
    )

    url_input.clear()
    url_input.send_keys(MAIN_URL)

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()

    time.sleep(5)

    # Close popup if exists
    try:
        skip_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Skip')]"))
        )
        skip_btn.click()
    except:
        pass

    time.sleep(5)

    # ================= PAGINATION LOOP =================
    while True:
        print(f"Processing Page {page_number}...")

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        links = driver.find_elements(
            By.XPATH,
            "//h4[@class='text-nord13 truncate']/ancestor::a"
        )

        profile_urls = []

        for link in links:
            url = link.get_attribute("href")
            if url and url not in profile_urls:
                profile_urls.append(url)

        print(f"Found {len(profile_urls)} profiles")

        main_tab = driver.current_window_handle

        for profile_url in profile_urls:
            try:
                driver.execute_script("window.open(arguments[0]);", profile_url)
                driver.switch_to.window(driver.window_handles[-1])

                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(2)

                try:
                    name = wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "h4"))
                    ).text.strip()
                except:
                    name = "unknown"

                invalid_chars = r'<>:"/\|?*'
                for char in invalid_chars:
                    name = name.replace(char, "")

                file_path = os.path.join(SAVE_FOLDER, f"{name}.txt")

                counter = 1
                original_name = name
                while os.path.exists(file_path):
                    name = f"{original_name}_{counter}"
                    file_path = os.path.join(SAVE_FOLDER, f"{name}.txt")
                    counter += 1

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)

                print(f"Saved: {file_path}")

                driver.close()
                driver.switch_to.window(main_tab)

            except Exception as e:
                print("Error:", e)
                driver.switch_to.window(main_tab)
                continue

        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
            next_url = next_btn.get_attribute("href")

            if not next_url:
                break

            driver.get(next_url)
            page_number += 1
            time.sleep(3)

        except:
            break

finally:
    driver.quit()

print("All done!")
