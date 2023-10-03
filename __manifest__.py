# -*- coding: utf-8 -*-
{
    'name': "smart_search",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/kramer.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'smart_search/static/src/customer_kanban_view/customer_kanban_view.js',
            'smart_search/static/src/customer_kanban_view/customer_kanban_view.scss',
            'smart_search/static/src/customer_kanban_view/customer_kanban_view.xml',
            'smart_search/static/src/smart_search/smart_search.js',
            'smart_search/static/src/smart_search/smart_search.scss',
            'smart_search/static/src/smart_search/smart_search.xml',
            # 'smart_search/static/src/**/*',
            # 'smart_search/static/src/**/*',
            # 'smart_search/static/src/**/*',
        ],

        'web.assets_frontend': [
            # Kramer_v1
            'smart_search/static/src/kramer_v1/000.js',


            'smart_search/static/src/s_smart_searchbar/000.js',
            'smart_search/static/src/s_smart_searchbar/options.js',
            'smart_search/static/src/s_smart_searchbar/000.xml',
        ],

    },

    "application": True,
}
