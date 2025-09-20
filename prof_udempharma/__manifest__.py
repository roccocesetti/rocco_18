# -*- coding: utf-8 -*-
{
    'name': "Udem farma",
    'author':" Rocco cesetti",
    'countries': ['it'],
    'website': 'https://www.ideawork.link',
    'category': 'Accounting/Localizations/EDI',
    'version': '0.1',
    'description': """
Personalizzazione allegato pdf analisi e modifica data di scadenza lotto
    """,
    'depends': ['stock', 'product_expiry','mrp'],
    'data': [
        'report/udempharma_report.xml',
        'views/stock_move_line_views.xml',
        'views/mrp_routing_views.xml',

        #'views/account_invoice_views.xml',
        #'data/udempharma_template.xml',
    ],
    'auto_install': True,    
    'license': 'LGPL-3',
}
