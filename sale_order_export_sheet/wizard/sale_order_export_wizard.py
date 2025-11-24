# -*- coding: utf-8 -*-
"""Wizard to export sale orders to an Excel spreadsheet."""


from collections import OrderedDict
import io, base64, csv
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date



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
        today = date.today()
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
            partner_rit=partner
            l10n_it_transport_method_details=""
            scheduled_date=""
            for pick in order.picking_ids:
                if pick.state !='cancel':
                    partner_rit = pick.partner_id
                    l10n_it_transport_method_details=pick.l10n_it_transport_method_details
                    scheduled_date=pick.scheduled_date.date()

            for line in order.order_line:
                rows.append(
                    {
                        "CHANNEL": "STAMPAMASSIVA",
                        "CODICE_CONTRATTO": "SFA-01038898",
                        "CENTRO_COSTO": "CDC-00064891",
                        "CODICE_IDENTIFICATIVO_CLIENTE": "88645324",
                        "PRODOTTO": "APT000902",
                        "COGNOME_RAGSOC_MITTENTE": partner.display_name or "",
                        "CONTATTO_MITTENTE_REF": "",
                        "EMAIL_MITTENTE": order.company_id.email or "",
                        "NUMERO_TELEFONO_MITTENTE": order.company_id.phone or "",
                        "NUMERO_CELLULARE_MITTENTE": order.company_id.mobile or "",
                        "NUMERO_TELEFONO_MITTENTE": order.company_id.phone or "",
                        "VIA_MITTENTE": order.company_id.street or "",
                        "NUMERO_CIVICO_MITTENTE": "snc",
                        "CAP_MITTENTE": order.company_id.zip or "",
                        "LOCALITA_MITTENTE": order.company_id.city or "",
                        "PROVINCIA_MITTENTE": order.company_id.state_id.code or "",
                        "CODICE_NAZIONE_MITTENTE": order.company_id.country_id.code or "",
                        "NAZIONE_MITTENTE": order.company_id.country_id.name or "",
                        "NOTE1_MITTENTE": "",
                        "COGNOME_RAGSOC_DESTINATARIO": partner.display_name or "",
                        "CONTATTO_DESTINATARIO_REF": partner.ref or "",
                        "EMAIL_DESTINATARIO": partner.email or "",
                        "NUMERO_TELEFONO_DESTINATARIO": partner.phone or "",
                        "NUMERO_CELLULARE_DESTINATARIO": partner.mobile or "",
                        "VIA_DESTINATARIO": partner.street or "",
                        "NUMERO_CIVICO_DESTINATARIO": "snc",
                        "VIA_DESTINATARIO": partner.street or "",
                        "CAP_DESTINATARIO": partner.zip or "",
                        "LOCALITA_DESTINATARIO": partner.city or "",
                        "PROVINCIA_DESTINATARIO": state_code or "IT",
                        "CODICE_NAZIONE_DESTINATARIO": partner.country_id.code or "IT",
                        "NAZIONE_DESTINATARIO": partner.country_id.name or "IT",
                        "NOTE1_DESTINATARIO": order.note or "",
                        "COGNOME_RAGSOC_RITIRO": partner_rit.country_id.code or "IT",
                        "CONTATTO_RITIRO_REF": partner_rit.ref or "",
                        "EMAIL_RITIRO": partner_rit.email or "",
                        "NUMERO_TELEFONO_RITIRO": partner_rit.phone or "",
                        "NUMERO_CELLULARE_RITIRO": partner_rit.mobile or "",
                        "VIA_RITIRO": partner_rit.street or "",
                        "NUMERO_CIVICO_RITIRO": "snc",
                        "VIA_RITIRO": partner_rit.street or "",
                        "CAP_RITIRO": partner_rit.zip or "",
                        "LOCALITA_RITIRO": partner.city or "",
                        "PROVINCIA_RITIRO": state_code or "IT",
                        "CODICE_NAZIONE_RITIRO": partner_rit.country_id.code or "IT",
                        "NAZIONE_RITIRO": partner_rit.country_id.name or "IT",
                        "NOTE1_RITIRO": l10n_it_transport_method_details or "",
                        "ID_LDV": "",
                        "NUMERO_RIFERIMENTO_SPEDIZIONE": order.origin or "",
                        "IDENTIFICATIVO_COLLO": order.origin or "",
                        "NUMERO_COLLI": 1,
                        "PESO_COLLO": 1000,
                        "LARGHEZZA": "",
                        "ALTEZZA": "",
                        "PROFONDITA": "",
                        "RITIRO_VOLUMETRICO": "",
                        "DATA_SPEDIZIONE_RITIRO": order.commitment_date.date() if order.commitment_date else scheduled_date if order.picking_ids else today,
                        "COL01": "",
                        "COL02": "",
                        "COL03": "",
                        "COL04": "",
                        "COL05": "",
                        "COL06": "",
                        "COL07": "",
                        "COL08": "",
                        "COL10": "",
                        "COL11": "",
                        "COL12": "",
                        "COL13": "",
                        "COL14": "",
                        "COL15": "",
                        "COL16": "",
                        "COL17": "",
                        "COL18": "",
                        "COL19": "",
                        "COL20": "",
                        "COL21": "",
                        "COL22": "",


                        #"description": line.product_id.display_name
                        #or line.name
                        #or "",
                        #"colli": 1,
                        #"peso": 1,
                        #"contra": "",
                        #"order_name": order.origin or order.name or "",
                        #"partner_mobile": partner.mobile.replace('+39','') if partner.mobile else "" or "",
                        #"partner_email": partner.email or "",
                    }
                )
                break
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
        partners.read(["display_name", "zip", "city", "state_id", "mobile", "email"])
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
            worksheet.write(0, col_index, (title), header_format)
            worksheet.set_column(col_index, col_index, width)

        for row_index, row in enumerate(rows, start=1):
            for col_index, (key, _) in enumerate(self.COLUMN_SPECS.items()):
                value = row.get(key)
                if key in {"colli", "peso"}:
                    worksheet.write(row_index, col_index, value or 0.0, number_format)
                else:
                    worksheet.write(row_index, col_index, value or "", text_format)

        workbook.close()

    def action_export_csv(self):
        """Genera il file CSV e ritorna il wizard in stato di download."""
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

        # Prefetch come nell'XLSX
        orders.read([
            "name",
            "partner_id",
            "order_line",
            "picking_ids",
        ])
        partners = orders.mapped("partner_id")
        partners.read(["display_name", "zip", "city", "state_id", "mobile", "email"])
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

        # Costruzione CSV
        sio = io.StringIO(newline="")
        self._build_csv(sio, rows)

        # Aggiungo BOM UTF-8 per compatibilità Excel
        export_content = ("\ufeff" + sio.getvalue()).encode("utf-8")
        if not export_content:
            raise UserError(_("Unable to generate the export file. Please try again."))

        filename = "sale_orders_%s.csv" % fields.Date.context_today(self)
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

    def _get_csv_delimiter(self):
        """Ritorna il delimitatore CSV leggendo da ir.config_parameter con normalizzazione."""
        param_val = self.env["ir.config_parameter"].sudo().get_param(
            "sale_order_export_sheet.csv_delimiter", default=";"
        )
        d = (param_val or ";").strip().lower()
        if d in {"\\t", "tab", "tabulatore"}:
            return "\t"
        if d in {"comma", "virgola"}:
            return ","
        if d in {"semicolon", "puntoevirgola"}:
            return ";"
        return d if d == "\t" or len(d) == 1 else ";"

    def _sanitize_csv_value(self, val):
        """Uniforma i valori per il CSV (header incluse): niente a-capo, niente recordset."""
        if val is None:
            return ""
        if hasattr(val, "display_name"):
            val = val.display_name or ""
        s = str(val)
        # Evita “colonne spostate” in Excel dovute a newline
        s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ")
        return s

    def _build_csv(self, output, rows, delimiter=None):
        """Crea il CSV su ``output`` usando lo stesso criterio per header e righe."""
        delimiter = delimiter or self._get_csv_delimiter()

        writer = csv.writer(
            output,
            delimiter=delimiter,
            quotechar='"',
            quoting=csv.QUOTE_ALL,  # <-- identico per header e righe
            lineterminator="\n",
            escapechar="\\",
        )

        # HEADER: stessi passaggi delle righe
        headers = []
        if rows:
            for row in rows:
                for key, value in row.items():
                    print(key, value)
                    headers.append(self._sanitize_csv_value(key))  # <-- sanitizzazione identica
            writer.writerow(headers)  # <-- passa dal writer (quindi stesso delimiter/quoting)

            # RIGHE: stesso identico trattamento
            for row in rows:
                csv_row = []
                for key, _spec in row.items():
                    csv_row.append(self._sanitize_csv_value(row.get(key)))
                writer.writerow(csv_row)
