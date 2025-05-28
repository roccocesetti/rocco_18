# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import datetime

class Stockpicking(models.Model):
    _inherit = "stock.picking"
    x_studio_binary_field_2qf_1hgi0u1nt = fields.Binary(attachment=True,  help="Documento di analisi",string='Documento di analisi')
    x_studio_binary_field_2qf_1hgi0u1nt_filename = fields.Char(compute='_x_studio_binary_field_2qf_1hgi0u1nt_filename')
    def _x_studio_binary_field_2qf_1hgi0u1nt_filename(self):
        for record in self:
            record.x_studio_binary_field_2qf_1hgi0u1nt_filename = f'_{record.name}'


class StockProductionLot(models.Model):
    _inherit = "stock.lot"
    def _get_attachments_search_domain(self):
        self.ensure_one()
        #for dom in self:
        #    dom.attachment_id_domain="[('res_id', '=', %s), ('res_model', '=', 'stock.move.line')]" % str(self.id)
        return "[('res_id', '=', %s), ('res_model', '=', 'stock.move.line')]" % str(self.id)
    #attachment_id_domain=fields.Char(compute='_get_attachments_search_domain')
    #attachment_id = fields.Many2one('ir.attachment', string="Documento di analisi", domain='_get_attachments_search_domain')
    document_serialnumber = fields.Binary(attachment=True,  help="Documento di analisi",string='Documento di analisi')
    document_serialnumber_filename = fields.Char(compute='_compute_serialnumber_filename')
    def _compute_serialnumber_filename(self):
        for record in self:
            record.document_serialnumber_filename = f'_{record.name}'


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_attachments_search_domain(self):
        self.ensure_one()
        for dom in self:
            dom.attachment_id_domain="[('res_id', '=', %s), ('res_model', '=', 'stock.move.line')]" % str(self.id)

    expiration_date = fields.Datetime(
        string='Expiration Date', compute='_compute_expiration_date', store=True,
        help='This is the date on which the goods with this Serial Number may'
        ' become dangerous and must not be consumed.',related='lot_id.expiration_date',readonly=False)
    @api.depends('product_id', 'picking_type_use_create_lots', 'lot_id.expiration_date')
    def _compute_expiration_date(self):
        for move_line in self:
            if not move_line.expiration_date and move_line.lot_id.expiration_date:
                move_line.expiration_date = move_line.lot_id.expiration_date
            elif move_line.picking_type_use_create_lots:
                if move_line.product_id.use_expiration_date:
                    if not move_line.expiration_date:
                        move_line.expiration_date = fields.Datetime.today() + datetime.timedelta(days=move_line.product_id.expiration_time)
                else:
                    move_line.expiration_date = False
    #attachment_id_domain=fields.Char(compute='_get_attachments_search_domain')
    #document_serialnumber = fields.Many2one('ir.attachment', string="Documento di analisi",related='lot_id.attachment_id',readonly=False, store=True,
    #                                )
    document_serialnumber = fields.Binary( attachment=True,related='lot_id.document_serialnumber',  help="Documento di analisi",string='Documento di analisi',store=True,)
    document_serialnumber_filename = fields.Char(compute='_compute_serialnumber_filename',related='lot_id.document_serialnumber_filename',store=True,)
    
    #attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Documento di analisi",
    #    help="Attachments that don't come from a message.")
    @api.depends('lot_id', 'expiration_date','lot_id.expiration_date','document_serialnumber','lot_id.document_serialnumber')
    def lot_id_onchange(self):
        for record in self:
            record.lot_id.write({'expiration_date':record.expiration_date,
                                 'document_serialnumber':record.document_serialnumber,
                                 
                                 })
    @api.model_create_multi
    def create(self, vals_list):
        res={}
        if 'expiration_date' in vals_list:
                res.update({'expiration_date':vals_list['expiration_date']})
        if 'document_serialnumber' in vals_list:
                res.update({'document_serialnumber':vals_list['document_serialnumber']})
        if res:
                for record in self:
                    record.lot_id.write(res)
        return models.Model.create(self, vals_list)
    def write(self, vals_list):
        res = super().write(vals_list)
        lot_updates={}
        if 'expiration_date' in vals_list:
                lot_updates.update({'expiration_date':vals_list['expiration_date']})
        if 'document_serialnumber' in vals_list:
                lot_updates.update({'document_serialnumber':vals_list['document_serialnumber']})
        if lot_updates:
                for record in self:
                    record.lot_id.write(lot_updates)
        return res
    def onchange(self, values, field_names, fields_spec):
        if 'expiration_date' in field_names:
            res = {key: val for key, val in values.items() if key == 'expiration_date'}
            for record in self:
                record.lot_id.write(res)
        elif 'document_serialnumber' in field_names:
            res = {key: val for key, val in values.items() if key == 'document_serialnumber'}
            for record in self:
                record.lot_id.write(res)
        return super().onchange(values, field_names, fields_spec)
        
    def _compute_serialnumber_filename(self):
        for record in self:
            record.document_serialnumber_filename = f'_{record.lot_id.name}'

    def _compute_attachment_ids(self):
        for line in self:
            attachment_ids = self.env['ir.attachment'].search(line._get_attachments_search_domain()).ids
            message_attachment_ids = line.mapped('message_ids.attachment_ids').ids  # from mail_thread
            line.attachment_ids = [(6, 0, list(set(attachment_ids) - set(message_attachment_ids)))]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tracking = fields.Selection(default='lot')  # Tracciabilità: lotti
    use_expiration_date = fields.Boolean(default=True)  # Scadenza attiva
    list_price = fields.Float(
        'Sales Price', default=0.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.",
    )

    @api.model
    def _get_mrp_route(self):
        mrp_route = self.env.ref('mrp.route_warehouse0_manufacture', raise_if_not_found=False)
        if mrp_route:
            return self.env['stock.route'].search([('id', '=', mrp_route.id)]).ids
        return []

    route_ids = fields.Many2many('stock.route', string="Routes", default=_get_mrp_route)

    @api.onchange('name')
    def _onchange_set_default_route(self):
        route = self.env.ref('mrp.route_warehouse0_manufacture', raise_if_not_found=False)
        if route and route not in self.route_ids:
            self.route_ids |= route  # aggiunge alla lista esistente
