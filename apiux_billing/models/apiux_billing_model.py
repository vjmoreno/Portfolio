# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.tools.safe_eval import safe_eval
import requests


class AccountPreInvoice(models.Model):
    _inherit = 'account.pre_invoice'

    @api.onchange('is_tax_exempt')
    def onchange_is_tax_exempt(self):
        if self.is_tax_exempt == 'si':
            self.document_type = self.env['sii.document_class'].search([('id', '=', '55')])
            self.tax = 0.00
        elif self.is_tax_exempt == 'no':
            self.document_type = self.env['sii.document_class'].search([('id', '=', '54')])
            self.tax = 19.00

    @api.onchange('document_number')
    def onchange_reference(self):
        self.reference = 'FVE_' + self.document_number + '_' + self.client_id.name

    @api.onchange('amount', 'currency_id', 'emission_date')
    def _get_uf(self):

        if self.emission_date:
            base_url = "http://api.sbif.cl/api-sbifv3/recursos_api/uf/"
            apikey = "?apikey=59c44c6a3ed8d27130d419c7406fdeee0ce84823"
            data_format = "&formato=json"

            valor_uf = 0.0
            try:
                year = self.emission_date[0:4]
                month = self.emission_date[5:7]
                day = self.emission_date[8:10]

                ufurl = base_url + str(year) + "/" + str(month) + "/dias/" + str(day) + apikey + data_format

                r = requests.get(ufurl)
                data = r.text
                # eval data as dict
                raw_data = safe_eval(data)
                raw_list = raw_data.get('UFs', False)
                raw_value = raw_list[0]["Valor"]
                # replace and correct decimal point and thousands divider
                valor_str = raw_value.replace(".", "").replace(",", ".")
                valor_uf = float(valor_str)
            except:
                pass
            self.uf_value = valor_uf


class Invoice(models.TransientModel):
    _inherit = 'project.invoice.wizard'
    document_type = fields.Many2one('sii.document_class',
                                    string="Tipo de documento",
                                    default=lambda self: self.env['sii.document_class'].search([('id', '=', '54')]))
    tax = fields.Float(string="Impuesto (%)", default=19.00)

    @api.onchange('is_tax_exempt')
    def onchange_is_tax_exempt(self):
        if self.is_tax_exempt == 'si':
            self.document_type = self.env['sii.document_class'].search([('id', '=', '55')])
            self.tax = 0.00
        elif self.is_tax_exempt == 'no':
            self.document_type = self.env['sii.document_class'].search([('id', '=', '54')])
            self.tax = 19.00

    @api.onchange('amount')
    def onchange_amount(self):
        if len(str(self.amount).split('.')) > 1:
            if len(str(self.amount).split('.')[1]) > 2:
                return {'value': {},
                        'warning': {'title': 'Atencion!', 'message': 'El monto neto debe tener maximo 2 decimales'}}

    @api.one
    def send_invoice(self):
        self.ensure_one()
        if self.is_tax_exempt == 'no' and self.tax == 0:
            raise models.ValidationError("Por favor ingresa el valor de impuesto >0")

        # default_currency=self.env['res.currency'].search([('name','=',self.money.upper())])
        default_clp = self.env['res.currency'].search([('name', '=', 'CLP')])

        values = {
            'company_id': self.company_id.id,
            'client_id': self.client_id.id,
            'project_id': self.project_id.id,
            'projection_id': self.projection_id.id,
            'hes': self.hes,
            'contract': self.contract,
            'oc': self.oc,
            'glosa': self.glosa,
            'amount': self.amount,
            'is_tax_exempt': self.is_tax_exempt,
            'tax': self.tax,
            'money': self.money,
            'clp_id': default_clp.id,
            'uf_value': self.uf_value,
            'dolar_value': self.dolar_value,
            'total_clp': self.total_clp,
            'emission_date': self.emission_date,
            'projection_status': self.pre_invoice_state,
            'document_type': self.document_type.id,
            'document_number': self.document_number,
            'invoice_product_id': self.env['product.product'].search([('id', '=', '1')]).id,
            'invoice_account_id': self.env['account.account'].search([('id', '=', '3635')]).id,
            'invoice_account_receivable_id': self.env['account.account'].search([('id', '=', '1239')]).id
        }

        lines_list = []
        lvalues = {}
        sequence = 1

        # find period id from emission date

        period_obj = self.env['account.period']
        period_id = period_obj.search(
            [('date_start', '<=', self.emission_date), ('date_stop', '>=', self.emission_date),
             ('company_id', '=', self.company_id.id), ('special', '=', False)])

        lvalues = {}

        lvalues['projection_id'] = self.projection_id.id
        lvalues['sequence'] = sequence
        lvalues['name'] = self.glosa
        lvalues['currency_id'] = self.currency_id.id
        lvalues['company_id'] = self.company_id.id
        lvalues['period_id'] = period_id.id
        lvalues['quantity'] = 1
        lvalues['amount'] = self.amount
        lvalues['amount_clp'] = self.total_clp
        lvalues['product_id'] = self.env['product.product'].search([('id', '=', '1')]).id
        lvalues['account_id'] = self.env['account.account'].search([('id', '=', '3635')]).id
        if self.is_tax_exempt == 'no':
            lvalues['taxes_id'] = [(4, 1)]

        lines_list.append((0, 0, lvalues))
        sequence += 1

        values['line_ids'] = lines_list
        res = self.env['account.pre_invoice'].create(values)
        res.amount = self.amount
        res.total_clp = self.total_clp
        res.currency_id = self.env['res.currency'].search([('name', '=', str(self.money).upper())]).id
        res.send_date = fields.Date.today()

        if not res:
            raise AssertionError("No se pudo ingresar la factura.")
        else:
            self.projection_id.write({'state': 'preinvoiced'})

    @api.onchange('amount', 'currency_id', 'emission_date')
    def _get_uf(self):

        if self.emission_date:
            base_url = "http://api.sbif.cl/api-sbifv3/recursos_api/uf/"
            apikey = "?apikey=59c44c6a3ed8d27130d419c7406fdeee0ce84823"
            data_format = "&formato=json"

            valor_uf = 0.0
            try:
                year = self.emission_date[0:4]
                month = self.emission_date[5:7]
                day = self.emission_date[8:10]

                ufurl = base_url + str(year) + "/" + str(month) + "/dias/" + str(day) + apikey + data_format

                r = requests.get(ufurl)
                data = r.text
                # eval data as dict
                raw_data = safe_eval(data)
                raw_list = raw_data.get('UFs', False)
                raw_value = raw_list[0]["Valor"]
                # replace and correct decimal point and thousands divider
                valor_str = raw_value.replace(".", "").replace(",", ".")
                valor_uf = float(valor_str)
            except:
                pass
            self.uf_value = valor_uf


