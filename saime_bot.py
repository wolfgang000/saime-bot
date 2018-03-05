import requests
from lxml import html
import configparser

config = configparser.ConfigParser()
config.read('USER_CREDENTIAL.INI')

USERNAME = config['DEFAULT']['USERNAME']
PASSWORD = config['DEFAULT']['PASSWORD']
RECAPTCHA_TOKEN = ""

LOGIN_URL = "https://tramites.saime.gob.ve/index.php?r=site/login"
HOME_URL = "https://tramites.saime.gob.ve/index.php?r=tramite/tramite/"


def check_login(session_requests):
    result = session_requests.get(HOME_URL, headers = dict(referer = HOME_URL))
    tree = html.fromstring(result.content)
    try:
        login_form = tree.get_element_by_id('login-form')
        return False
    except KeyError:
        return True


def get_user_data(session_requests):
    result = session_requests.get(HOME_URL, headers = dict(referer = HOME_URL))
    tree = html.fromstring(result.content)
    try:
        login_form = tree.get_element_by_id('login-form')
        return False
    except KeyError:
        return True

def get_table_row(table_node):
    return None



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