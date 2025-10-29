# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.tools.float_utils import float_compare
import logging
_logger = logging.getLogger(__name__)

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

class CrmLeadCronPartner(models.Model):
    _inherit = "crm.lead"

    @api.model
    def cron_update_lead_city_from_partner(self, batch_size=1000, dry_run=False):
        """
        Aggiorna crm.lead.city prendendo la città dal partner collegato.
        Logica:
          - Usa commercial_partner_id per coerenza (azienda) e fallback al partner stesso
          - Aggiorna solo se la città del partner esiste e differisce da quella della lead
        Parametri:
          - batch_size: dimensione del lotto per non saturare memoria/lock
          - dry_run: se True non scrive, ma logga cosa farebbe
        Ritorna:
          - dict con contatori utili nel log/monitoraggio
        """
        env = self.env
        Lead = env["crm.lead"].sudo()  # tipicamente il cron gira come admin, ma sudo per sicurezza

        total_seen = 0
        total_updated = 0
        total_skipped = 0

        last_id = 0
        # batching robusto: paginiamo per id per evitare salti da offset dopo write/commit
        while True:
            leads = Lead.search(
                [("id", ">", last_id), ("partner_id", "!=", False)],
                order="id",
                limit=batch_size,
            )
            if not leads:
                break

            for lead in leads:
                total_seen += 1
                partner = lead.partner_id.commercial_partner_id or lead.partner_id
                city_src = (partner.city or "").strip()
                city_dst = (lead.city or "").strip()

                # aggiorna solo se la sorgente esiste e differisce
                if city_src and city_src != city_dst:
                    if not dry_run:
                        # disabilito tracking per non generare chatter rumoroso
                        lead.with_context(tracking_disable=True).write({"city": city_src})
                    total_updated += 1
                else:
                    total_skipped += 1

            last_id = leads[-1].id
            # commit in cron per rilasciare lock su lotti molto grandi
            if not dry_run:
                env.cr.commit()

        _logger.info(
            "CRM City Sync: seen=%s, updated=%s, skipped=%s, dry_run=%s",
            total_seen, total_updated, total_skipped, dry_run
        )
        return {
            "seen": total_seen,
            "updated": total_updated,
            "skipped": total_skipped,
            "dry_run": dry_run,
        }
