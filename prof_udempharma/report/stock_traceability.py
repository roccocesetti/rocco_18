# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.tools import format_datetime
from markupsafe import Markup


rec = 0
def autoIncrement():
    global rec
    pStart = 1
    pInterval = 1
    if rec == 0:
        rec = pStart
    else:
        rec += pInterval
    return rec

class MrpStockReport(models.TransientModel):
    _inherit = 'stock.traceability.report'


    @api.model
    def get_lines(self, line_id=False, **kw):
        lines=super().get_lines(line_id, **kw)
        context = dict(self.env.context)
        model = kw and kw['model_name'] or context.get('model')
        rec_id = kw and kw['model_id'] or context.get('active_id')
        level = kw and kw['level'] or 1
        lines = self.env['stock.move.line']
        move_line = self.env['stock.move.line']
        if rec_id and model == 'stock.lot':
            lines = move_line.search([
                ('lot_id', '=', context.get('lot_name') or rec_id),
                ('state', '=', 'done'),
            ])
        elif  rec_id and model == 'stock.move.line' and context.get('lot_name'):
            record = self.env[model].browse(rec_id)
            dummy, is_used = self._get_linked_move_lines(record)
            if is_used:
                lines = is_used
        elif rec_id and model in ('stock.picking', 'mrp.production'):
            record = self.env[model].browse(rec_id)
            if model == 'stock.picking':
                lines = record.move_ids.move_line_ids.filtered(lambda m: m.lot_id and m.state == 'done')
            else:
                lines = record.move_finished_ids.mapped('move_line_ids').filtered(lambda m: m.state == 'done')
        #move_line_vals = self._lines(line_id, model_id=rec_id, model=model, level=level, move_lines=lines)
        #final_vals = sorted(move_line_vals, key=lambda v: v['date'], reverse=True)
        #lines = self._final_vals_to_lines(final_vals, level)
        # Costruzione dei valori riga con la funzione esistente
        move_line_vals = self._lines(
            line_id,
            model_id=rec_id,
            model=model,
            level=level,
            move_lines=lines,
        )

        # --- AGGIUNTE/RIMOZIONI RICHIESTE ---
        Lot = self.env['stock.lot']
        for v in move_line_vals:
            # Trova un riferimento al lotto nella struttura valori
            lot_ref = v.get('lot_id') or v.get('campo_lot_id') or v.get('lot') or v.get('lot_name')

            lot = False
            if lot_ref:
                # Gestione robusta per vari formati (id int, many2one [id, name], nome stringa)
                if isinstance(lot_ref, int):
                    lot = Lot.browse(lot_ref)
                elif isinstance(lot_ref, (list, tuple)) and lot_ref:
                    lot = Lot.browse(lot_ref[0])
                elif isinstance(lot_ref, str):
                    lot = Lot.search([('name', '=', lot_ref)], limit=1)

            # Inserisci expiration_date del lotto (fallback su use_date/life_date se necessario)
            v['expiration_date'] = (
                    (lot and getattr(lot, 'expiration_date', False)) or
                    (lot and getattr(lot, 'use_date', False)) or
                    (lot and getattr(lot, 'life_date', False)) or
                    False
            )

            # Rimuovi ubicazioni di origine/destinazione (sia id che nomi/display)
            for key in (
                    'location_id', 'location_dest_id',
                    'location_name', 'location_dest_name',
                    'location_id_display', 'location_dest_id_display',
            ):
                v.pop(key, None)
        # --- FINE MODIFICHE ---

        # Ordina per data decrescente e crea le lines finali
        final_vals = sorted(move_line_vals, key=lambda v: v.get('date'), reverse=True)
        lines = self._final_vals_to_lines(final_vals, level)
        return lines

    def _make_dict_move(self, level, parent_id, move_line, unfoldable=False):
        data=super()._make_dict_move(level, parent_id, move_line, unfoldable)
        res_model, res_id, ref = self._get_reference(move_line)
        dummy, is_used = self._get_linked_move_lines(move_line)
        data = [{
            'level': level,
            'unfoldable': unfoldable,
            'date': move_line.move_id.date,
            'parent_id': parent_id,
            'is_used': bool(is_used),
            'usage': self._get_usage(move_line),
            'model_id': move_line.id,
            'model': 'stock.move.line',
            'product_id': move_line.product_id.display_name,
            'product_qty_uom': "%s %s" % (self._quantity_to_str(move_line.product_uom_id, move_line.product_id.uom_id, move_line.quantity), move_line.product_id.uom_id.name),
            'lot_name': move_line.lot_id.name,
            'lot_id': move_line.lot_id.id,
            'expiration_date': move_line.expiration_date,
            #'location_source': move_line.location_id.name,
            #'location_destination': move_line.location_dest_id.name,
            'reference_id': ref,
            'res_id': res_id,
            'res_model': res_model}]
        return data

    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        lines=super()._final_vals_to_lines(final_vals, level)
        lines = []
        for data in final_vals:
            lines.append({
                'id': autoIncrement(),
                'model': data['model'],
                'model_id': data['model_id'],
                'parent_id': data['parent_id'],
                'usage': data.get('usage', False),
                'is_used': data.get('is_used', False),
                'lot_name': data.get('lot_name', False),
                'lot_id': data.get('lot_id', False),
                'reference': data.get('reference_id', False),
                'res_id': data.get('res_id', False),
                'res_model': data.get('res_model', False),
                'columns': [data.get('reference_id', False),
                            data.get('product_id', False),
                            format_datetime(self.env, data.get('date', False), tz=False, dt_format=False),
                            data.get('lot_name', False),
                            format_datetime(self.env, data.get('expiration_date', False), tz=False, dt_format=False),
                            #data.get('location_source', False),
                            #data.get('location_destination', False),
                            data.get('product_qty_uom', 0)],
                'level': level,
                'unfoldable': data['unfoldable'],
            })
        return lines

    def _get_main_lines(self):
        #lines=super()._get_main_lines()
        context = dict(self.env.context)
        context["hide_locations"] = True
        return self.with_context(context).get_lines()

    @api.model
    def get_main_lines(self, given_context=None):
        res = self.search([('create_uid', '=', self.env.uid)], limit=1)
        if not res:
            result = self.create({}).with_context(given_context)._get_main_lines()
        else:
            result = res.with_context(given_context)._get_main_lines()

        # --- aggiungo expiration_date a ogni linea ---
        Lot = self.env['stock.lot']
        for line in result:
            lot_id = line.get('lot_id')
            if lot_id:
                # lot_id di solito è [id, display_name]
                if isinstance(lot_id, (list, tuple)):
                    lot = Lot.browse(lot_id[0])
                else:
                    lot = Lot.browse(lot_id)
                line['expiration_date'] = (
                        lot.expiration_date or lot.use_date or lot.life_date or False
                )

        return result
