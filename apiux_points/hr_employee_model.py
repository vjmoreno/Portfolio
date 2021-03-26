from openerp import models, fields, api
import datetime


class hr_employee(models.Model):
	_inherit = "hr.employee"
	points = fields.Integer('Puntos', readonly=True)
	points_ids = fields.One2many('hr.points', 'employee_id', string='Puntos APIUX')
	total_administrative_points = fields.Integer('Total puntos')
	total_compensatory_points = fields.Integer('Total puntos')

	@api.onchange('points_ids')
	def onchange_points(self):
		self.total_administrative_points = 0
		self.total_compensatory_points = 0
		for _id in self.points_ids:
			if _id.behavior not in ('Compensatorios', 'Medio dia compensatorio', 'Cumpleanos') :
				self.total_administrative_points += _id.administrative_points
			else:
				self.total_compensatory_points += _id.compensatory_points

	def add_birthday_points(self):
		date = datetime.datetime.strptime(fields.Date.today(), '%Y-%m-%d').date()
		for employee in self.env['hr.employee'].search([]):
			if employee.birthday:
				birth = datetime.datetime.strptime(employee.birthday, '%Y-%m-%d').date()
				if (birth.month == date.month) and (date.day == birth.day):
						self.env['hr.points'].create({'administrative_points': 600, 
													'behavior':'Cumpleanos', 
													'employee_id': employee.id})
						employee.onchange_points()

	def add_one_year_points(self):
		#keys = employees_id values = min(contract_start_dates)
		contracts_dict = {}
		date = datetime.datetime.strptime(fields.Date.today(), '%Y-%m-%d').date()
		for contract in self.env['hr.contract'].search([]):
			if contract.type_id.name in ['Plazo Fijo', 'Plazo Indefinido']:
				#if contract has end date and is after today
				if contract.date_end:
					date_end = datetime.datetime.strptime(contract.date_end, '%Y-%m-%d').date()
					if date_end > date:
						if contract.employee_id not in contracts_dict.keys():
							contracts_dict[contract.employee_id] = contract.date_start
						else:
							contracts_dict[contract.employee_id] = min(contracts_dict[contract.employee_id], contract.date_start)
				#if contract do not have end date
				else:
					if contract.employee_id not in contracts_dict.keys():
						contracts_dict[contract.employee_id] = contract.date_start
					else:
						contracts_dict[contract.employee_id] = min(contracts_dict[contract.employee_id], contract.date_start)

		for employee, value in contracts_dict.items():
			contract_date = datetime.datetime.strptime(value, '%Y-%m-%d').date()
			#if employee completes a year of contract
			if (contract_date.month == date.month) and (contract_date.day == date.day) and (contract_date.year < date.year):
				self.env['hr.points'].create({'administrative_points': 4000, 
											'behavior':'Ano de contrato', 
											'employee_id': employee.id})
				employee.onchange_points()

	#this method substract the remaining administrative points that had been added one year ago
	def subtract_administrative_points(self):
		for employee in self.env['hr.employee'].search([]):
			admin_points = 0
			discount = False
			for points in employee.points_ids:
				admin_points += points.administrative_points
				date = datetime.datetime.strptime(points.date, '%Y-%m-%d')
				today = datetime.datetime.strptime(fields.Date.today(), '%Y-%m-%d')
				if (date.month == today.month) and (date.day == today.day) and (date.year + 1 == today.year) and (points.behavior == 'Ano de contrato'):
					discount = True
			if discount:
				self.env['hr.points'].create({'administrative_points': - admin_points, 
												'behavior': 'Vencimiento de puntos administrativos', 
												'employee_id': employee.id})
				employee.onchange_points()
				
	#method called by a planned action to update administrative points
	def update_points(self):
		self.subtract_administrative_points()
		self.add_one_year_points()