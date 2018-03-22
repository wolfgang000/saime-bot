import requests
from lxml import html
import configparser
import os
import random


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read('USER_CREDENTIAL.INI')

PUSHED_APP_KEY = config['DEFAULT']['PUSHED_APP_KEY']
PUSHED_APP_SECRET = config['DEFAULT']['PUSHED_APP_SECRET']
default = config['DEFAULT']


CARD_HOLDER_CI = default['CARD_HOLDER_CI']
CARD_TYPE = default['CARD_TYPE']
CARD_HOLDER = default['CARD_HOLDER']
CARD_NUMBER = default['CARD_NUMBER']
CARD_CVV = default['CARD_CVV']
CARD_EXPIRATION_DATE_MONTH = default['CARD_EXPIRATION_DATE_MONTH']
CARD_EXPIRATION_DATE_YEAR = default['CARD_EXPIRATION_DATE_YEAR']
SECRET_ANSWER = default['SECRET_ANSWER']


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

	def __init__(self, username, password, secret_answer, names):
		self.session_requests = requests.session()
		self.username = username
		self.password = password
		self.secret_answer = secret_answer
		self.names = names

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
		if response.status_code >= 500:
			raise self.SiteIsDown()

		if self._is_login_page(response.content.decode('utf_8')):
			raise self.LoginFailed()
	
	def is_login(self):
		response = self.session_requests.get(
			self.HOME_URL, 
			headers = dict(referer = self.HOME_URL), 
			timeout = 20
		)
		if response.status_code >= 500:
			raise self.SiteIsDown()
		
		return not self._is_login_page(response.content.decode('utf_8'))


	def get_user_data(self):
		result = self.session_requests.get(
			self.HOME_URL, 
			headers = dict(referer = self.HOME_URL),
			timeout = 20
		)
		if result.status_code >= 500:
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


	def is_name_in_text(self, name_list, text_content):
		for name in name_list:
			if name in text_content:
				return True
		return False

	def get_filter_forms(self, tree, names):
		tr_nodes = tree.xpath("//table[@class='table']/tr")
		tr_nodes = list(filter(lambda node: self.is_name_in_text(names, node.text_content()), tr_nodes))
		form_nodes = []
		for tr_node in tr_nodes: 
			tr_node = html.fromstring(html.tostring(tr_node))
			form_nodes += tr_node.xpath("//tr/td/form")
		return form_nodes

	
	def get_express_passport_payment_form_links(self):
		'''
		Return forms links to the express passport payment form
		'''
		response = self.session_requests.get(
			self.EXPRESS_URL,
			headers = dict(referer = self.EXPRESS_URL),
			timeout = 20
		)
		if response.status_code >= 500:
			raise self.SiteIsDown()
		
		tree = html.fromstring(response.content)
