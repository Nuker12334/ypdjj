import requests
import random
import string
import time

PASSWORD = "muhameds1!@$"

def generate_roblox_account():
    session = requests.Session()

    # Get CSRF token
    session.post("https://auth.roblox.com/v2/logout")
    xsrf_token = session.headers.get('x-csrf-token')
    if not xsrf_token:
        return None

    username = ''.join(random.choices(string.ascii_lowercase, k=8)) + str(random.randint(100, 999))
    email = f"{username}@gmail.com"

    signup_data = {
        "username": username,
        "password": PASSWORD,
        "birthDay": 15,
        "birthMonth": 1,
        "birthYear": 2005,
        "gender": 2,
        "email": email,
        "agreementIds": [1, 2, 3, 4]
    }
    headers = {"X-CSRF-TOKEN": xsrf_token}
    response = session.post("https://auth.roblox.com/v2/signup", json=signup_data, headers=headers)
    if response.status_code != 200:
        return None

    # Login to get .ROBLOSECURITY cookie
    login_data = {"ctype": "Username", "cvalue": username, "password": PASSWORD}
    login_resp = session.post("https://auth.roblox.com/v2/login", json=login_data)
    if login_resp.status_code != 200:
        return None

    roblosec = None
    for cookie in session.cookies:
        if cookie.name == ".ROBLOSECURITY":
            roblosec = cookie.value
            break

    return {
        "username": username,
        "password": PASSWORD,
        "email": email,
        "cookie": roblosec,
        "type": "roblox"
    }
