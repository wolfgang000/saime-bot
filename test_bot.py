import unittest
from lxml import html

class SaimeBotTests(unittest.TestCase):
	def test_row_data_from_table_node(self):
		from saime_bot import get_table_row
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
		print(table_node)
		self.assertTrue(get_table_row(table_node)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
