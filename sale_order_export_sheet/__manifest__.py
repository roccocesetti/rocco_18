# -*- coding: utf-8 -*-
"""Manifest for the sale_order_export_sheet module."""

{
    "name": "Sale Order Export Sheet",
    "summary": "Export sale orders to a spreadsheet template.",
    "description": """
This module provides the technical manifest definition that allows Odoo to
load the sale order export sheet features. The functional components will be
implemented in subsequent updates.
""",
    "version": "18.0.1.0.0",
    "author": "Rocco",
    "website": "https://www.example.com",
    "license": "OEEL-1",
    "category": "Sales/Reporting",
    "depends": [
        "sale_management",
        "spreadsheet_edition",
    ],
    "data": [],
    "assets": {},
    "installable": True,
    "application": False,
}
