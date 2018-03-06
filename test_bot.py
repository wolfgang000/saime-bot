import unittest
import os
from lxml import html
from saime_bot import UserApi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))



class SaimeBotTests(unittest.TestCase):

	def setUp(self):
		self.user_api = UserApi(username="blala",password="blala")

	def test_row_data_from_table_node(self):
		
		table_str = """
			<table class="table" cellpadding="0" cellspacing="0">
			<tr>
				<td width="20%" class="titulo">
				<h5>C&eacute;dula</h5>
				</td>
				<td width="30%" class="titulo">
				<h5>Nombre Completo</h5>
				</td>
				<td width="20%" class="titulo">
				<h5>Sexo</h5>
				</td>
				<td width="20%" class="titulo">
				<h5>Fecha de Nacimiento</h5>
				</td>
				<td width="20%" class="titulo">
				<h5>Opciones</h5>
				</td></tr>
				<tr id="0">
					<td class="dato">123456</td>
					<td class="dato">Pancho Villa</td>
					<td class="dato">M</td>
					<td class="dato">17/12/1988</td>
					<td class="dato">
					<input onClick="mostrar_seleccion(&quot;0&quot;)" name="yt0" type="button" value="Ver" id="yt0" /> </td> 
				</tr> 
			</table>
		"""
		table_node = html.fromstring(table_str)
		row = self.user_api._get_first_row_from_table(table_node)
		self.assertEqual(row[0],'123456')
		self.assertEqual(row[1],'Pancho Villa')
		self.assertEqual(row[2],'M')
		self.assertEqual(row[3],'17/12/1988')

	def test_payload_from_form(self):
		file_path = os.path.join(BASE_DIR, 'tests/data/express.html')
		with open(file_path, 'r') as myfile:
			express_html = myfile.read()

		form_node = html.fromstring(express_html).get_element_by_id("pago-form")
		payload = self.user_api._get_payload_from_form(form_node)
		self.assertEqual(len(payload), 5)

	def test_disabled_payment_site(self):
		file_path = os.path.join(BASE_DIR, 'tests/data/express_failed.html')
		with open(file_path, 'r') as myfile:
			express_html = myfile.read()

		self.assertEqual(self.user_api._is_payment_form_enable(site_text=express_html), False)

		test_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor"
		self.assertEqual(self.user_api._is_payment_form_enable(site_text=test_text), True)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
