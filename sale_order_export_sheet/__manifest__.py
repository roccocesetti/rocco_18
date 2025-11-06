# -*- coding: utf-8 -*-
{
    "name": "Sale Order Export Sheet",
    "summary": "Export sale orders to a spreadsheet template.",
    "description": """
Export selected sale orders to a pre-defined spreadsheet template
(Google Sheets-like in Odoo). Adds an export wizard, actions, and access rules.
""",
    "version": "18.0.1.0.0",
    "author": "Rocco",
    "website": "https://www.example.com",
    "license": "LGPL-3",  # or "OPL-1" / your actual choice
    "category": "Sales/Reporting",
    "depends": [
        "sale_management",
        "spreadsheet",
        "sale",# or documents_spreadsheet, verify the exact name
    ],
    "data": [
        # "security/ir.model.access.csv",
        # "wizard/sale_export_wizard_views.xml",
        # "views/sale_order_views.xml",
        # "data/sale_export_actions.xml",
    ],
    # "assets": {
    #     "web.assets_backend": [
    #         "sale_order_export_sheet/static/src/js/*.js",
    #         "sale_order_export_sheet/static/src/xml/*.xml",
    #         "sale_order_export_sheet/static/src/scss/*.scss",
    #     ],
    # },
    "images": ["static/description/icon.png"],  # optional
    "installable": True,
    "application": False,
    # "maintainers": ["rocco"],  # optional
}