# -*- coding: utf-8 -*-
{
	'name': "Apiux Points",
	'summary': 'Sistema de puntos de APIUX',
	'description': '''Funcionamiento general del sistema:
					1) Los puntos pueden ser de dos tipos: Administrativos o compensatorios\n
					2) Los puntos pueden ser generados por medio de:\n
					\t2.1.- Validacion solicitudes de inasistencias\n
					\t2.2.- Ejecucion del metodo update_points del modelo hr.employee (agregar accion planificada)\n
					\t2.3.- De manera manual en la pestana Recursos Humanos -> Puntos -> Puntos\n
					3) Se deben crear 2 grupos para un correcto funcionamiento del sistema (administradores y empleados)\n
					4) Se debe agregar la siguiente regla: Los empleados solo deben poder ver sus propios puntos y no deben poder editar, eliminar o crear puntos.''',
	'author': "Vicente Moreno",
	'data': ['views/hr_points_view.xml', 
			'views/hr_employee_view.xml'],
	'depends': [ 'hr', 
				'hr_holidays', 
				'apiux_nomina'],
	'application': False
}