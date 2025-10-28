# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.tools.float_utils import float_compare

class CrmLead(models.Model):
    _inherit = "crm.lead"

    def write(self, vals):
        # Se la data di chiusura viene modificata, assegna l'opportunità all'utente corrente.
        # Usiamo setdefault per non sovrascrivere un user_id passato esplicitamente dal chiamante.
        if "date_deadline" in vals and not self.env.context.get("skip_assign_on_deadline_change"):
            vals = dict(vals)  # copia per non mutare il dict originale del chiamante
            vals.setdefault("user_id", self.env.uid)
        return super().write(vals)


class CrmLeadCron(models.Model):
    _inherit = "crm.lead"

    @api.model
    def cron_unassign_overdue_deadline(self):
        """Rimuove user_id se la date_deadline è oltre 90 giorni fa."""
        today = fields.Date.context_today(self)
        import datetime as _dt
        if isinstance(today, str):
            today = fields.Date.from_string(today)
        cutoff = today - _dt.timedelta(days=90)
        leads = self.env['crm.lead'].sudo().search([
            ('date_deadline', '!=', False),
            ('date_deadline', '<=', cutoff),
            ('user_id', '!=', False),
        ])
        if leads:
            leads.write({'user_id': False})
        return True