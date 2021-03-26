#!/usr/bin/env python
# -*- coding: utf-8 -*-
from openerp import models, fields, api
import xlwt
from xlsxwriter.workbook import Workbook
from cStringIO import StringIO
import base64
from datetime import datetime
import logging
from openerp.exceptions import Warning
_logger = logging.getLogger(__name__) 

class purchase_order(models.Model):
	_inherit = "purchase.order"
	READONLY_STATES = {
		'confirmed': [('readonly', True)],
		'approved': [('readonly', True)],
		'done': [('readonly', True)],
		'cancel': [('readonly', True)]
	}
	STATE_SELECTION = [
		('draft', 'Draft PO'),
		('sent', 'RFQ'),
		('bid', 'Bid Received'),
		('confirmed', 'Waiting Approval'),
		('approved', 'Purchase Confirmed'),
		('except_picking', 'Shipping Exception'),
		('except_invoice', 'Invoice Exception'),
		('done', 'Done'),
		('cancel', 'Cancelled')
	]
	partner_id= fields.Many2one('res.partner', 'Supplier', required=True, states=READONLY_STATES, change_default=True, track_visibility='always')
	partner_ref = fields.Char('Supplier Reference', states=READONLY_STATES)
	pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', required=True, states=READONLY_STATES)
	employee_id = fields.Many2one('hr.employee', 'Solicitado por', states=READONLY_STATES)
	date_order = fields.Datetime('Order Date', required=True, states=READONLY_STATES, select=True, copy=False)
	currency_id = fields.Many2one('res.currency','Currency', required=True, states=READONLY_STATES)
	company_id = fields.Many2one('res.company', 'Company', required=True, select=1, states=READONLY_STATES)
	picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', required=True, states=READONLY_STATES)
	order_line = fields.One2many('purchase.order.line', 'order_id', 'Order Lines', states=READONLY_STATES, copy=True)
	state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, select=True, copy=False, default='draft')
	payment_type_options = [('Anticipado', 'Anticipado'), 
							('Contado', 'Contado'), 
							('15 dias', '15 dias'), 
							('30 dias', '30 dias'), 
							('45 dias', '45 dias'), 
							('60 dias', '60 dias')]
	payment_type= fields.Selection(payment_type_options, 'Tipo de pago', states=READONLY_STATES)
	new_states_options = [('Cancelado', 'Cancelado'),
							('Borrador', 'Borrador'),
							('Ingresado', 'Ingresado'), 
							('Aprobado por solicitante', 'Aprobado por solicitante'), 
							('Aprobado por departamento', 'Aprobado por departamento'), 
							('Aprobado por jefe', 'Aprobado por jefe'), 
							('Aprobado por gerente', 'Aprobado por gerente'),
							('Parcialmente facturado','Parcialmente facturado'),
							('Facturado', 'Facturado')]
	new_states = fields.Selection(new_states_options, 'Estados', default='Borrador')
	is_boss =fields.Boolean('is current user = boss?', compute='_check_current_user')
	current_user_id = fields.Integer('Current user id')
	boss_id = fields.Many2one('hr.employee', 'Jefe', states=READONLY_STATES)
	is_solicitant = fields.Boolean('Is solicitant?', compute='_check_solicitant')
	num_approves = fields.Integer('Numero de aprobaciones')
	notes = fields.Text('Terms and Conditions', states=READONLY_STATES)

	@api.onchange('payment_type', 'date_order')
	def onchange_payment_type(self):
		date = datetime.strptime(self.date_order, "%Y-%m-%d %H:%M:%S")
		self.notes = """CONDICIONES:
			1.- Para cualquier consulta sobre la Orden: contactar a Adm & Finanzas FONO 562-232445000 o al e-mail administracion.cl@apiux.com
			2.- La Guía de Despacho y la Factura deberán indicar el número de esta orden (PO) en el detalle o en el campo 801 de los formatos XML.
			3.- La factura puede ser enviada a la dirección MONSEÑOR NUNCIO SOTERO SANZ N° 161 OF. 601, PROVIDENCIA,SANTIAGO,REGIÓN METROPOLITANA, CHILE.
			4.- No se aceptarán facturas por mayor valor que el arriba especificado.
			5.- Las consultas sobre pagos de facturas al fono 562-232445000 o a email administracion.cl@api-ux.com
			6.- Mail recepción de documentos administracion.cl@api-ux.com.
			7.- IMPORTANTE: A partir del 01 de septiembre de 2018, las Facturas Electrónicas asociadas a Servicios que no contengan el número de Orden de Compra en los campos respectivos del XML, serán rechazados e invalidados ante el SII, debiendo ser emitidos nuevamente de forma correcta.
			8.- Condición de pago: {0}
			9.- Tipo de cambio UF {1}""".format(self.payment_type,str(date.day)+'/'+str(date.month)+'/'+str(date.year))


	@api.multi
	@api.onchange('employee_id')
	def onchange_employee_id(self):
		for record in self:
			record.boss_id = record.employee_id.parent_id.id

	@api.multi
	def _check_current_user(self):
		for record in self:
			if record.boss_id.user_id.id == self.env.user.id and record.state == 'approved':
				record.is_boss = True
			else:
				record.is_boss = False

	@api.multi
	def _check_solicitant(self):
		for record in self:
			if record.employee_id.user_id.id == self.env.user.id and record.state == 'approved':
				record.is_solicitant = True
			else:
				record.is_solicitant = False

	@api.multi
	def approve_solicitant(self):
		for record in self:
			record.new_states = 'Aprobado por solicitante'
			self.send_mail(74)
			record.num_approves += 1
				

	@api.multi
	def approve_department(self):
		for record in self:
			record.new_states = 'Aprobado por departamento'
			self.send_mail(75)
			record.num_approves += 1

	@api.multi
	def approve_boss(self):
		for record in self:
			if record.amount_total < 500000:
				record.new_states = 'Aprobado por gerente'
				self.send_mail(77, done=True)
				record.num_approves += 2
			else:
				record.new_states = 'Aprobado por jefe'
				self.send_mail(76)
				record.num_approves += 1
				
	@api.multi
	def approve_manager(self):
		for record in self:
			record.new_states = 'Aprobado por gerente'
			self.send_mail(77, done=True)
			record.num_approves += 1

	def change_states(self):
		for po in self.search([]):
			po.num_approves = 4
			invoiced = 0
			total = 0
			for line in po.order_line:
				if line.invoiced:
					invoiced += 1
					line.invoiced_text = 'Facturado'
				else:
					line.invoiced_text = 'No facturado'
				total += 1
			difference = total - invoiced
			if difference == 0:
				if po.state == 'cancel':
					po.new_states = 'Cancelado'
				else:
					po.state = 'approved'
					po.new_states = 'Facturado'
			elif difference == total:
				if po.state == 'cancel':
					po.new_states = 'Cancelado'
				else:
					po.state = 'approved' 
					po.new_states = 'Aprobado por gerente'
			else:
				if po.state == 'cancel':
					po.new_states = 'Cancelado'
				else:
					po.state = 'approved'
					po.new_states = 'Parcialmente facturado'


	def send_mail(self, _id, done=False):
		email_template = self.env['email.template'].search([('id', '=', _id)])
		values = email_template.generate_email(_id, self.id)
		if done:
			val = values.get('attachments')
			attachment = {'name': 'orden_compra.pdf',
						'datas': val[0][1],
						'datas_fname':'orden_compra.pdf',
						'type': 'binary'}
			attach_obj = self.env['ir.attachment'].create(attachment)
			values['attachment_ids'] = [(4, attach_obj.id)]
		mail_mail_obj = self.env['mail.mail']
		msg = mail_mail_obj.create(values)
		msg.send()

	@api.one
	def copy(self, default=None):
		default = dict(default or {})
		res = super(purchase_order, self).copy(default)
		for line in res.order_line:
			line.invoiced_text = 'No facturado'
		return res

	@api.multi
	def replace_new_action_cancel_draft(self):
		for po in self:
			po.new_states = 'Borrador'
		super(purchase_order, self).new_action_cancel_draft()

	@api.multi
	def replace_new_action_cancel(self):
		for po in self:
			po.new_states = 'Cancelado'
			po.send_mail(79)
		super(purchase_order, self).new_action_cancel()

	@api.multi
	def replace_wkf_approve_order(self):
		for po in self:
			if po.num_approves == 4:
				po.new_states = 'Aprobado por gerente'
			elif po.num_approves == 3:
				po.new_states = 'Aprobado por jefe'
			elif po.num_approves == 2:
				po.new_states = 'Aprobado por departamento'
			elif po.num_approves == 1:
				po.new_states = 'Aprobado por solicitante'
			else:
				po.new_states = 'Ingresado'
			for line in po.order_line:
				line.state = 'confirmed'


		super(purchase_order, self).wkf_approve_order()


	def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
		"""Collects require data from purchase order line that is used to create invoice line
		for that purchase order line
		:param account_id: Expense account of the product of PO line if any.
		:param browse_record order_line: Purchase order line browse record
		:return: Value for fields of invoice lines.
		:rtype: dict
		"""
		_taxes_ids = []
		for tax in order_line.taxes_id:
			_taxes_ids.append(tax.id)
		return {
			'name': order_line.name,
			'account_id': order_line.account_account_id.id,
			'price_unit': order_line.price_unit or 0.0,
			'quantity': order_line.product_qty,
			'product_id': order_line.product_id.id or False,
			'uos_id': False,
			'account_analytic_id': order_line.account_analytic_id.id,
			'purchase_line_id': order_line.id,
			'cost_center_id': order_line.cost_center_id.id,
			'invoice_line_tax_id': [(6, 0, _taxes_ids)]}

	def create(self, cr, uid, vals, context=None):
		res = super(purchase_order, self).create(cr, uid, vals, context)
		self.browse(cr, uid, res, context=None).send_mail(78)
		self.browse(cr, uid, res, context=None).invoice_method = 'manual'
		return res


