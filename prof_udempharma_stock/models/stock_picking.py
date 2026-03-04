# -*- coding: utf-8 -*-
from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "portal.mixin"]

    def _get_report_base_filename(self):
        self.ensure_one()
        return self.name or "Picking"

    def _get_portal_url(self, suffix=None, report_type=None, download=False, query_string=None, anchor=None):
        """Force portal URL to match our controller routes."""
        self.ensure_one()
        url = f"/my/pickings/{self.id}"
        # lascia che portal.mixin aggiunga querystring standard (report_type/download/token) se serve
        return super()._get_portal_url(
            suffix=url,
            report_type=report_type,
            download=download,
            query_string=query_string,
            anchor=anchor,
        )