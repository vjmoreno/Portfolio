from openerp import models, fields, api, exceptions
from datetime import datetime
import re, logging

_logger = logging.getLogger(__name__)

class hr_onboard(models.Model):
	_inherit = 'hr.onboard'
	solicitante_id = fields.Many2one('apiux.background.form', 'Solicitante')
	tecnologias_experto_ids = fields.Many2many('apiux.knowledge.category', relation='tecnologias_experto_solicitante_rel', string='Tecnologias Experto')
	tecnologias_dominio_ids = fields.Many2many('apiux.knowledge.category', relation='tecnologias_dominio_solicitante_rel', string='Tecnologias Dominio')
	tecnologias_aprendizaje_ids = fields.Many2many('apiux.knowledge.category',relation='tecnologias_aprendizaje_solicitante_rel', string='Tecnologias Aprendizaje')
	tag_list = [
	'JAVA',
	'C/C++',
	'Python',
	'Visual Basic .NET',
	'C#',
	'PHP',
	'JavaScript',
	'Delphi',
	'Objective - C',
	'Ruby',
	'Perl',
	'PL/SQL',
	'COBOL/400',
	'RPG/400',
	'PHP - LaraveL',
	'PHP - Symfony',
	'PHP - ZEND',
	'PHP - Codelgniter',
	'PHP - Cake',
	'PHP - Fuel',
	'PHP - YII 2',
	'PHP - Phalcon',
	'JAVA - JEE',
	'JAVA - Spring Framework',
	'JAVA - JPA',
	'JAVA - IBATIS',
	'JAVA - Spring Boot',
	'JAVA - GRAILS',
	'JAVA - Spring Netflix',
	'Python - Django',
	'Python - Web2py',
	'Python - CubicWeb',
	'Python - Giotto',
	'Python - Pylon',
	'Python - Bottle',
	'Python - Cherry Py',
	'Ruby - On Rails',
	'Ruby - Sinatra',
	'Ruby - Padrino',
	'Ruby - Hanami/Lotus',
	'Perl - Catalyst',
	'Perl - Catalyst',
	'Perl - Mojolicious',
	'Perl - CGI',
	'Perl - TAP',
	'JavaScript - NodeJS',
	'Ionic',
	'Apache Cordova',
	'Android Native',
	'Objective - C',
	'Swift',
	'HTML',
	'HTML5',
	'CSS',
	'CSS3',
	'Bootstrap',
	'JAVA - JSF',
	'JAVA - STRUTS',
	'JAVA - GWT',
	'JAVA - Vaadin',
	'JAVA - Spring MVC',
	'JAVA - GRAILS',
	'AngularJS',
	'Angular',
	'React.js',
	'Foundation',
	'Semantic UI',
	'Pure',
	'Linux Redhat FUSE',
	'Linux Redhat BRMS',
	'WSO2',
	'Oracle OSB',
	'MULE ESB',
	'IBM Datapower',
	'IBM ODM',
	'WSO2 Identity',
	'JASIG CAS',
	'Keycloak',
	'IBM Websphere',
	'Oracle Weblogic',
	'JBoss EAP/Wildfly',
	'Apache Torncat',
	'Apache Tomee',
	'Microsoft SII',
	'Apache Web Server',
	'Redhat BPMS',
	'IBM Lombardi',
	'Oracle BPM',
	'Bizagi BPM Suite',
	'BonitaSoft',
	'PyFlow',
	'Activiti',
	'IBM Filenet',
	'Alfresco ECM',
	'Microsoft Sharepoint',
	'OpenText',
	'Documentum',
	'DOCUX',
	'IBM Datacap',
	'Kofax',
	'Ephesoft',
	'Informatica - Powercenter',
	'IBM DataStage',
	'Oracle Data Integrator',
	'Microsoft - SQL SSIS',
	'Talend',
	'Pentaho Data Integration',
	'Apache Nifi',
	'ETL',
	'Sisense',
	'Looker',
	'Yellowfin',
	'SAP Crystal Reports',
	'Domo',
	'Tableau',
	'Microsoft Power BI',
	'QlikSense',
	'IBM Cognos Analytics',
	'Board',
	'Datapine',
	'BI',
	'Hadoop',
	'Cloudera',
	'Hortonworks',
	'Apache Storm',
	'Cassandra',
	'Flink',
	'Hive',
	'WordPress',
	'Drupal',
	'Adobe Experience Manager',
	'WCM',
	'AmazonWS',
	'Google Cloud',
	'Oracle Cloud',
	'Alibaba Cloud',
	'IBM Bluemix/IBM Cloud',
	'Azure',
	'Oracle Database',
	'Informix',
	'DB2',
	'SQL Server',
	'PostgreSQL',
	'MySQL/MariaDB',
	'MongoDB',
	'Windows Desktop',
	'Windows Server',
	'Linux Redhat/ Centos',
	'Linux Ubuntu',
	'Linux Debian',
	'Unix',
	'TCP/IP',
	'VPN',
	'Cisco dispositivos',
	'VMWare',
	'Hyperv',
	'Microsoft Project',
	'Microsoft Team Foundation',
	'Atlasian JIRA',
	]

	def habilidades_to_dict_(self):
		str_habilidades = \
		str(self.solicitante_id.lenguajes_de_programacion \
		+ self.solicitante_id.frameworks_backend \
		+ self.solicitante_id.mobile + self.solicitante_id.web \
		+ self.solicitante_id.frameworks_frontend \
		+ self.solicitante_id.integracion_servicios \
		+ self.solicitante_id.plataformas_gestion_procesos \
		+ self.solicitante_id.plataformas_documental_captura \
		+ self.solicitante_id.plataformas_etl_informacion \
		+ self.solicitante_id.plataformas_gestion_web \
		+ self.solicitante_id.plataformas_cloud \
		+ self.solicitante_id.bases_datos \
		+ self.solicitante_id.sistemas_operativos_redes \
		+ self.solicitante_id.gestion_proyectos)
		list_habilidades = re.findall('[A-Z][^A-Z]*', str_habilidades)
		dict_habilidades = dict(zip(self.tag_list, list_habilidades))
		return dict_habilidades


	@api.onchange('solicitante_id')
	def onchange_tags(self):
		dict_habilidades = self.habilidades_to_dict_()
		ids_experto = []
		ids_dominio = []
		ids_aprendizaje = []
		for key in dict_habilidades.keys():
			tag = self.env['apiux.knowledge.category'].search([('name', '=', key)])
			if tag:
				if dict_habilidades[key] == 'Experto':
					ids_experto.append(tag.id)
				elif dict_habilidades[key] == 'Dominio':
					ids_dominio.append(tag.id)
				elif dict_habilidades[key] == 'Aprendizaje':
					ids_aprendizaje.append(tag.id)
		if self.solicitante_id:
			self.update({'tecnologias_experto_ids': [[6, False, ids_experto]]})
			self.update({'tecnologias_dominio_ids': [[6, False, ids_dominio]]})
			self.update({'tecnologias_aprendizaje_ids': [[6, False, ids_aprendizaje]]})

	@api.onchange('solicitante_id')
	def onchange_solicitante_id(self):
		if self.solicitante_id:
			self.name = str(self.solicitante_id.nombre) + ' ' + str(self.solicitante_id.apellido_paterno) + ' ' + str(self.solicitante_id.apellido_materno) 
			self.firstname = self.solicitante_id.nombre
			self.surname_paternal = self.solicitante_id.apellido_paterno
			self.surname_maternal = self.solicitante_id.apellido_materno
			self.hr_city = self.solicitante_id.ciudad
			self.municipality = self.solicitante_id.comuna
			self.personal_telephone = self.solicitante_id.telefono_fijo
			self.p_mobile = self.solicitante_id.telefono_movil
			self.identification_id = self.solicitante_id.rut
			if self.solicitante_id.estado_civil == 'Soltero':
				self.marital = 'single'
			elif self.solicitante_id.estado_civil == 'Casado':
				self.marital = 'married'
			elif self.solicitante_id.estado_civil == 'Divorciado':
				self.marital = 'divorced'
			elif self.solicitante_id.estado_civil == 'Viudo':
				self.marital = 'widow'
			self.personal_email = self.solicitante_id.correo
			self.children = self.solicitante_id.cargas
			nacimiento = self.solicitante_id.nacimiento.split('/')
			self.birthday = datetime.strptime(nacimiento[2] + '-' + nacimiento[1] + '-' + nacimiento[0], "%Y-%m-%d")
			self.country_id = self.env['res.country'].search([('name','=',self.solicitante_id.nacionalidad)])

	@api.multi
	def set_employee(self):
		emp_obj=self.env['hr.employee']
		resource_obj = self.env['resource.resource']
		emp_type_obj = self.env['hr.type.employee']
		partner_obj =self.env['res.partner']

		wp_partner=False
		if self.workplace=='office':
			wp_partner=partner_obj.search([('name','like','Apiux')])
			wp_partner=wp_partner and wp_partner[0] or False

		
		
		emp_type=emp_type_obj.search([('id_type','=','0')])
		parent_id=emp_obj.search([('user_id','=',self.user_id.id)])		
				
				
		if not self.employee_id:
			#include a RUT check for Chile
			if self.country_id.code=='CL' and not self.identification_id:
				raise exceptions.Warning(('''Este OnBoard tiene nacionalidad Chileno. Por favor ingrese su RUT en campo No. Identificacion '''))			 
		
			values={
				'name_related':self.name,
				'name':self.name,				
				'type_id':emp_type.id,
				'register_hours':self.register_hours,
				'parent_id':parent_id and parent_id[0].id or False,
				'account_cost_center':self.cost_center.id,
				'job_id':self.job_id.id,
				'company_id':self.company_id.id,
				'address_id':wp_partner and wp_partner.id or False,
				'department_id':self.department_id.id,
				'firstname':self.firstname,
				'surname_paternal':self.surname_paternal,
				'surname_maternal':self.surname_maternal,
				'country_id':self.country_id.id,
				'identification_id':self.identification_id,
				'passport_id':self.passport_id,
				'otherid':self.otherid,
				'hr_city':self.hr_city,
				'municipality':self.municipality,
				'address_home_id':self.address_home_id and self.address_home_id.id or False,
				'personal_telephone':self.personal_telephone,
				'personal_email':self.personal_email,
				'p_mobile':self.p_mobile,
				'gender':self.gender,
				'marital':self.marital,
				'birthday':self.birthday,
				'email_location':self.workplace,
				'technology_ids': [(6,0,self.tecnologias_experto_ids.ids)],
				'technology_known_ids': [(6,0,self.tecnologias_dominio_ids.ids)],
				'technology_learn_ids': [(6,0,self.tecnologias_aprendizaje_ids.ids)]
				}
				
			try:
				emp=emp_obj.create(values)
				self.employee_id=emp
				
				street=(emp.address_home_id and emp.address_home_id.name) or ''
				comuna=self.municipality
				ciudad=self.hr_city
		
				if emp.address_home_id:
					emp.address_home_id.street=','.join([street,comuna,ciudad])
					emp.address_home_id.firstname=self.firstname
					emp.address_home_id.lastname=self.surname_paternal + " " + self.surname_maternal
					emp.address_home_id.is_company=False
					
				else:
					address_home_id=partner_obj.create({'firstname':self.firstname,
														'lastname':self.surname_paternal + " " + self.surname_maternal,
														'street':','.join([street,comuna,ciudad]),
														'is_company':False})
					self.address_home_id=address_home_id
					emp.address_home_id=address_home_id
				
				#only copy id to partner NIF if country is Chile, otherwise it will fail
				if emp.country_id.code=='CL':
					emp.check_vat_cl()
					emp.address_home_id.vat=self.country_id.code+self.identification_id
				else:	
					pass				
				
			
				#get attachments and create apiux documentation
				att_obj = self.env['ir.attachment']
				apiux_object=self.env['apiux.documentation']
				file_ids = att_obj.sudo().search([('res_model', '=', 'hr.onboard'),('res_id', '=', self.id)])
				for file_id in file_ids:
					dvalues={
						'name':file_id.datas_fname,
						'datas':file_id.datas,
						'f_name':file_id.datas_fname,
						'emp_id':self.employee_id.id,
						}
					apiux_object.create(dvalues)
				#generate payslip password
				self.employee_id.generate_payslip_password() 
					
						
			except Exception,e:
				_logger.error("Error in hr_onboard.set_employee, %s",str(e))
				raise exceptions.Warning(('''No se puede crear empleado. Por favor contactarse con el Administrador del sistema'''))   
		else:
			raise exceptions.Warning(('''Este OnBoard ya tiene empleado asociado. Por favor crear un nuevo OnBoard'''))		

		cform = self.env.ref('hr.view_employee_form', False)
		action = {
			'type': 'ir.actions.act_window',
			'name': 'Empleado relacionado',
			'res_model': 'hr.employee',
			'res_id':self.employee_id.id,
			'src_model': 'hr.onboard',
			'view_id':cform.id,
			'view_mode': 'form',
			'view_type':'form',
			}
		return action
			
class ProfileSkillCategory(models.Model):
	_inherit = 'apiux.knowledge.category'
	solicitante_tecnologias_experto_ids = fields.Many2many('hr.onboard'
										, relation='tecnologias_experto_solicitante_rel'
										, string='Tecnologias Experto')
	solicitante_tecnologias_dominio_ids = fields.Many2many('hr.onboard'
										, relation='tecnologias_dominio_solicitante_rel'
										, string='Tecnologias Dominio')
	solicitante_tecnologias_aprendizaje_ids = fields.Many2many('hr.onboard'
										, relation='tecnologias_aprendizaje_solicitante_rel'
										, string='Tecnologias Aprendizaje')

