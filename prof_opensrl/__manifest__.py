# -*- coding: utf-8 -*-
{
    'name': "open srl",
    'author':" Rocco cesetti",
    'countries': ['it'],
    'website': 'https://www.ideawork.link',
    'category': 'Sales/CRM',
    'version': '0.1',
    'description': """
Personalizzazione crm 
    """,
    'depends': ['sales_team','crm', ],
    'data': [
        #'report/udempharma_report.xml',
        #'views/stock_move_line_views.xml',
        #'views/mrp_routing_views.xml',

        'views/crm_lead_views.xml',
        'data/cron.xml',
    ],
    'auto_install': True,    
    'license': 'LGPL-3',
}
