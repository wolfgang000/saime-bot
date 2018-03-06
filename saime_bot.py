import requests
from lxml import html
import configparser

config = configparser.ConfigParser()
config.read('USER_CREDENTIAL.INI')

USERNAME = config['DEFAULT']['USERNAME']
PASSWORD = config['DEFAULT']['PASSWORD']
RECAPTCHA_TOKEN = ""


class UserApi():
	BASE_URL = "https://tramites.saime.gob.ve/"
	LOGIN_URL = "https://tramites.saime.gob.ve/index.php?r=site/login"
	HOME_URL = "https://tramites.saime.gob.ve/index.php?r=tramite/tramite/"
	PAYMENT_URL = "https://tramites.saime.gob.ve/index.php?r=pago/pago/formpago"
	EXPRESS_URL = "https://tramites.saime.gob.ve/index.php?r=inicio/inicio/agilizacion"

	def __init__(self, username, password):
		self.session_requests = requests.session()
		self.username = username
		self.password = password

	def is_site_up(self):
		result = self.session_requests.get(self.BASE_URL, headers = dict(referer = self.BASE_URL))
		if result.status_code == 200:
			return True
		else:
			return False

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
		if response.status_code == 502:
			raise self.SiteIsDown()
		elif response.status_code == 302:
			return True
		else:
			return False
	
	def check_login(self):
		response = self.session_requests.get(self.HOME_URL, headers = dict(referer = self.HOME_URL))
		if response.status_code == 502:
			raise self.SiteIsDown()

		tree = html.fromstring(response.content)
		try:
			tree.get_element_by_id('login-form')
			return False
		except KeyError:
			return True	

	def get_user_data(self):
		result = self.session_requests.get(self.HOME_URL, headers = dict(referer = self.HOME_URL))
		if result.status_code == 502:
			raise self.SiteIsDown()
		
		tree = html.fromstring(result.content)
		table_node = tree.xpath('//table')
		row_data = self._get_first_row_from_table(table_node[0])
		return {
			'ci': row_data[0], 
			'full_name': row_data[1],
			'sex': row_data[2],
			'birth_date': row_data[3]
		}
	
	def get_payment_form(self):
		print("start payment")
		response = self.session_requests.get(self.EXPRESS_URL, headers = dict(referer = self.EXPRESS_URL))
		if response.status_code == 502:
			raise self.SiteIsDown()
		tree = html.fromstring(response.content)
		form_node = tree.get_element_by_id("pago-form")
		payload = self._get_payload_from_form(form_node)
		response = self.session_requests.post(
			self.PAYMENT_URL, 
			data = payload, 
			headers = dict(referer = self.PAYMENT_URL)
		)
		if response.status_code == 502:
			raise self.SiteIsDown()
		print("status:",response.status_code)
		print("headers:",response.headers)
		print("content:",response.content)
	

	def _is_payment_form_enable(self, site_text):
		error_msg = "Estimado ciudadano, le invitamos a acceder a la solicitud de prórroga de pasaporte en Venezuela,"
		if error_msg in site_text:
			return False
		else:
			return True


	def _get_first_row_from_table(self, table_node):
		rows = table_node.xpath("tr")
		first_row = rows[1]
		data_row = first_row.xpath("td/text()")
		return data_row

	def _get_payload_from_form(self, form_node):
		input_nodes = form_node.xpath("input")
		payload = {}
		for input_node in input_nodes:
			payload[input_node.name] = input_node.value
		return payload
	
	class SiteIsDown(Exception):
		pass

	class LoginFailed(Exception):
		pass
	


def main():
	bot = UserApi(username=USERNAME, password=PASSWORD)
	

	print("Perform logged in...")
	bot.login()

	print("Checking logged in...")
	login_success = bot.check_login()
	if login_success:
		print("You have been successfully logged in!")

		print("Pulling user data...")
		user_data = bot.get_user_data()
		print(user_data)
		bot.get_payment_form()


	else:
		print("Logged in failed :( ")

    


if __name__ == '__main__':
    main()