#		form_nodes = tree.xpath('//form')
		form_nodes = self.get_filter_forms(tree, self.names)

		#Check if there are payment forms
		if not form_nodes:
			raise self.ExpressPassportPaymentFormNotFound()

		return form_nodes
	
	def get_express_passport_payment_form(self, form_node_link):
		'''
		Return the actual payment form for the express passport
		'''
		payload = self._get_payload_from_form(form_node_link)
		response = self.session_requests.post(
			self.PAYMENT_URL, 
			data = payload, 
			headers = dict(referer = self.PAYMENT_URL),
			timeout = 20
		)
		if response.status_code >= 500:
			raise self.SiteIsDown()
		payment_form = self._get_payment_form(response.content)
		if payment_form == None:
			raise self.PaymentFormDisabled()

		return payment_form
	
	def perform_payment(self, payment_form, card_ci, card_type, card_holder_name, card_number, card_cvc, card_expiration_date_month, card_expiration_date_year,):
		payload = self._get_payload_from_form(payment_form)
		payload['Banesco[cardHolderId]'] = card_ci
		payload['Banesco[tipoTarjeta]'] = card_type
		payload['Banesco[cardHolder]'] = card_holder_name
		payload['Banesco[cardNumber]'] = card_number
		payload['Banesco[cvc]'] = card_cvc
		payload['Banesco[expirationDateMonth]'] = card_expiration_date_month
		payload['Banesco[expirationDateYear]'] = card_expiration_date_year
		payload['Banesco[respuesta]'] = self.secret_answer
		
		response = self.session_requests.post(
			self.PAYMENT_URL, 
			data = payload, 
			headers = dict(referer = self.PAYMENT_URL),
			timeout = 30
		)
		if response.status_code >= 500:
			raise self.SiteIsDown()

		error_msg = 'Estimado ciudadano usted posee el máximo de pagos permitidos para este tipo de tramite en este año'
		if error_msg in response.content.decode('utf_8'):
			raise self.PaymentGatewayDisabled()
		
		success_msg = 'Estimado ciudadano, le informamos que su pago ha sido procesado'
		if success_msg not in response.content.decode('utf_8'): 
			send_notification("Error de pago con targeta:" + self.username)
			raise self.PaymentGatewayDisabled()

		file_path = os.path.join(BASE_DIR, self.username +  str(random.randint(0, 50)) + 'success.html') 
		with open(file_path, 'w') as myfile: 
			myfile.write(response.content.decode('utf_8')) 
		send_notification("parece que se pago:" + self.username)

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

	class PaymentGatewayDisabled(Exception):
		pass

	class LoginFailed(Exception):
		pass
	
	class ExpressPassportPaymentFormNotFound(Exception):
		pass

import time
import datetime
from collections import deque
import json


def main():

	file_path = os.path.join(BASE_DIR, 'users.json')
	with open(file_path, 'r') as myfile:
		express_html = myfile.read()
	users = json.loads(express_html)


	d = deque() 
	for user in users:
		d.append(UserApi(
			username=user['username'],
			password=user['password'],
			secret_answer = user['secret_answer'],
			names = user['names'],
			)
		)
	while True:
		try:
			bot = d.popleft()
			while True:
				print("user:", bot.username )
				try:
					print(datetime.datetime.now(),"Checking logged in...")
					if not bot.is_login():
						print(datetime.datetime.now(),"logout...")	
						print(datetime.datetime.now(),"Trying login...")
						bot.login()
					else:
						print(datetime.datetime.now(),"Still loging")

					print(datetime.datetime.now(),"Getting express passport payment form links")
					payment_form_links = bot.get_express_passport_payment_form_links()
					print("tarmites:", len(payment_form_links))
					for payment_form_link in payment_form_links:
						payment_form = bot.get_express_passport_payment_form(payment_form_link)
						bot.perform_payment(
							payment_form=payment_form,
							card_ci=CARD_HOLDER_CI,
							card_type=CARD_TYPE,
							card_holder_name=CARD_HOLDER,
							card_number=CARD_NUMBER,
							card_cvc=CARD_CVV,
							card_expiration_date_month=CARD_EXPIRATION_DATE_MONTH,
							card_expiration_date_year=CARD_EXPIRATION_DATE_YEAR,
						)
						print("Payment success")
					break

					
				except UserApi.SiteIsDown:
					print(datetime.datetime.now(),"Site down....")
				except UserApi.PaymentFormDisabled:
					print(datetime.datetime.now(),"Payment form disabled....")
				
				except UserApi.ExpressPassportPaymentFormNotFound:
					print(datetime.datetime.now(),"Express Passport Payment Form Not Found, exiting....")
					send_notification("quisas se pago...")
					break
				except UserApi.LoginFailed:
					print(datetime.datetime.now(),"Login error with user:{}, check username and password, exiting....".format(bot.username))
					send_notification("Error login with user:{}...".format(bot.username))
					break
				except requests.exceptions.RequestException as err:
					print(datetime.datetime.now(),"Connection error....")
					print(datetime.datetime.now(), err)
					time.sleep(10)
					continue
	
				print(datetime.datetime.now(),"Going to sleep....")
				time.sleep(31) 

		except IndexError:
			print("No more accounts left")
			break
	print("Exiting...")

	

		
	
    

if __name__ == '__main__':
    main()