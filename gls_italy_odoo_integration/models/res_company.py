# -*- coding: utf-8 -*-
from odoo import fields, models, api


class GLSResCompany(models.Model):
    _inherit = 'res.company'

    use_gls_italy_shipping_provider = fields.Boolean(copy=False, string="Are You Using GLS Italy ?",
                                                     help="If use GLS Italy shipping Integration than value set TRUE.",
                                                     default=False)

    gls_italy_sede = fields.Char(string="GLS ITALY Sede", help="Enter gls italy's sede number")
    gls_italy_customer_code = fields.Char(string="GLS ITALY Customer Code", help="Enter gls italy's customer code")
    gls_italy_password = fields.Char(string="GLS ITALY Password", help="Enter gls italy's account password")
    gls_italy_contract_code = fields.Char(string="GLS ITALY Contract Code", help="Enter gls Italy ")
    gls_italy_api_url = fields.Char(string="GLS ITALY API URl", help="Enter gls italy api url", default="https://labelservice.gls-italy.com/ilswebservice.asmx")