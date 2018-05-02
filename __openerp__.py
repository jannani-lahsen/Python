{
	"name": "Pop Up - Purchase cost",
	"version": "Avril  v1.0",
	"depends": ["base","product", "purchase", "sale","popup_stock_report"],
	"author": "Lahsen Jannani",
	"category": "Test",
	"description": """\n
	Purchase cost : Ce module permet de définir le cout d'achat standard des articles achetés en se basant sur la moyenne pondérée
""",
	"data": [
		"wizard/wizard_purchase_cost_view.xml",
		"view/view_popup_analytic_price.xml",
		"report/report_purchase_cost.xml",
        "wizard/export_view.xml",
		"data.xml",
		#"security/ir.model.access.csv",


		#all other data files, except demo data and tests
	],
	"demo": [
		#files containg demo data
	],
	"test": [
		#files containg tests
	],
	"installable": True,
	"auto_install": False,
	"application": True,
	"repo_id": "https://github.com/imlopes/odoo-dev#SummerParty",
}
