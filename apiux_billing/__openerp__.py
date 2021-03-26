{
	'name': "Apiux Billing",
	'author': "Vicente Moreno",
	'application': True,
	'depends': ['apiux_acc_ext', 'apiux_pr_ext'],
	'data': ['views/apiux_billing_view.xml'],
	'description':'''Se realizan los siguientes cambios en la contabilidad:\n
					1) Reordenamiento de los campos glosa, hes y oc de la prefactura\n
					2) Se rellenan de forma automática los campos 'Cuenta de ingresos', 
					'Cuenta a cobrar', 'Tipo de documento' y 'Producto' en la prefactura\n
					3) Valor de la UF automatizado en la prefactura\n
					'''
}
