from openerp import models, fields, api
import datetime
import math
from openerp import tools
from datetime import datetime
from openerp.osv import osv
from datetime import timedelta
from openerp.tools.translate import _

import logging

_logger = logging.getLogger(__name__)

HOLIDAY_EXEMPTION_LIST=['Licencia Medica','Sick Leaves','Permiso']

class hr_holidays(models.Model):
	_rec_name = 'combination' 
	_inherit = 'hr.holidays'
	points_id = fields.Many2one('hr.points', relation='puntos_holidays', string='Puntos')
	combination = fields.Char(string='Combination', compute='_compute_fields_combination')

	#date_check2 edited to be allways true
	_sql_constraints = [
		('type_value', "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or (holiday_type='category' AND category_id IS NOT NULL))", 
		 "The employee or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
		('date_check2', "CHECK(1=1)", "The start date must be anterior to the end date."),
		('date_check', "CHECK ( number_of_days_temp >= 0 )", "The number of days must be greater than 0."),
	]

	#compute _rec_name
	@api.depends( 'employee_id','holiday_status_id', 'date_from', 'date_to')
	def _compute_fields_combination(self):
		for holiday in self:
			if holiday.employee_id and holiday.holiday_status_id and holiday.date_from and holiday.date_to:
				holiday.combination =holiday.employee_id.name_related + ' ' + holiday.holiday_status_id.name + ' ' + holiday.date_from + ' ' + holiday.date_to

	#create points when a holiday is validated
	def holidays_validate(self, cr, uid, ids, context=None):
		
		res=super(hr_holidays, self).holidays_validate(cr, uid, ids, context)
  
		for holiday in self.browse(cr,uid,ids,context=None):

			if holiday.holiday_status_id.name== 'Dia administrativo':
				values = {'administrative_points': -1000, 
						'behavior':holiday.holiday_status_id.name, 
						'employee_id': holiday.employee_id.id,
						'holidays_id': holiday.id}
				holiday.employee_id.onchange_points()
				record = self.pool.get('hr.points').create(cr, uid, values, context)
			elif holiday.holiday_status_id.name == 'Medio dia administrativo':
				values = {'administrative_points': -600, 
						'behavior':holiday.holiday_status_id.name, 
						'employee_id': holiday.employee_id.id,
						'holidays_id': holiday.id}
				holiday.employee_id.onchange_points()
				record = self.pool.get('hr.points').create(cr, uid, values, context)
			elif holiday.holiday_status_id.name == 'Trabajo remoto':
				values = {'administrative_points': -300, 
						'behavior':holiday.holiday_status_id.name, 
						'employee_id': holiday.employee_id.id,
						'holidays_id': holiday.id}
				holiday.employee_id.onchange_points()
				record = self.pool.get('hr.points').create(cr, uid, values, context)
			elif holiday.holiday_status_id.name == 'Compensatorios':
				values = {'compensatory_points': -1000, 
						'behavior':holiday.holiday_status_id.name, 
						'employee_id': holiday.employee_id.id,
						'holidays_id': holiday.id}
				holiday.employee_id.onchange_points()
				record = self.pool.get('hr.points').create(cr, uid, values, context)
			elif holiday.holiday_status_id.name == 'Medio dia compensatorio':
				values = {'compensatory_points': -600, 
						'behavior':holiday.holiday_status_id.name, 
						'employee_id': holiday.employee_id.id,
						'holidays_id': holiday.id}
				holiday.employee_id.onchange_points()
				record = self.pool.get('hr.points').create(cr, uid, values, context)

		return True

	def onchange_date_from(self, cr, uid, ids, holiday_status_id, employee_id,date_to, date_from):
		result = {'value': {}}
		#these kind of holidays will always have number_of_days = 1
		if holiday_status_id:
			if self.pool['hr.holidays.status'].browse(cr,uid,holiday_status_id,context=None).name in ('Dia administrativo', 
																									'Medio dia administrativo', 
																									'Trabajo remoto', 
																									'Compensatorios', 
																									'Medio dia compensatorio'):
				result['value']['date_to'] = str(datetime.strptime(date_from, tools.DEFAULT_SERVER_DATE_FORMAT))

		elif (date_from and date_to) and (date_from > date_to):
			raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
			
		if (date_from or date_to) and not holiday_status_id:
			raise osv.except_osv(_('Warning!'),_('Selecciona tipo de ausencia primero!'))

		# No date_to set so far: automatically compute one 8 hours later
		if date_from and not date_to:
			date_to_with_delta = datetime.strptime(date_from, tools.DEFAULT_SERVER_DATE_FORMAT)
			result['value']['date_to'] = str(date_to_with_delta)

		# Compute and update the number of days
		if (date_to and date_from) and (date_from <= date_to):
			diff_day = self._get_number_of_days(date_from, date_to)
			if self.pool['hr.holidays.status'].browse(cr,uid,holiday_status_id,context=None).name not in ('Medio dia administrativo', 
																										'Medio dia compensatorio'):
				result['value']['number_of_days_temp'] = round(math.floor(diff_day)) + 1
			else:
				result['value']['number_of_days_temp'] = round(math.floor(diff_day)) + 0.5
		else:
			result['value']['number_of_days_temp'] = 0

		#get company from employee..obligatory field
		emp=self.pool("hr.employee").browse(cr,uid,[employee_id],context=None)
		company_id=emp.company_id.id or 1			 
		
		holiday_type_obj=self.pool("hr.holidays.status")
		holiday_type=holiday_type_obj.browse(cr,uid,[holiday_status_id],context=None)
		
		exemptions_cnt=0
		if date_from and date_to and holiday_type.name not in HOLIDAY_EXEMPTION_LIST:	
			
			DATETIME_FORMAT = "%Y-%m-%d"
			from_dt = datetime.strptime(date_from, DATETIME_FORMAT)
			to_dt = datetime.strptime(date_to, DATETIME_FORMAT)
			   
			exemptions_cnt,exemptions_list=self._get_exemption_list(cr,uid,from_dt,to_dt,company_id)			 
			
		result['value']['number_of_days_temp'] = result['value']['number_of_days_temp'] -exemptions_cnt			  
			
			
		return result

	def onchange_date_to(self, cr, uid, ids, holiday_status_id,employee_id,date_to, date_from):

		result = {'value': {}}
		#these kind of holidays will always have number_of_days = 1
		if holiday_status_id:
			if self.pool['hr.holidays.status'].browse(cr,uid,holiday_status_id,context=None).name in ('Dia administrativo', 
																									'Medio dia administrativo', 
																									'Trabajo remoto', 
																									'Compensatorios', 
																									'Medio dia compensatorio'):
				result['value']['date_from'] = str(datetime.strptime(date_to, tools.DEFAULT_SERVER_DATE_FORMAT))
				result['value']['date_to'] = str(datetime.strptime(date_to, tools.DEFAULT_SERVER_DATE_FORMAT))


		# date_to has to be greater than date_from
		elif (date_from and date_to) and (date_from > date_to):
			raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
			
		if (date_from or date_to) and not holiday_status_id:
			raise osv.except_osv(_('Warning!'),_('Selecciona tipo de ausencia primero!'))			  


		# Compute and update the number of days
		if (date_to and date_from) and (date_from <= date_to):
			diff_day = self._get_number_of_days(date_from, date_to)
			if self.pool['hr.holidays.status'].browse(cr,uid,holiday_status_id,context=None).name not in ('Medio dia administrativo', 
																										'Medio dia compensatorio'):
				result['value']['number_of_days_temp'] = round(math.floor(diff_day)) + 1
			else:
				result['value']['number_of_days_temp'] = round(math.floor(diff_day)) + 0.5
		else:
			result['value']['number_of_days_temp'] = 0

			
		#get company from employee..obligatory field
		emp=self.pool("hr.employee").browse(cr,uid,[employee_id],context=None)
		company_id=emp.company_id.id or 1			

		holiday_type_obj=self.pool("hr.holidays.status")
		holiday_type=holiday_type_obj.browse(cr,uid,[holiday_status_id],context=None)
		_logger.info("htname=%s",holiday_type.name)		
		
		exemptions_cnt=0
		if date_from and date_to and holiday_type.name not in HOLIDAY_EXEMPTION_LIST:	 
			
			DATETIME_FORMAT = "%Y-%m-%d"
			from_dt = datetime.strptime(date_from, DATETIME_FORMAT)
			to_dt = datetime.strptime(date_to, DATETIME_FORMAT)
			   
			exemptions_cnt,exemptions_list=self._get_exemption_list(cr,uid,from_dt,to_dt,company_id)			
			
		result['value']['number_of_days_temp'] = result['value']['number_of_days_temp'] -exemptions_cnt	
			
		return result

	"""def create(self, cr, uid, values, context=None):
		create_bool = True
		if self.browse(cr,uid,values['holiday_status_id'],context=None).name in ('Dia administrativo', 'Medio dia administrativo'):
			_logger.info(self.browse(cr, uid, [('employee_id.id', '=', values['employee_id'])]))
			_logger.info(self.browse(cr, uid, [('employee_id.id', '=', values['employee_id'])]))
			for holiday in self.browse(cr, uid, [('employee_id.id', '=', values['employee_id'])]):
				if holiday.holiday_status_id.name in ('Dia administrativo', 'Medio dia administrativo'):
					date_from = datetime.strptime(values['date_from'], tools.DEFAULT_SERVER_DATE_FORMAT)
					holiday_date_from = datetime.strptime(holiday.date_from, tools.DEFAULT_SERVER_DATE_FORMAT)
					if (holiday_date_from.day - 1 < date_from.day < holiday_date_from.day + 1):
						create_bool = False
		if create_bool:
			return super(hr_holidays, self).create(cr, uid, values, context=context)"""