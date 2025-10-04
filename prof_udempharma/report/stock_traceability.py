# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.tools import format_datetime
from markupsafe import Markup
from odoo.tools.misc import format_datetime as fmt_dt
import logging
_logger = logging.getLogger(__name__)

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
def _format_duration_hms(seconds):
    if not seconds:
        return "-"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"
def _format_hms(seconds):
    """Ritorna 'HH:MM:SS' da secondi (int/float). Se falsy => '-'."""
    if not seconds:
        return "-"
    try:
        seconds = int(seconds)
    except Exception:
        return "-"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

class MrpStockReport(models.TransientModel):
    _inherit = 'stock.traceability.report'

    #def get_pdf_lines(self, line_data=[]):
    #    # lines = []
    #    # for line in line_data:
    #    #     ...
    #    # return lines
    #    return super().with_context(print_mode=True).get_pdf_lines(line_data or [])
    def get_pdf_lines(self, line_data=None):
        line_data = line_data or []
        return super().get_pdf_lines(line_data)

    def _compute_mrp_meta_from_lines(self, lines):
        """Prova prima a ricavare la mrp.production dal context attivo.
           Se non la trova, fa fallback alle righe come prima."""
        ctx = self.env.context
        prod = None

        # 1) Prendo la produzione direttamente dal contesto se il report è lanciato da mrp.production
        if ctx.get('active_model') == 'mrp.production' and ctx.get('active_id'):
            prod = self.env['mrp.production'].browse(int(ctx['active_id']))

        # 2) Altri lanci: provo a risalire da move line / picking / lot
        elif ctx.get('active_model') == 'stock.move.line' and ctx.get('active_id'):
            ml = self.env['stock.move.line'].browse(int(ctx['active_id']))
            prod = ml.move_id.production_id or ml.move_id.raw_material_production_id

        elif ctx.get('active_model') == 'stock.picking' and ctx.get('active_id'):
            pick = self.env['stock.picking'].browse(int(ctx['active_id']))
            ml = pick.move_ids.move_line_ids[:1]
            if ml:
                prod = ml.move_id.production_id or ml.move_id.raw_material_production_id

        elif ctx.get('active_model') == 'stock.lot' and ctx.get('active_id'):
            lot = self.env['stock.lot'].browse(int(ctx['active_id']))
            ml = self.env['stock.move.line'].search(
                [('lot_id', '=', lot.id), ('state', '=', 'done')],
                limit=1, order='date desc'
            )
            if ml:
                prod = ml.move_id.production_id or ml.move_id.raw_material_production_id

        # Se ho trovato la produzione, costruisco i meta direttamente da lì
        if prod:
            ds = prod.date_start
            # su v18 spesso è 'date_finished'
            df = getattr(prod, 'date_finished', False) or getattr(prod, 'date_planned_finished', False)
            dur_s = (df - ds).total_seconds() if (ds and df) else None
            return {
                'mrp_product_name': prod.product_id.display_name,
                'mrp_date_start': ds,
                'mrp_date_start_fmt': ds and format_datetime(self.env, ds, tz=False, dt_format=False) or False,
                'mrp_date_finished': df,
                'mrp_duration_seconds': dur_s,
                'mrp_duration_human': _format_hms(dur_s) if dur_s else "-",
                'mrp_user_name': prod.user_id and prod.user_id.display_name or False,
                'mrp_picking_type_name': prod.picking_type_id and prod.picking_type_id.display_name or False,
            }

        # Fallback: usa la prima riga come facevi prima (se le righe contengono già i meta)
        first = (lines and lines[0]) or {}
        ds = first.get('mrp_date_start')
        df = first.get('mrp_date_finished')
        dur_s = first.get('mrp_duration_seconds')
        return {
            'mrp_product_name': first.get('mrp_product_name'),
            'mrp_date_start': ds,
            'mrp_date_start_fmt': ds and format_datetime(self.env, ds, tz=False, dt_format=False) or False,
            'mrp_date_finished': df,
            'mrp_duration_seconds': dur_s,
            'mrp_duration_human': first.get('mrp_duration_hms') or _format_hms(dur_s),
            'mrp_user_name': first.get('mrp_user') or first.get('mrp_user_name'),
            'mrp_picking_type_name': first.get('mrp_picking_type') or first.get('mrp_picking_type_name'),
        }

    def get_pdf(self, line_data=None):
        line_data = [] if line_data is None else line_data
        lines = self.with_context(print_mode=True).get_pdf_lines(line_data)  # <-- questa riga cambia
        _logger.info("TRACEABILITY LINES COUNT: %s", len(lines))
        meta_ctx = self._compute_mrp_meta_from_lines(lines)
        _logger.debug("MRP META: %s", meta_ctx)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {'mode': 'print', 'base_url': base_url}
        ctx = self.env.context
        if ctx.get('active_id') and ctx.get('active_model'):
            rcontext['reference'] = self.env[ctx['active_model']].browse(int(ctx['active_id'])).display_name

        body = self.env['ir.ui.view'].with_context(meta_ctx)._render_template(
            "stock.report_stock_inventory_print",
            values=dict(rcontext, lines=lines, report=self, context=self),
        )
        header = self.env['ir.actions.report']._render_template("web.internal_layout", values=rcontext)
        header = self.env['ir.actions.report']._render_template(
            "web.minimal_layout", values=dict(rcontext, subst=True, body=Markup(header.decode()))
        )
        return self.env['ir.actions.report']._run_wkhtmltopdf(
            [body], header=header.decode(), landscape=True,
            specific_paperformat_args={'data-report-margin-top': 30, 'data-report-header-spacing': 25}
        )

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


            # trova la produzione associata alla move_line
            ml = None
            if v.get('model') == 'stock.move.line' and v.get('model_id'):
                ml = self.env['stock.move.line'].browse(v['model_id'])
            production = False
            if ml and ml.move_id:
                # per materie prime
                production = ml.move_id.raw_material_production_id or production
                # per finiti/semi-lavorati
                production = ml.move_id.production_id or production

            # popola i campi produzione (se trovata)
            date_start = date_finished = False
            duration_seconds = False
            user_name = picking_type_name = False
            if production:
                date_start = production.date_start
                mrp_product_name=production.product_id.display_name
                date_finished = getattr(production, 'date_finished', False)  # in 18 è "date_finished"
                if date_start and date_finished:
                    duration_seconds = (date_finished - date_start).total_seconds()
                user_name = production.user_id and production.user_id.display_name or False
                picking_type_name = production.picking_type_id and production.picking_type_id.display_name or False




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
        res_model, res_id, ref = self._get_reference(move_line)
        dummy, is_used = self._get_linked_move_lines(move_line)

        production = move_line.move_id.raw_material_production_id or move_line.move_id.production_id
        mrp_product_name = False
        date_start = date_finished = False
        duration_seconds = False
        user_name = picking_type_name = False
        if production:
            date_start = production.date_start
            date_finished = getattr(production, 'date_finished', False)
            mrp_product_name = production.product_id.display_name
            if date_start and date_finished:
                duration_seconds = (date_finished - date_start).total_seconds()
            user_name = production.user_id and production.user_id.display_name or False
            picking_type_name = production.picking_type_id and production.picking_type_id.display_name or False

        lot = move_line.lot_id
        expiration_date = (lot and (lot.expiration_date or lot.use_date or getattr(lot, 'life_date', False))) or False

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
            'product_qty_uom': "%s %s" % (
            self._quantity_to_str(move_line.product_uom_id, move_line.product_id.uom_id, move_line.quantity),
            move_line.product_id.uom_id.name),
            'lot_name': move_line.lot_id.name,
            'lot_id': move_line.lot_id.id,
            'reference_id': ref,
            'res_id': res_id,
            'res_model': res_model,
            'expiration_date': expiration_date,

            # --- MRP meta (chiavi coerenti) ---
            'mrp_product_name': mrp_product_name,
            'mrp_date_start': date_start,
            'mrp_date_finished': date_finished,
            'mrp_duration_seconds': duration_seconds,
            'mrp_duration_hms': _format_hms(duration_seconds) if duration_seconds else "-",
            'mrp_user_name': user_name,
            'mrp_picking_type_name': picking_type_name,
        }]
        return data


    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        lines = []
        for data in final_vals:
            line = {
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
                'columns': [
                    data.get('reference_id', False),
                    data.get('product_id', False),
                    format_datetime(self.env, data.get('date', False), tz=False, dt_format=False),
                    data.get('lot_name', False),
                    format_datetime(self.env, data.get('expiration_date', False), tz=False, dt_format=False),
                    data.get('product_qty_uom', 0),
                    # (niente MRP qui: le mostri in header/footer)
                ],
                'level': level,
                'unfoldable': data['unfoldable'],
            }
            # --- PROPAGA meta MRP perché _compute_mrp_meta_from_lines li legga ---
            for k in (
                    'mrp_product_name', 'mrp_date_start', 'mrp_date_finished',
                    'mrp_duration_seconds', 'mrp_duration_hms',
                    'mrp_user_name', 'mrp_picking_type_name'
            ):
                if k in data:
                    line[k] = data[k]
            lines.append(line)
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
