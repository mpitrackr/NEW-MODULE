# -*- encoding: utf-8 -*-

{
    'name': 'Purchase Inventory Import Export',
    'version': '13.0.0.0.0',
    'summary': 'Purchase Inventory Import Export',
    'description': """
            This module is used to generate the purchase order from the csv file. and generate the csv file from the receipt
""",
    'category': '',
    'author': "",
    'depends': ['purchase','product_expiry','purchase_stock','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/file_process_log.xml',
        'views/ftp_server.xml',
        'views/stock_picking.xml',
        'data/ir_cron_views.xml',
    ],
    'installable': True,
}
