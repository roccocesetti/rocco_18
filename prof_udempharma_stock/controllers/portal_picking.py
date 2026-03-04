# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, content_disposition
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class PortalPicking(CustomerPortal):

    def _picking_domain(self):
        partner = request.env.user.partner_id.commercial_partner_id
        return [("partner_id.commercial_partner_id", "=", partner.id)]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "picking_count" in counters:
            values["picking_count"] = request.env["stock.picking"].sudo().search_count(self._picking_domain())
        return values

    @http.route(["/my/pickings", "/my/pickings/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_pickings(self, page=1, sortby="date", **kw):
        Picking = request.env["stock.picking"].sudo()
        domain = self._picking_domain()

        sortings = {
            "date": {"label": "Scheduled Date", "order": "scheduled_date desc, id desc"},
            "name": {"label": "Reference", "order": "name desc, id desc"},
            "state": {"label": "Status", "order": "state asc, id desc"},
        }
        order = sortings.get(sortby, sortings["date"])["order"]

        total = Picking.search_count(domain)
        pager = portal_pager(url="/my/pickings", url_args={"sortby": sortby}, total=total, page=page, step=20)
        pickings = Picking.search(domain, order=order, limit=20, offset=pager["offset"])
        return request.render("prof_udempharma_stock.portal_my_pickings", {
            "page_name": "picking",
            "pickings": pickings,
            "pager": pager,
            "sortings": sortings,
            "sortby": sortby,
        })
    @http.route(["/my/pickings/<int:picking_id>"], type="http", auth="user", website=True)
    def portal_picking_page(self, picking_id, access_token=None, report_type=None, download=False, **kw):
        picking = self._document_check_access("stock.picking", picking_id, access_token=access_token)

        products = (picking.move_ids_without_package.mapped("product_id") or picking.move_line_ids.mapped(
            "product_id")).sudo()
        products = products.with_company(picking.company_id)

        availability = {
            p.id: {"qty_available": p.qty_available, "virtual_available": p.virtual_available,
                   "uom_name": p.uom_id.name}
            for p in products
        }

        if report_type == "pdf":
            report = request.env.ref("stock.action_report_delivery", raise_if_not_found=False) or request.env.ref("stock.action_report_picking", raise_if_not_found=False)
            if not report:
                return request.not_found()
            pdf_content, _ = report.sudo()._render_qweb_pdf([picking.id])
            filename = f"{picking.name or 'Picking'}.pdf"
            headers = [("Content-Type", "application/pdf"), ("Content-Length", str(len(pdf_content)))]
            if download:
                headers.append(("Content-Disposition", content_disposition(filename)))
            return request.make_response(pdf_content, headers=headers)

        return request.render("prof_udempharma_stock.portal_picking_page",
                              {"page_name": "picking",
                               "picking": picking,
                               "availability": availability
                               })
