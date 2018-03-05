import requests
from lxml import html
import configparser

config = configparser.ConfigParser()
config.read('USER_CREDENTIAL.INI')

USERNAME = config['DEFAULT']['USERNAME']
PASSWORD = config['DEFAULT']['PASSWORD']
RECAPTCHA_TOKEN = ""

LOGIN_URL = "https://tramites.saime.gob.ve/index.php?r=site/login"
URL = "https://tramites.saime.gob.ve/index.php?r=tramite/tramite/"


def check_login(session_requests):
    result = session_requests.get(URL, headers = dict(referer = URL))
    tree = html.fromstring(result.content)
    print(result.content)
    try:
        login_form = tree.get_element_by_id('login-form')
        return False
    except KeyError:
        return True


def main():
    session_requests = requests.session()

    payload = {
        "LoginForm[username]": USERNAME, 
        "LoginForm[password]": PASSWORD, 
        "g-recaptcha-response": RECAPTCHA_TOKEN
    }

    # Perform login
    result = session_requests.post(LOGIN_URL, data = payload, headers = dict(referer = LOGIN_URL))
    print("login",check_login(session_requests))

    


if __name__ == '__main__':
    main()