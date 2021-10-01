# -*- encoding: utf-8 -*-

{
    'name': 'Purchase Inventory Barcode Extended',
    'version': '13.0.0.0.0',
    'summary': 'Purchase Inventory Barcode Extended',
    'description': """
""",
    'category': '',
    'author': "",
    'depends': ['purchase','product_expiry','purchase_stock'],
    'data': [
        'views/purchase_view.xml', 
        'views/inventory_view.xml',
        'views/stock_product_lot_view.xml',
        'views/stock_move_line_view.xml', 
        'views/stock_picking_kanban_view.xml',
    ],
    'installable': True,
}