class Invoice(models.TransientModel):
    _inherit = 'project.outsourcing.invoice.wizard'
    document_type = fields.Many2one('sii.document_class',
                                    string="Tipo de documento",
                                    default=lambda self: self.env['sii.document_class'].search([('id', '=', '54')]))
    tax = fields.Float(string="Impuesto (%)", default=19.00)

    @api.onchange('is_tax_exempt')
    def onchange_is_tax_exempt(self):
        if self.is_tax_exempt == 'si':
            self.document_type = self.env['sii.document_class'].search([('id', '=', '55')])
            self.tax = 0.00
        elif self.is_tax_exempt == 'no':
            self.document_type = self.env['sii.document_class'].search([('id', '=', '54')])
            self.tax = 19.00

    @api.multi
    def action_send(self):
        self.ensure_one()

        if self.is_tax_exempt == 'no' and self.tax == 0:
            raise models.ValidationError("Por favor ingresa el valor de impuesto >0")

        values = {
            'company_id': self.company_id.id,
            'client_id': self.partner_id.id,
            'project_id': self.project_id.id,
            'invoice_account_receivable_id': self.partner_id.property_account_receivable.id or False,
            'hes': self.hes,
            'contract': self.contract,
            'oc': self.oc,
            'glosa': self.glosa,
            'money': self.money,
            'is_tax_exempt': self.is_tax_exempt,
            'tax': self.tax,
            'currency_id': self.currency_id.id,
            'clp_id': self.clp_id.id,
            'uf_value': self.uf_value,
            'dolar_value': self.dolar_value,
            'total_clp': self.total_clp,
            'emission_date': self.emission_date,
            'document_type': self.document_type.id,
            'send_date': self.send_date,
            'projection_status': 'pendiente',
            'invoice_product_id': self.env['product.product'].search([('id', '=', '1')]).id,
            'invoice_account_id': self.env['account.account'].search([('id', '=', '3635')]).id,
            'invoice_account_receivable_id': self.env['account.account'].search([('id', '=', '1239')]).id

        }

        # create lines for Prefactura

        lines_list = []
        lvalues = {}
        sequence = 1

        for line in self.line_ids:
            lvalues = {}

            temp_clp = 0
            # here we need to calculate the amounts
            if self.currency_id.name == 'USD':
                temp_clp = round(self.dolar_value * float(line.line_amount))
            elif self.currency_id.name == 'UF':
                temp_clp = round(self.uf_value * float(line.line_amount))
            elif self.currency_id.name == 'CLP':
                temp_clp = float(line.line_amount)

            lvalues['sequence'] = sequence
            lvalues['name'] = line.outsourcing_id.name
            lvalues['outsourcing_id'] = line.outsourcing_id.id
            lvalues['currency_id'] = line.currency_id.id
            lvalues['company_id'] = line.company_id.id
            lvalues['period_id'] = line.period_id.id
            lvalues['quantity'] = line.quantity
            lvalues['amount'] = line.line_amount
            lvalues['amount_clp'] = temp_clp

            lines_list.append((0, 0, lvalues))
            sequence += 1

        values['line_ids'] = lines_list
        res = self.env['account.pre_invoice'].create(values)

        if not res:
            raise AssertionError("No se pudo ingresar la factura.")
        else:
            for line in self.line_ids:
                line.outsourcing_id.write({'state': 'preinvoiced'})

    def _get_uf(self):

        if self.emission_date:
            base_url = "http://api.sbif.cl/api-sbifv3/recursos_api/uf/"
            apikey = "?apikey=59c44c6a3ed8d27130d419c7406fdeee0ce84823"
            data_format = "&formato=json"

            valor_uf = 0.0
            try:
                year = self.emission_date[0:4]
                month = self.emission_date[5:7]
                day = self.emission_date[8:10]

                ufurl = base_url + str(year) + "/" + str(month) + "/dias/" + str(day) + apikey + data_format

                r = requests.get(ufurl)
                data = r.text
                # eval data as dict
                raw_data = safe_eval(data)
                raw_list = raw_data.get('UFs', False)
                raw_value = raw_list[0]["Valor"]
                # replace and correct decimal point and thousands divider
                valor_str = raw_value.replace(".", "").replace(",", ".")
                valor_uf = float(valor_str)
            except:
                pass
            self.uf_value = valor_uf

    @api.model
    def create(self, values):
        res = super(Invoice, self).create(values)
        res._get_uf()
        res.document_type = self.env['sii.document_class'].search([('id', '=', '54')])
        return res
