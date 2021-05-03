# -*- coding: utf-8 -*-
{
    'name': "Product Category on Inv. Report",
    'summary': """
       This module will make new field on Inventory Report
       """,

    'description': """
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'views/stock_quant_views.xml',
        'views/stock_move_line_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