class account_invoice(models.Model):
	_inherit = "account.invoice"
	invoice_type = fields.Selection([('Boleta', 'Boleta'), ('Factura', 'Factura')], 'Tipo', required=True)

	@api.onchange('invoice_type, partner_id', 'supplier_invoice_number')
	def onchange_invoice_type(self):
		_dict = {'Boleta': 'BHE', 'Factura': 'FCE'}
		if (self.partner_id) and (self.supplier_invoice_number) and (self.type not in ['in_refund', 'out_refund']):
			if self.invoice_type in _dict.keys():
				self.reference = _dict[self.invoice_type] + '_' + self.supplier_invoice_number + '_' + self.partner_id.name

			elif self.type == 'out_invoice':
				self.reference = 'FVE_' + self.supplier_invoice_number + '_' + self.partner_id.name

class purchase_order_line(models.Model):
	_inherit = 'purchase.order.line'
	cost_center_id = fields.Many2one('account.cost.center', 'Centro de costos')
	account_account_id = fields.Many2one('account.account', 'Cuenta')
	invoiced_text = fields.Char('Facturación', default='No facturado', readonly=True)

class account_cost_center(models.Model):
	_inherit = 'account.cost.center'
	purchase_order_line_ids =fields.One2many('purchase.order.line' , 'cost_center_id', 'Purchase order lines')

