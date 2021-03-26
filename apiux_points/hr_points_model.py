from openerp import models, fields, api


class hr_points(models.Model):
	_name = 'hr.points'
	behavior_options = [('Dia administrativo', 'Dia administrativo'),
						('Medio dia administrativo', 'Medio dia administrativo'),
						('Trabajo remoto', 'Trabajo remoto'),
						('Cumpleanos', 'Cumpleanos'), 
						('Ano de contrato', 'Ano de contrato'), 
						('Puntos restantes ano anterior de contrato', 'Puntos restantes ano anterior de contrato'),
						('Compensatorios', 'Compensatorios'),
						('Medio dia compensatorio', 'Medio dia compensatorio'),
						('Vencimiento de puntos administrativos', 'Vencimiento de puntos administrativos')]
	behavior = fields.Selection(behavior_options, 'Tipo de comportamiento')
	#dictionaries: keys = behavior, values = points
	administrative_points_dict = { 'Ano de contrato': 4000, 
								'Dia administrativo': -1000, 
								'Medio dia administrativo': -600, 
								'Trabajo remoto':-300}
	compensatory_points_dict = {'Cumpleanos': 600,
								'Medio dia compensatorio': -600}
	administrative_points = fields.Integer('Puntos administrativos')
	compensatory_points = fields.Integer('Puntos compensatorios')
	employee_id = fields.Many2one('hr.employee', 'Empleado')
	holidays_id = fields.Many2one('hr.holidays', relation='puntos_holidays', string='Ausencia')
	date = fields.Date('Fecha', default=fields.Date.today())
	
	@api.onchange('behavior')
	def onchange_behavior(self):
		self.administrative_points = 0
		self.compensatory_points = 0
		if self.behavior in self.administrative_points_dict.keys():
			self.administrative_points = self.administrative_points_dict[self.behavior]
		elif self.behavior in self.compensatory_points_dict:
			self.compensatory_points = self.compensatory_points_dict[self.behavior]



