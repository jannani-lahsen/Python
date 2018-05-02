# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp import models, tools, SUPERUSER_ID, api, exceptions
import base64
import StringIO
import xlwt
from datetime import datetime, date
import time

class popup_wizard_purchase_export(osv.TransientModel):

    _name = "purchase.report.wizard_analysis_achat"

    _table = "purchase_report_wizard_analysis_achat"

    _columns = {
        'product_ids': fields.many2many('product.product', string='Products'),
        'category_ids': fields.many2many('product.category', string='Category'),
        'google_url': fields.char(string='Google URL'),
        'export_total': fields.boolean(string='All Years', default=False),
        'state': fields.selection([('choose', 'choose'),  # choose date
                                   ('get', 'get')]),
        "start_date": fields.date(string="Start date"),
        "end_date": fields.date(string="End date"),
        "last": fields.date(string="End date"),
    }

    _defaults = {
        'state': 'choose',
        'start_date': time.strftime('2017-01-01'),
        'end_date': time.strftime('2017-12-31')
    }

    @api.multi
    def prepare_export_data_products_annexes(self):

        headers_annexes = ['Article', 'Prix', 'Moyenne pondérée', 'Nombre de fournisseurs', 'Nombre des commandes',
                           'Total des quantités commandées', 'Total des prix', 'Quantité commandée par fournisseur',
                           'Montant par fournisseur']
        if self.category_ids:
            product_ids = [x.id for x in self.category_ids]
            products_annexes = self.env['product.template'].search([('categ_id', 'in', product_ids)])
        if self.product_ids:
            product_ids = [x.product_tmpl_id.id for x in self.product_ids]
            products_annexes = self.env['product.template'].search([('id', 'in', product_ids)])
        # products_annexes = self.env['product.template'].search([('purchase_ok', '=', True), ('type', '!=', 'service')])
        sheets = {}
        result_ann = [headers_annexes]
        for ann in products_annexes:
            name = ann.name
            standard_price = ann.standard_price
            average_weight = ann.average_weight_func(self.start_date, self.end_date)
            sum_supp = ann.calcul_sum_supp(self.start_date, self.end_date)
            qty = ann.calcul_qty(self.start_date, self.end_date)
            sum_qty = ann.calcul_sum_qty(self.start_date, self.end_date)
            qty_supp = ann.qty_supp(self.start_date, self.end_date)
            price_total = ann.price_total(self.start_date, self.end_date)
            price_supp = ann.price_supp(self.start_date, self.end_date)
            ann_list = [name, standard_price, average_weight, sum_supp, sum_qty, qty, price_total, qty_supp, price_supp]
            result_ann.append(ann_list)
        sheets['articles_annexes'] = {'sheet_name': 'Purchase cost - Analyse Cout Achat', 'sheet_data': result_ann}
        return sheets, headers_annexes


    @api.multi
    def create_report_cout_achat(self):

        popup_auth_obj = self.env['popup.auth_functions']

        sheets, headers = self.prepare_export_data_products_annexes()
        folder_name = "Analyse Comptables"
        file_name = "Analyse Cout d'achat"
        # spreadsheet_id="1usIPXwE6Ms9qKhpN4ngh08n5v5fe7A6Vit977Z-dJw8"
        sheet_report = popup_auth_obj.create_sheet_report(sheets, headers, file_name, folder_name, share_folder=False)

        return sheet_report


