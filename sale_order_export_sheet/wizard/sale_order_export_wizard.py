# -*- coding: utf-8 -*-
"""Wizard to export sale orders to an Excel spreadsheet."""

import base64
from collections import OrderedDict
import io

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderExportWizard(models.TransientModel):
    """Wizard used to export selected sale orders to XLSX."""

    _name = "sale.order.export.wizard"
    _description = "Sale Order Export Wizard"

    export_file = fields.Binary(readonly=True)
    export_filename = fields.Char(readonly=True)
    state = fields.Selection(
        selection=[("choose", "Choose"), ("ready", "Ready")],
        string="State",
        default="choose",
        readonly=True,
    )

    COLUMN_SPECS = OrderedDict(
        [
            ("partner_name", ("NOME", 30)),
            ("partner_cap", ("CAP", 12)),
            ("partner_city", ("CITTA", 20)),
            ("partner_state", ("PROVINCIA", 12)),
            ("description", ("DESCRIZIONE", 40)),
            ("colli", ("COLLI", 12)),
            ("peso", ("PESO", 12)),
            ("contra", ("CONTRA", 12)),
            ("order_name", ("NUMERO ORDINE", 20)),
            ("partner_mobile", ("CELLULARE", 20)),
            ("partner_email", ("EMAIL", 30)),
        ]
    )

    @api.model
    def _prepare_lines(self, orders):
        """Build the data rows for the export.

        :param orders: recordset of ``sale.order``
        :return: list of dictionaries containing the row data
        """
        rows = []
        for order in orders:
            partner = order.partner_id
            state_code = partner.state_id.code if partner.state_id else None
            colli = sum(
                p.l10n_it_parcels or 1 for p in order.picking_ids if p.state != "cancel"
            )
            peso = sum(
                p.shipping_weight or 1.0 for p in order.picking_ids if p.state != "cancel"
            )
            for line in order.order_line:
                rows.append(
                    {
                        "partner_name": partner.display_name or "",
                        "partner_cap": partner.cap or "",
                        "partner_city": partner.city or "",
                        "partner_state": state_code or "IT",
                        "description": line.product_id.display_name
                        or line.name
                        or "",
                        "colli": colli,
                        "peso": peso,
                        "contra": "",
                        "order_name": order.name or "",
                        "partner_mobile": partner.mobile or "",
                        "partner_email": partner.email or "",
                    }
                )
        return rows

    def action_export(self):
        """Generate the Excel file and return the wizard in download state."""
        self.ensure_one()

        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids") or []
        if active_model != "sale.order" or not active_ids:
            raise UserError(
                _("Please select at least one sale order to export from the list view.")
            )

        orders = self.env["sale.order"].browse(active_ids).exists()
        if not orders:
            raise UserError(_("The selected sale orders are no longer available."))

        # Prefetch related records to minimize queries when iterating.
        orders.read([
            "name",
            "partner_id",
            "order_line",
            "picking_ids",
        ])
        partners = orders.mapped("partner_id")
        partners.read(["display_name", "cap", "city", "state_id", "mobile", "email"])
        partners.mapped("state_id").read(["code"])
        order_lines = orders.mapped("order_line")
        order_lines.read([
            "product_id",
            "name",
            "product_uom_qty",
            "qty_delivered",
        ])
        order_lines.mapped("product_id").read(["display_name"])
        pickings = orders.mapped("picking_ids")
        if pickings:
            pickings.read(["state", "l10n_it_parcels", "shipping_weight"])

        rows = self._prepare_lines(orders)
        if not rows:
            raise UserError(_("The selected sale orders do not contain any order lines."))

        output = io.BytesIO()
        self._build_workbook(output, rows)

        export_content = output.getvalue()
        if not export_content:
            raise UserError(_("Unable to generate the export file. Please try again."))

        filename = "sale_orders_%s.xlsx" % fields.Date.context_today(self)
        self.write(
            {
                "export_file": base64.b64encode(export_content),
                "export_filename": filename,
                "state": "ready",
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    def _build_workbook(self, output, rows):
        """Create the XLSX workbook in ``output`` using the provided rows."""
        try:
            from xlsxwriter import Workbook
        except ImportError as exc:  # pragma: no cover - handled at runtime
            raise UserError(
                _(
                    "Missing Python dependency xlsxwriter. Please install it to export Excel files."
                )
            ) from exc

        workbook = Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Sale Orders")

        header_format = workbook.add_format(
            {"bold": True, "bg_color": "#1F4E78", "font_color": "#FFFFFF", "align": "center"}
        )
        text_format = workbook.add_format({"align": "left"})
        number_format = workbook.add_format({"num_format": "0.00", "align": "right"})

        # Write headers and define column widths as per COLUMN_SPECS
        for col_index, (key, (title, width)) in enumerate(self.COLUMN_SPECS.items()):
            worksheet.write(0, col_index, _(title), header_format)
            worksheet.set_column(col_index, col_index, width)

        for row_index, row in enumerate(rows, start=1):
            for col_index, (key, _) in enumerate(self.COLUMN_SPECS.items()):
                value = row.get(key)
                if key in {"colli", "peso"}:
                    worksheet.write(row_index, col_index, value or 0.0, number_format)
                else:
                    worksheet.write(row_index, col_index, value or "", text_format)

        workbook.close()

