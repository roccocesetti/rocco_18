# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Portal Stock Scrap Orders',
    'version': '18.0.1.0',
    'sequence': 1,
    'category': 'Warehouse',
    'description':
        """
This Odoo application allows portal users to access scrap orders. Portal User can also print pdf report of the scrap order

Odoo Features
Portal User can access Scrap Orders
Portal User can print pdf report of Scrap Order
Sort Scrap Order records by below options:
Name
Product
Filter Scrap Order records by below options:
All
Last 30 Days
Last 7 Days
Last Week
This Month
Today
This Week
This Year
Yesterday
Group Scrap Order records by below options:
All
Product
Search Scrap Order records by below options:
Search in Product
Search in Source Location
Search in Scrap Location
Search in State
Search in All

Portal user access Scrap Order
Download Scrap Order as PDF Report
Various options provided to Sort Scrap Order records
Various options provided to Filter Scrap Order records
Various options provided to Group Scrap Order records
Various options provided to Search Scrap Order records

Portal Stock Scrap Orders to allow portal user to see Delivery order,view Scrap Orders , Portal Scrap Orders filter, Portal Scrap Orders filter by date,company, partner Scrap Orders website, Access portal Scrap Orders website,website Scrap Orders details portal,Website Portal Scrap order full details

    """,
    'summary': 'Portal Stock Scrap Orders to allow portal user to see Delivery order view Scrap Orders Portal Scrap Orders filter Portal Scrap Orders filter by date company partner Scrap Orders website Access portal Scrap Orders website website Scrap Orders details portal Website Portal Scrap order full details',
    'depends': ['stock','website','dev_scrap_report'],
    'data': [
        'security/ir.model.access.csv',
        'views/scrap_view.xml',
        'views/scrap_portal_templates.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'https://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':22.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/nSKyq-1SJAY',
    "license":"LGPL-3",
    'pre_init_hook' :'pre_init_check',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
