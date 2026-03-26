# -*- coding: utf-8 -*-
{
    "name": "prof_udempharma_mrp",
    "version": "18.0.1.0.0",
    "category": "mrp",
    "summary": "Portal: show customer stock pickings (deliveries/receipts) + PDF download.",
    "license": "LGPL-3",
    "author": "Rocco Cesetti (custom)",
    "depends": ["portal", "website", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/mo_overview_wizard_views.xml",
    ],

    "installable": True,
    "application": False,
}
