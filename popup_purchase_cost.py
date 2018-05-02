# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp import models, tools, SUPERUSER_ID, api

import time

# from openerp.tools.translate import _
# from openerp.exceptions import Warning
# from openerp.osv import orm
# import logging
# from lxml import etree
# from datetime import datetime, timedelta




class popup_product_template_price(osv.Model):
    _inherit = "product.template"



    _columns = {

        "average_weight": fields.float(string="Average weight", digits=(4, 2)),
        "sum_supp": fields.float(string="Sum of supplier", digits=(4, 2), compute="purchase_cost_calculation"),


        # "sum_order": fields.char(string="Sum of orders", digits=(4, 2)),
    }


    # @api.model
    # def purchase_cost_calculation(self):
    #     pr_update = self.env['wizard.cout.achat']
    #     purchase = pr_update.search([('id', '=', self.id)])
    #     for product in purchase:
    #         product.average_weight = purchase.average_weight


    @api.multi
    def purchase_analyse_cost(self):
        #return {
         #   'type': 'ir.actions.act_window',
          #  'res_model': 'contract.wizard_analysis',
           # 'view_mode': 'form',
            #'target': 'new',
        #}
         return {
             'name': 'Cout d\'achat standard',
             'type': 'ir.actions.act_window',
             'res_model': 'wizard.cout.achat',
             "view_type": 'form',
             "view_mode": 'form',
             'target': 'new',
            # 'res_id': self.id,

         }

    @api.model
    def purchase_model(self):
        pr_update = self.env['product.template']
        purchase = pr_update.search([])
        for product in purchase:
            product.purchase_cost_calculation()


    @api.multi
    def purchase_cost_calculation(self):
        purchase_order_line = self.env['purchase.order.line']
        cout = 0
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id)])
            dict_supplier = {}
            total = 0
            total_qnt = 0
            coutT = 0
            total_tran = 0
            sum_supp = 0
            for line in purchase_line_ids:
                supplier = line.partner_id.id
                if supplier not in dict_supplier:
                    dict_supplier[supplier] = [line]
                    sum_supp += 1
                else:
                    dict_supplier[supplier].append(line)
            product.sum_supp = sum_supp
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

    @api.multi
    def compare_func(self):
        compare = ''
        if self.standard_price == self.average_weight: compare = 'ok'
        else: compare = 'Nok'
        return compare

    @api.multi
    def compute_report(self):
        '''
        This function prints the request analysis
        '''
        # assert len(self.ids) == 1, 'This option should only be used for a single id at a time'
        contract_obj = self.env['product.template']
        # contract_ids = contract_obj.search([('product_id.product_tmpl_id', '=', self.product_id)])
        return self.env['report'].get_action(contract_obj, 'popup_purchase_cost.report_stock_state2')



    @api.multi
    def average_weight_func(self,date_deb,date_fin):
        purchase_order_line = self.env['purchase.order.line']
        cout = 0
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id),('date_planned', '>', date_deb),
                 ('date_planned','<' ,date_fin)])
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

        return coutT

    @api.multi
    def calcul_sum_supp(self,date_deb,date_fin):
        purchase_order_line = self.env['purchase.order.line']
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', date_deb),
                 ('date_planned','<' ,date_fin)])
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
    def calcul_qty(self,date_deb,date_fin):
        purchase_order_line = self.env['purchase.order.line']
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id),('date_planned', '>', date_deb),
                 ('date_planned','<' ,date_fin)])
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
    def calcul_sum_qty(self,date_deb,date_fin):
        purchase_order_line = self.env['purchase.order.line']
        sum_qty = 0
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search([('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', date_deb),
                 ('date_planned','<' ,date_fin)])
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
    def qty_supp(self,date_deb,date_fin):
        purchase_order_line = self.env['purchase.order.line']
        purchase_res_partner = self.env['res.partner']
        cout = 0
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search(
                [('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', date_deb),
                 ('date_planned','<' ,date_fin)])
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
    def price_supp(self,date_deb,date_fin):
        purchase_order_line = self.env['purchase.order.line']
        purchase_res_partner = self.env['res.partner']
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search(
                [('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', date_deb),
                 ('date_planned','<' ,date_fin)])
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
    def price_total(self,date_deb,date_fin):
        purchase_order_line = self.env['purchase.order.line']
        purchase_res_partner = self.env['res.partner']
        for product in self:
            product_id = product.id
            purchase_line_ids = purchase_order_line.search(
                [('product_id.product_tmpl_id', '=', product_id), ('date_planned', '>', date_deb),
                 ('date_planned','<' ,date_fin)])
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


    @api.multi
    def prepare_export_data_products_annexes(self):

        headers_annexes = ['Article', 'Prix', 'Moyenne pondérée','Nombre de fournisseurs','Nombre des commandes','Total des quantités commandées','Total des prix', 'Quantité commandée par fournisseur','Montant par fournisseur']
        product_ids = [x.id for x in self.product_ids]

        products_annexes = self.env['product.template'].search([('id', 'in', product_ids)])
        sheets = {}
        result_ann = [headers_annexes]
        for ann in products_annexes:
            name = ann.name
            standard_price = ann.standard_price
            average_weight = ann.average_weight
            sum_supp = ann.calcul_sum_supp()
            qty = ann.calcul_qty()
            sum_qty = ann.calcul_sum_qty()
            qty_supp = ann.qty_supp()
            price_total = ann.price_total()
            price_supp = ann.price_supp()
            ann_list = [name,standard_price,average_weight,sum_supp,sum_qty,qty,price_total,qty_supp,price_supp]
            result_ann.append(ann_list)
        sheets['articles_annexes'] = {'sheet_name': 'Purchase cost - Analyse Cout Achat', 'sheet_data': result_ann}
        return sheets, headers_annexes

    @api.multi
    def create_report_membrane(self):

        popup_auth_obj = self.env['popup.auth_functions']

        sheets, headers = self.prepare_export_data_products_annexes()
        folder_name = "Analyse Comptables"
        file_name = "Analyse Cout d'achat"
        # spreadsheet_id="1usIPXwE6Ms9qKhpN4ngh08n5v5fe7A6Vit977Z-dJw8"
        sheet_report = popup_auth_obj.create_sheet_report(sheets, headers, file_name, folder_name, share_folder=False)

        return sheet_report