import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import string
import time
import capsolver

# ========== CAPSOLVER API KEY ==========
capsolver.api_key = "sprnxz-3dbf6c1c-fdd0-8a9a-4544-a37c4b42bbcc"
# ========================================

def solve_hcaptcha(site_key, page_url):
    solution = capsolver.solve({
        "type": "HCaptchaTaskProxyless",
        "websiteURL": page_url,
        "websiteKey": site_key,
    })
    return solution.get("gRecaptchaResponse")

def generate_discord_account():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)

    try:
        driver.get("https://discord.com/register")
        wait = WebDriverWait(driver, 10)

        email = ''.join(random.choices(string.ascii_lowercase, k=10)) + "@gmail.com"
        username = ''.join(random.choices(string.ascii_lowercase, k=8)) + str(random.randint(1, 99))
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + "!A1"

        wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(email)
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)

        # Birthday
        driver.find_element(By.XPATH, "//select[@aria-label='Month']").send_keys("January")
        driver.find_element(By.XPATH, "//select[@aria-label='Day']").send_keys("15")
        driver.find_element(By.XPATH, "//select[@aria-label='Year']").send_keys("1990")

        # Click continue
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        time.sleep(3)

        # Extract sitekey and solve captcha
        site_key = driver.execute_script(
            "return document.querySelector('[data-sitekey]')?.getAttribute('data-sitekey')"
        )
        if not site_key:
            site_key = "f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34"  # Discord's known sitekey

        captcha_token = solve_hcaptcha(site_key, driver.current_url)
        if captcha_token:
            driver.execute_script(
                f"document.querySelector('textarea[name=\"h-captcha-response\"]').innerHTML = '{captcha_token}';"
            )
            driver.execute_script("window.captchaCallback && window.captchaCallback();")

        # Wait for successful creation
        wait.until(EC.url_contains("/channels/"))
        token = driver.execute_script("return window.localStorage.token;")

        return {
            "email": email,
            "password": password,
            "username": username,
            "token": token,
            "type": "discord"
        }
    except Exception as e:
        print(f"Discord error: {e}")
        return None
    finally:
        driver.quit()
