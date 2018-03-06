import requests
from lxml import html
import configparser

config = configparser.ConfigParser()
config.read('USER_CREDENTIAL.INI')

USERNAME = config['DEFAULT']['USERNAME']
PASSWORD = config['DEFAULT']['PASSWORD']
RECAPTCHA_TOKEN = ""


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


class Bot():
	BASE_URL = "https://tramites.saime.gob.ve/"
	LOGIN_URL = "https://tramites.saime.gob.ve/index.php?r=site/login"
	HOME_URL = "https://tramites.saime.gob.ve/index.php?r=tramite/tramite/"

	def __init__(self, username, password):
		self.session_requests = requests.session()
		self.username = username
		self.password = password

	def login(self):
		payload = {
			"LoginForm[username]": self.username, 
			"LoginForm[password]": self.password, 
			"g-recaptcha-response": ""
		}
		response = self.session_requests.post(
			self.LOGIN_URL, 
			data = payload, 
			headers = dict(referer = self.
			LOGIN_URL)
		)
		if(response.status_code == 302):
			return True
		else:
			return False
	
	def check_login(self):
		response = self.session_requests.get(self.HOME_URL, headers = dict(referer = self.HOME_URL))
		tree = html.fromstring(response.content)
		try:
			tree.get_element_by_id('login-form')
			return False
		except KeyError:
			return True	

	def get_user_data(self):
		result = self.session_requests.get(self.HOME_URL, headers = dict(referer = self.HOME_URL))
		tree = html.fromstring(result.content)
		table_node = tree.xpath('//table')
		row_data = self.__get_table_row(table_node[0])
		return {
			'ci': row_data[0], 
			'full_name': row_data[1],
			'sex': row_data[2],
			'birth_date': row_data[3]
		}
	
	def __get_table_row(self, table_node):
		rows = table_node.xpath("tr")
		first_row = rows[1]
		data_row = first_row.xpath("td/text()")
		return data_row



def main():
	bot = Bot(username=USERNAME, password=PASSWORD)
	

	print("Perform logged in...")
	bot.login()

	print("Checking logged in...")
	login_success = bot.check_login()
	if login_success:
		print("You have been successfully logged in!")

		print("Pulling user data...")
		user_data = bot.get_user_data()
		print(user_data)


	else:
		print("Logged in failed :( ")

    


if __name__ == '__main__':
    main()