# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_round


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    time_cycle_second = fields.Float(
        string="Cycle Time (Seconds)",
        compute="_compute_time_cycle_second",
        store=True,
    )

    @api.depends('time_cycle')
    def _compute_time_cycle_second(self):
        for rec in self:
            rec.time_cycle_second = float(rec.time_cycle or 0.0) * 60.0

