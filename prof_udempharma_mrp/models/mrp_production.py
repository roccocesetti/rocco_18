# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpProductionOverviewWizard(models.TransientModel):
    _name = 'mrp.production.overview.wizard'
    _description = 'Panoramica multipla ordini di produzione'

    line_ids = fields.One2many(
        'mrp.production.overview.wizard.line',
        'wizard_id',
        string='Righe'
    )

    production_ids = fields.Many2many(
        'mrp.production',
        string='Ordini di produzione'
    )

    @api.model
    def action_open_from_productions(self):
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_("Seleziona almeno un ordine di produzione."))

        productions = self.env['mrp.production'].browse(active_ids).exists()
        if not productions:
            raise UserError(_("Nessun ordine di produzione valido trovato."))

        wizard = self.create({
            'production_ids': [(6, 0, productions.ids)],
        })

        lines_vals = []
        for production in productions:
            for move in production.move_raw_ids.filtered(lambda m: m.state not in ('cancel', 'done')):
                product = move.product_id

                qty_required = move.product_uom_qty
                qty_reserved = sum(move.move_line_ids.mapped('quantity')) if move.move_line_ids else (
                            move.quantity or 0.0)
                qty_available = product.with_context(
                    warehouse=production.picking_type_id.warehouse_id.id
                ).free_qty

                shortage = max(qty_required - qty_reserved, 0.0)

                status = 'available'
                if shortage > 0:
                    status = 'to_order' if qty_available <= 0 else 'partial'

                lines_vals.append({
                    'wizard_id': wizard.id,
                    'production_id': production.id,
                    'product_finished_id': production.product_id.id,
                    'component_id': product.id,
                    'uom_id': move.product_uom.id,
                    'qty_required': qty_required,
                    'qty_reserved': qty_reserved,
                    'qty_available': qty_available,
                    'shortage_qty': shortage,
                    'status': status,
                    'date_planned_start': production.date_start or production.date_planned_start,
                })
        self.env['mrp.production.overview.wizard.line'].create(lines_vals)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Panoramica ordini di produzione'),
            'res_model': 'mrp.production.overview.wizard.line',
            'view_mode': 'list,form',
            'domain': [('wizard_id', '=', wizard.id)],
            'target': 'current',
            'context': {
                'search_default_group_by_component_id': 0,
            },
            'views': [(self.env.ref('prof_udempharma_mrp.view_mrp_production_overview_wizard_line_list').id, 'list')],
        }


    @api.model
    def action_reorder_components_from_productions(self):
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_("Seleziona almeno un ordine di produzione."))

        productions = self.env['mrp.production'].browse(active_ids).exists()
        if not productions:
            raise UserError(_("Nessun ordine di produzione valido trovato."))

        raw_moves = productions.mapped('move_raw_ids').filtered(
            lambda m: m.state not in ('done', 'cancel') and m.product_id
        )

        if not raw_moves:
            raise UserError(_("Nessun componente trovato sugli ordini selezionati."))

        products = raw_moves.mapped('product_id')
        if not products:
            raise UserError(_("Nessun prodotto componente trovato."))

        action = self.env['stock.warehouse.orderpoint'].with_context(
            search_default_filter_to_reorder=True,
            search_default_filter_not_snoozed=True,
            default_trigger='manual',
            searchpanel_default_trigger='manual',
        ).action_open_orderpoints()

        action['name'] = _('Riordina componenti MO')
        action['domain'] = [('product_id', 'in', products.ids)]
        action['target'] = 'current'
        return action

class MrpProductionOverviewWizardLine(models.TransientModel):
    _name = 'mrp.production.overview.wizard.line'
    _description = 'Riga panoramica multipla ordini di produzione'
    _order = 'production_id, component_id'

    wizard_id = fields.Many2one(
        'mrp.production.overview.wizard',
        required=True,
        ondelete='cascade'
    )

    production_id = fields.Many2one('mrp.production', string='Ordine di produzione')
    product_finished_id = fields.Many2one('product.product', string='Prodotto finito')
    component_id = fields.Many2one('product.product', string='Componente')
    uom_id = fields.Many2one('uom.uom', string='UdM')

    qty_required = fields.Float(string='Qta richiesta')
    qty_reserved = fields.Float(string='Prenotata')
    qty_available = fields.Float(string='Disponibile')
    shortage_qty = fields.Float(string='Da approvvigionare')

    date_planned_start = fields.Datetime(string='Data prevista')

    status = fields.Selection([
        ('available', 'Disponibile'),
        ('partial', 'Parziale'),
        ('to_order', 'Da ordinare'),
    ], string='Stato')

    def action_replenish(self):
        lines = self.filtered(lambda l: l.component_id and l.shortage_qty > 0)
        if not lines:
            raise UserError(_("Seleziona almeno una riga con quantità da approvvigionare."))

        products = lines.mapped('component_id')

        action = self.env['stock.warehouse.orderpoint']\
            .with_context(
                search_default_filter_to_reorder=True,
                search_default_filter_not_snoozed=True,
                default_trigger='manual',
                searchpanel_default_trigger='manual',
            )\
            .action_open_orderpoints()

        action['domain'] = [('product_id', 'in', products.ids)]
        return action
