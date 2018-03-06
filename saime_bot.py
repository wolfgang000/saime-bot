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
PAYMENT_URL = "https://tramites.saime.gob.ve/index.php?r=pago/pago/formpago"
EXPRESS_URL = "https://tramites.saime.gob.ve/index.php?r=inicio/inicio/agilizacion"


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
	table_node = tree.xpath('//table')
	row_data = get_table_row(table_node[0])
	return {
		'ci': row_data[0], 
		'full_name': row_data[1],
		'sex': row_data[2],
		'birth_date': row_data[3]
	}

def get_table_row(table_node):
	rows = table_node.xpath("tr")
	first_row = rows[1]
	data_row = first_row.xpath("td/text()")
	return data_row

def get_payload_from_form(form_node):
	input_nodes = form_node.xpath("input")
	payload = {}
	for input_node in input_nodes:
		payload[input_node.name] = input_node.value
	return payload


def main():
	session_requests = requests.session()

	payload = {
		"LoginForm[username]": USERNAME, 
		"LoginForm[password]": PASSWORD, 
		"g-recaptcha-response": RECAPTCHA_TOKEN
	}

	print("Perform logged in...")
	result = session_requests.post(LOGIN_URL, data = payload, headers = dict(referer = LOGIN_URL))

	print("Checking logged in...")
	login_success = check_login(session_requests)
	if login_success:
		print("You have been successfully logged in!")

		print("Pulling user data...")
		user_data = get_user_data(session_requests)
		print(user_data)


	else:
		print("Logged in failed :( ")

    


if __name__ == '__main__':
    main()