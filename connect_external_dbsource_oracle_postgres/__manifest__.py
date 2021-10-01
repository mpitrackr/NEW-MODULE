# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Postgresql and Oracle Database Synchronization",
    "author": "Warlock Technologies Pvt Ltd.",
    "description": """Using this extension user can connect and access Oracle Database & Postgresql Databse
                        Also fetch the data using queries and append to existing database.
    """,
    "summary": """External Database Synchronization""",
    "version": "7.0",
    "price": 30.00,
    "currency": "USD",
    "license": "OPL-1",
    "support": "info@warlocktechnologies.com",
    "website": "http://warlocktechnologies.com",
    "category": "Base",
    "depends": ["base", "purchase", "stock", "stock_account", "product_expiry", "sale_management"],
    "images": ["images/screen_image.png"],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "wizard/message_view.xml",
        "views/synchronize_view.xml",
        "views/sychronize_log_view.xml",
        "views/menu_parameters.xml",
        "views/res_partner_view.xml",
        "views/stock_picking_view.xml",
        "views/purchase_order_view.xml",
        "views/product_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
