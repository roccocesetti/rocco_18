# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class stock_scrap(models.Model):
    _name = 'stock.scrap'
    _inherit = ['stock.scrap','portal.mixin']

    partner_id = fields.Many2one('res.partner',string="Customer")
    user_id = fields.Many2one('res.users', string='User',default=lambda self: self.env.user)
    scrap_date = fields.Date(string="Date",default=fields.date.today())

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (_('Scrap'), self.name)    

    
    def _compute_access_url(self):
        super(stock_scrap, self)._compute_access_url()
        for scrap in self:
            scrap.access_url = '/my/scrap/%s' % (scrap.id)
#           
#        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