class account_account(models.Model):
	_inherit = 'account.account'
	purchase_order_line_ids =fields.One2many('purchase.order.line' , 'account_account_id', 'Purchase order lines')

class payment_order(models.Model):
	_inherit = 'payment.order'
	excel_report = fields.Binary('Generar reporte')
	filename = 'ordenes_pago.xls' 

	@api.multi
	def generate_excel_report(self):
		stream = StringIO()
		book = xlwt.Workbook(encoding='utf-8')
		sheet = book.add_sheet(u'Sheet1')
		sheet.write(0, 0, 'Cta_origen')
		sheet.write(0, 1, 'moneda_origen')
		sheet.write(0, 2, 'Cta_destino')
		sheet.write(0, 3, 'moneda_destino')
		sheet.write(0, 4, 'Cod_banco')
		sheet.write(0, 5, 'RUT benef.')
		sheet.write(0, 6, 'nombre benef.')
		sheet.write(0, 7, 'Mto Total')
		sheet.write(0, 8, 'Glosa TEF')
		sheet.write(0, 9, 'Correo')
		sheet.write(0, 10, 'Glosa correo')
		sheet.write(0, 11, 'Glosa Cartola Cliente')
		sheet.write(0, 12, 'Glosa Cartola Beneficiario')
		for counter, line in enumerate(self.line_ids):
			sheet.write(counter + 1, 0, '69357970')
			sheet.write(counter + 1, 1, line.company_currency.name)
			sheet.write(counter + 1, 2, line.bank_id.acc_number)
			sheet.write(counter + 1, 3, line.company_currency.name)
			sheet.write(counter + 1, 4, line.bank_id.bank_sbif)
			sheet.write(counter + 1, 5, line.partner_id.display_rut)
			sheet.write(counter + 1, 6, line.partner_id.name)
			sheet.write(counter + 1, 7, line.amount_currency)
			sheet.write(counter + 1, 8, line.communication)
			sheet.write(counter + 1, 9, line.partner_id.email)
			sheet.write(counter + 1, 10, line.communication)
			sheet.write(counter + 1, 11, line.communication)
			sheet.write(counter + 1, 12, line.communication)
		book.save(stream)
		self.excel_report = base64.encodestring(stream.getvalue())
		return {'type' : 'ir.actions.act_url', 
						'url': '/web/binary/saveas?model=payment.order&field=excel_report&id={0}&filename_field={1}'.format(self.id, self.filename),
						'target': 'self'}


