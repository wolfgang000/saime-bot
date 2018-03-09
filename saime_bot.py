import requests
from lxml import html
import configparser
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read('USER_CREDENTIAL.INI')

USERNAME = config['DEFAULT']['USERNAME']
PASSWORD = config['DEFAULT']['PASSWORD']
PUSHED_APP_KEY = config['DEFAULT']['PUSHED_APP_KEY']
PUSHED_APP_SECRET = config['DEFAULT']['PUSHED_APP_SECRET']


def send_notification(msg):
	payload = {
		"app_key": PUSHED_APP_KEY,
		"app_secret": PUSHED_APP_SECRET,
		"target_type": "app",
		"content": msg
	}
	r = requests.post("https://api.pushed.co/1/push", data=payload)
	print(r.text)

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
		result = self.session_requests.get(
			self.BASE_URL, 
			headers = dict(referer = self.BASE_URL),
			timeout = 20
		)
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
			headers = dict(referer = self.LOGIN_URL),
			timeout = 20
		)
		if response.status_code == 502:
			raise self.SiteIsDown()
	
	def check_login(self):
		response = self.session_requests.get(
			self.HOME_URL, 
			headers = dict(referer = self.HOME_URL), 
			timeout = 20
		)
		if response.status_code == 502:
			raise self.SiteIsDown()
		return not self._is_login_page(response.content.decode('utf_8'))


	def get_user_data(self):
		result = self.session_requests.get(
			self.HOME_URL, 
			headers = dict(referer = self.HOME_URL),
			timeout = 20
		)
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
	
	def get_express_passport_payment_form(self):
		response = self.session_requests.get(
			self.EXPRESS_URL,
			headers = dict(referer = self.EXPRESS_URL),
			timeout = 20
		)
		if response.status_code == 502:
			raise self.SiteIsDown()
		
		tree = html.fromstring(response.content)
		form_node = tree.get_element_by_id("pago-form")
		payload = self._get_payload_from_form(form_node)
		response = self.session_requests.post(
			self.PAYMENT_URL, 
			data = payload, 
			headers = dict(referer = self.PAYMENT_URL),
			timeout = 20
		)
		if response.status_code == 502:
			raise self.SiteIsDown()
		else:
			payment_form = self._get_payment_form(response.content)
			if payment_form == None:
				raise self.PaymentFormDisabled()

			return payment_form

	def _get_payment_form(self, site_text):
		return html.fromstring(site_text).get_element_by_id("banesco-form", None)

	def _is_login_page(self, site_text):
		error_msg = "Para ingresar debe usar el usuario y clave del portal pasaporte."
		if error_msg in site_text:
			return True
		else:
			return False


	def _get_first_row_from_table(self, table_node):
		rows = table_node.xpath("tr")
		first_row = rows[1]
		data_row = first_row.xpath("td/text()")
		return data_row

	def _get_payload_from_form(self, form_node):
		payload = {}
		for name, value in form_node.form_values():
			payload[name] = value
		return payload

	class SiteIsDown(Exception):
		pass
	
	class PaymentFormDisabled(Exception):
		pass

	class PaymentGatwwayDisabled(Exception):
		pass

	class LoginFailed(Exception):
		pass
	

import time
import datetime

def main():
	bot = UserApi(username=USERNAME, password=PASSWORD)
	
	while True:
		try:
			print(datetime.datetime.now(),"Checking logged in...")
			if bot.check_login():
				print(datetime.datetime.now(),"Still loging")

				print(datetime.datetime.now(),"Getting express passport payment form")
				payment_form = bot.get_express_passport_payment_form()


			else:
				print(datetime.datetime.now(),"logout...")
				
				print(datetime.datetime.now(),"Trying login...")
				bot.login()
			
		except UserApi.SiteIsDown:
			print(datetime.datetime.now(),"Site down....")
		except UserApi.PaymentFormDisabled:
			print(datetime.datetime.now(),"Payment form disabled....")
		except requests.exceptions.RequestException as err:
			print(datetime.datetime.now(),"Connection error....")
			print(datetime.datetime.now(), err)
			time.sleep(10)
			continue
		
		
		print(datetime.datetime.now(),"Going to sleep....")
		time.sleep(60) 
		
	print("Exiting...")
    

if __name__ == '__main__':
    main()