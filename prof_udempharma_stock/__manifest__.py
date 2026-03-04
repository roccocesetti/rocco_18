# -*- coding: utf-8 -*-
{
    "name": "prof_udempharma_stock",
    "version": "18.0.1.0.0",
    "category": "Warehouse",
    "summary": "Portal: show customer stock pickings (deliveries/receipts) + PDF download.",
    "license": "LGPL-3",
    "author": "UdemPharma (custom)",
    "depends": ["portal", "website", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "security/stock_picking_portal_rules.xml",
        "views/portal_picking_templates.xml",
    ],

    "installable": True,
    "application": False,
}