class hr_employee(models.Model):
	_inherit = "hr.employee"
	purchase_order_employee_id= fields.One2many('purchase.order', 'employee_id', 'Solicitado por')
	purchase_order_boss_id= fields.One2many('purchase.order', 'boss_id', 'Jefe')

class purchase_line_invoice(models.Model):

	_inherit = 'purchase.order.line_invoice'


	def makeInvoices(self, cr, uid, ids, context=None):

		"""
			 To get Purchase Order line and create Invoice
			 @param self: The object pointer.
			 @param cr: A database cursor
			 @param uid: ID of the user currently logged in
			 @param context: A standard dictionary
			 @return : retrun view of Invoice
		"""

		if context is None:
			context={}

		record_ids =  context.get('active_ids',[])
		if record_ids:
			res = False
			invoices = {}
			invoice_obj = self.pool.get('account.invoice')
			purchase_obj = self.pool.get('purchase.order')
			purchase_line_obj = self.pool.get('purchase.order.line')
			invoice_line_obj = self.pool.get('account.invoice.line')
			account_jrnl_obj = self.pool.get('account.journal')

			def multiple_order_invoice_notes(orders):
				notes = ""
				for order in orders:
					notes += "%s \n" % order.notes
				return notes



			def make_invoice_by_partner(partner, orders, lines_ids):
				"""
					create a new invoice for one supplier
					@param partner : The object partner
					@param orders : The set of orders to add in the invoice
					@param lines : The list of line's id
				"""
				name = orders and orders[0].name or ''
				journal_id = account_jrnl_obj.search(cr, uid, [('type', '=', 'purchase')], context=None)
				journal_id = journal_id and journal_id[0] or False
				a = partner.property_account_payable.id
				inv = {
					'name': name,
					'origin': name,
					'type': 'in_invoice',
					'journal_id':journal_id,
					'reference' : partner.ref,
					'account_id': a,
					'partner_id': partner.id,
					'invoice_line': [(6,0,lines_ids)],
					'currency_id' : orders[0].currency_id.id,
					'comment': multiple_order_invoice_notes(orders),
					'payment_term': orders[0].payment_term_id.id,
					'fiscal_position': partner.property_account_position.id
				}
				inv_id = invoice_obj.create(cr, uid, inv)
				for order in orders:
					order.write({'invoice_ids': [(4, inv_id)]})
				return inv_id
			#ACA SE CREAN LAS LINEAS DE LAS FACTURAS
			res = []
			validator = True
			for line in purchase_line_obj.browse(cr, uid, record_ids, context=context):
				if line.order_id.num_approves < 4:
					validator = False
					raise Warning(('No puedes crear facturas a partir de un pedido de compra no aprobado.'))

			if validator:
				for line in purchase_line_obj.browse(cr, uid, record_ids, context=context):
					if (not line.invoiced) and (line.state not in ('draft', 'cancel')):
						if not line.partner_id.id in invoices:
							invoices[line.partner_id.id] = []
						acc_id = purchase_obj._choose_account_from_po_line(cr, uid, line, context=context)
						inv_line_data = purchase_obj._prepare_inv_line(cr, uid, acc_id, line, context=context)
						inv_line_data.update({'origin': line.order_id.name})
						inv_id = invoice_line_obj.create(cr, uid, inv_line_data, context=context)
						purchase_line_obj.write(cr, uid, [line.id], {'invoiced': True, 'invoice_lines': [(4, inv_id)]})
						purchase_line_obj.write(cr, uid, [line.id], {'invoiced_text': 'Facturado'})
						invoices[line.partner_id.id].append((line,inv_id))

				#ACA SE CREAN LAS FACTURAS CON LAS LINEAS CORRESPONDIENTES
				
				for result in invoices.values():
					il = map(lambda x: x[1], result)
					orders = list(set(map(lambda x : x[0].order_id, result)))
					total, difference = self.calculate_purchase_order_invoiced_amounts(orders[0])
					if difference == 0:
						orders[0].new_states = 'Facturado'
					elif difference == total:
						orders[0].new_states = 'Aprobado por gerente'
					else:
						orders[0].new_states = 'Parcialmente facturado'
					res.append(make_invoice_by_partner(orders[0].partner_id, orders, il))

		return {
			'domain': "[('id','in', ["+','.join(map(str,res))+"])]",
			'name': ('Supplier Invoices'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.invoice',
			'view_id': False,
			'context': "{'type':'in_invoice', 'journal_type': 'purchase'}",
			'type': 'ir.actions.act_window'
		}

	def calculate_purchase_order_invoiced_amounts(self, order):
		total = 0
		invoiced = 0
		for order_line in order.order_line:
			if order_line.invoiced:
				invoiced += 1
			total += 1
		difference = total - invoiced
		return (total, difference)




