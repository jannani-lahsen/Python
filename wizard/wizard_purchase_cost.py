# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp import models, tools, SUPERUSER_ID, api
from datetime import datetime, timedelta
# from openerp.tools.translate import _
# from openerp.exceptions import Warning
from openerp.osv import orm
# import logging
# from lxml import etree
import time
from decimal import *


class wizard_analytic_price_template_test(orm.TransientModel):

    _name = 'wizard.cout.achat'
    _description = 'Wizard Analytic Price'


    _columns = {
        "product_id": fields.integer(string="Product id"),
        "average_weight": fields.float(string="Average weight", digits=(4, 2), compute="purchase_cost_calculation"),
        "average_weight_date": fields.float(string="Average weight per date", digits=(4, 2), compute="onchange_purchase_cost_calculation_per_date"),
        "average": fields.text(string="Normal average per supplier", compute="onchange_normal_average_per_supplier"),
        "start_date": fields.date(string="Start date"),
        "end_date": fields.date(string="End date"),
        "sum_supp": fields.char(string="Sum of supplier", digits=(4, 2)),
        "sum_order": fields.char(string="Sum of orders", digits=(4, 2)),
        "total_order": fields.text(string="Total of orders by supplier", digits=(4, 2)),



        #"resume": fields.float(string="resume", digits=(4, 2), compute="resumeF"),
    }

    @api.model
    def get_product_id(self, context):
        if context['active_id']:
            active_id = context['active_id']
            model = context['active_model']
            product_obj = self.env[model].search([('id', '=', active_id)])
            product_id = product_obj
            return product_id
        else:
            return False

    _defaults = {
        'product_id': get_product_id,
        'start_date': time.strftime('2017-01-01'),
        'end_date': time.strftime('2017-12-31')
    }



    @api.depends('product_id')
    @api.multi
    def purchase_cost_calculation(self):
        purchase_order_line = self.env['purchase.order.line']
        cout = 0
        for product in self:
            product_id = product.product_id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id)])
            dict_supplier = {}
            total = 0
            total_qnt = 0
            coutT = 0
            total_tran = 0
            for line in purchase_line_ids:
                supplier = line.partner_id.id
                if supplier not in dict_supplier:
                    dict_supplier[supplier] = [line]
                else:
                    dict_supplier[supplier].append(line)

            for supp in dict_supplier:
                lines = dict_supplier.get(supp)
                for ligne in lines:
                    product_qty = ligne.product_qty
                    price_unit = ligne.price_unit
                    total_qnt += product_qty
                    total += price_unit * product_qty
                cout += (total / total_qnt) * total_qnt
                total = 0
                total_tran += total_qnt
                total_qnt = 0
                coutT = cout / total_tran

            product.average_weight = coutT

    @api.depends('product_id','start_date', 'end_date')
    @api.multi
    def onchange_normal_average_per_supplier(self):
        purchase_order_line = self.env['purchase.order.line']
        purchase_res_partner = self.env['res.partner']
        cout = 0
        for product in self:
            product_id = product.product_id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', self.start_date),('date_planned', '<', self.end_date)])
            dict_supplier = {}
            total = 0
            total_qnt = 0
            coutF = 0
            total_tran = 0
            sum_supp = 0
            for line in purchase_line_ids:
                supplier = line.partner_id.id
                if supplier not in dict_supplier:
                    dict_supplier[supplier] = [line]
                    sum_supp += 1
                else:
                    dict_supplier[supplier].append(line)
            sum_supp_final = " " + "\t Nombre total des fournisseurs : \t" + '\n' +str(sum_supp)
            resume = ''
            resume_quant = ""
            sum_order_final = ""
            sum_order = 0
            for supp in dict_supplier:
                lines = dict_supplier.get(supp)
                coutA = 0
                for ligne in lines:
                    purchase_line_id_part = purchase_res_partner.search([('id', '=', supp)])
                    nomF = purchase_line_id_part.name
                    product_qty = ligne.product_qty
                    price_unit = ligne.price_unit
                    total_qnt += product_qty
                    total += price_unit * product_qty
                    coutA = total / total_qnt
                    sum_order += 1
                total_quant_final = total_qnt
                cout = coutA
                resume += nomF + " " + str(round(cout, 2)) + "  "
                resume_quant += nomF + " " + str(round(total_quant_final, 2)) + "  "
                total = 0
                total_qnt = 0
                sum_order_final = "Nombre total des commandee : " + str(sum_order)
            resume_final = "MN par fournisseurs : " + " " + resume
            resume_quant_final = "Quantite commandee par fournisseur :" + " " + resume_quant + "\n"
            product.total_order = resume_quant_final
            product.sum_order = sum_order_final
            product.sum_supp = sum_supp_final
            product.average = resume_final

    @api.multi
    def compute_update_purchase_cost(self):
        pr_update = self.env['product.template']
        purchase = pr_update.search([('id', '=', self.product_id)])
        purchase.average_weight = self.average_weight

    @api.multi
    def compute_update_purchase_cost_weighted_average(self):
        pr_update = self.env['product.template']
        purchase = pr_update.search([('id', '=', self.product_id)])
        purchase.standard_price = self.average_weight
        purchase.average_weight = self.average_weight

    @api.depends('start_date', 'end_date')
    @api.multi
    def onchange_purchase_cost_calculation_per_date(self):
        purchase_order_line = self.env['purchase.order.line']
        cout = 0
        for product in self:
            product_id = product.product_id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id),('date_planned', '>',self.start_date),('date_planned', '<',self.end_date)])
            dict_supplier = {}
            total = 0
            total_qnt = 0
            coutT = 0
            total_tran = 0
            for line in purchase_line_ids:
                supplier = line.partner_id.id
                if supplier not in dict_supplier:
                    dict_supplier[supplier] = [line]
                else:
                    dict_supplier[supplier].append(line)

            for supp in dict_supplier:
                lines = dict_supplier.get(supp)
                for ligne in lines:
                    product_qty = ligne.product_qty
                    price_unit = ligne.price_unit
                    total_qnt += product_qty
                    total += price_unit * product_qty
                cout += (total / total_qnt) * total_qnt
                total = 0
                total_tran += total_qnt
                total_qnt = 0
                coutT = cout / total_tran

            product.average_weight_date = coutT

    # @api.multi
    # def compute_report(self):
    #     '''
    #     This function prints the request analysis
    #     '''
    #     #assert len(self.ids) == 1, 'This option should only be used for a single id at a time'
    #     contract_obj = self.env['product.template']
    #     #contract_ids = contract_obj.search([('product_id.product_tmpl_id', '=', self.product_id)])
    #     return self.env['report'].get_action(contract_obj, 'popup_purchase_cost.report_stock_state2')





    @api.multi
    def calcul_sum_supp(self):
        purchase_order_line = self.env['purchase.order.line']
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', '2017-01-01'),
                 ('date_planned', '<', '2017-12-31')])
            dict_supplier = {}
            sum_supp = 0
            for line in purchase_line_ids:
                supplier = line.partner_id.id
                if supplier not in dict_supplier:
                    dict_supplier[supplier] = [line]
                    sum_supp += 1
                else:
                    dict_supplier[supplier].append(line)
        return sum_supp

    @api.multi
    def calcul_qty(self):
        purchase_order_line = self.env['purchase.order.line']
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', '2017-01-01'),
                 ('date_planned', '<', '2017-12-31')])
            dict_supplier = {}
            total_qnt = 0
            total_tran = 0
            for line in purchase_line_ids:
                supplier = line.partner_id.id
                if supplier not in dict_supplier:
                    dict_supplier[supplier] = [line]
                else:
                    dict_supplier[supplier].append(line)
            for supp in dict_supplier:
                lines = dict_supplier.get(supp)
                for ligne in lines:
                    product_qty = ligne.product_qty
                    total_qnt += product_qty
                total_tran += total_qnt
                total_qnt = 0

        return total_tran

    @api.multi
    def calcul_sum_qty(self):
        purchase_order_line = self.env['purchase.order.line']
        sum_qty = 0
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', '2017-01-01'),
                 ('date_planned', '<', '2017-12-31')])
            dict_supplier = {}
            for line in purchase_line_ids:
                supplier = line.id
                if supplier not in dict_supplier:
                    dict_supplier[supplier] = [line]
                else:
                    dict_supplier[supplier].append(line)
            for supp in dict_supplier:
                lines = dict_supplier.get(supp)
                for ligne in lines:
                    sum_qty += len(ligne)

        return sum_qty


    @api.multi
    def qty_supp(self):
        purchase_order_line = self.env['purchase.order.line']
        purchase_res_partner = self.env['res.partner']
        cout = 0
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search(
                [('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', '2017-01-01'),
                 ('date_planned', '<', '2017-12-31')])
            dict_supplier = {}
            total = 0
            total_qnt = 0
            sum_supp = 0
            for line in purchase_line_ids:
                supplier = line.partner_id.id
                if supplier not in dict_supplier:
                    dict_supplier[supplier] = [line]
                    sum_supp += 1
                else:
                    dict_supplier[supplier].append(line)
            resume = ''
            resume_quant = ""
            sum_order = 0
            for supp in dict_supplier:
                lines = dict_supplier.get(supp)
                coutA = 0
                for ligne in lines:
                    purchase_line_id_part = purchase_res_partner.search([('id', '=', supp)])
                    nomF = purchase_line_id_part.name
                    product_qty = ligne.product_qty
                    price_unit = ligne.price_unit
                    total_qnt += product_qty
                    total += price_unit * product_qty
                    coutA = total / total_qnt
                    sum_order += 1
                total_quant_final = total_qnt
                cout = coutA
                resume += nomF + " " + str(round(cout, 2)) + " \n "
                resume_quant += nomF + " " + str(round(total_quant_final, 2)) + " \n "
                total = 0
                total_qnt = 0

            return resume_quant

    @api.multi
    def price_supp(self):
        purchase_order_line = self.env['purchase.order.line']
        purchase_res_partner = self.env['res.partner']
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search(
                [('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', '2017-01-01'),
                 ('date_planned', '<', '2017-12-31')])
            dict_supplier = {}
            total = 0
            total_qnt = 0
            sum_supp = 0
            for line in purchase_line_ids:
                supplier = line.partner_id.id
                if supplier not in dict_supplier:
                    dict_supplier[supplier] = [line]
                    sum_supp += 1
                else:
                    dict_supplier[supplier].append(line)
            resume = ''
            resume_quant = ""
            sum_order = 0
            for supp in dict_supplier:
                lines = dict_supplier.get(supp)
                coutA = 0
                for ligne in lines:
                    purchase_line_id_part = purchase_res_partner.search([('id', '=', supp)])
                    nomF = purchase_line_id_part.name
                    product_qty = ligne.product_qty
                    price_unit = ligne.price_unit
                    total_qnt += product_qty
                    total += price_unit * product_qty
                    coutA = total / total_qnt
                    sum_order += 1
                price_total = total
                total_quant_final = total_qnt
                cout = coutA
                resume += nomF + " " + str(round(price_total, 2)) + " \n "
                total = 0
                total_qnt = 0

            return resume

    @api.multi
    def price_total(self):
        purchase_order_line = self.env['purchase.order.line']
        purchase_res_partner = self.env['res.partner']
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search(
                [('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', '2017-01-01'),
                 ('date_planned', '<', '2017-12-31')])
            dict_supplier = {}
            total = 0
            total_qnt = 0
            sum_supp = 0
            price_total = 0
            for line in purchase_line_ids:
                supplier = line.partner_id.id
                if supplier not in dict_supplier:
                    dict_supplier[supplier] = [line]
                    sum_supp += 1
                else:
                    dict_supplier[supplier].append(line)
            sum_order = 0
            for supp in dict_supplier:
                lines = dict_supplier.get(supp)
                for ligne in lines:
                    purchase_line_id_part = purchase_res_partner.search([('id', '=', supp)])
                    nomF = purchase_line_id_part.name
                    product_qty = ligne.product_qty
                    price_unit = ligne.price_unit
                    total_qnt += product_qty
                    total += price_unit * product_qty
                    sum_order += 1
                price_total += round(total, 2)
                total = 0
                total_qnt = 0

            return price_total








