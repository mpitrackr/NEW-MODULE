# -*- encoding: utf-8 -*-
{
    'name': "odoo Barcode customisations",  # Name first, others listed in alphabetical order
    'application': False,
    'auto_install': False,
    'category': "Extra Tools",  # Odoo Marketplace category
    'data': [  # Files are processed in the order of listing
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/stock.xml',
    ],
    'demo': [],
    'depends': [  # Include only direct dependencies
        'sale', 'purchase', 'stock', 'inventory_barcode', 'product_expiry'
    ],
    'description': "some new fields and barcode changes",
    'installable': True,
    'summary': "Odoo Barcode Related Customisations",
    'version': "1.0.1",
}
