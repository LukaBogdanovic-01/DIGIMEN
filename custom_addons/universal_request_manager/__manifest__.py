{
    'name': 'DIGIMEN',
    'version': '18.0.1.0.0',
    'summary': 'Digitalni menadžer',
    'license': 'LGPL-3',
    'depends': ['project', 'base', 'mail', 'hr', 'auth_signup', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/demo_users.xml',
        'views/universal_request_views.xml',
        'views/request_type_views.xml',
        'views/code_book_data.xml',
        'views/code_book_proces.xml',
        'views/universal_request_menus.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'universal_request_manager/static/src/css/universal_request.css',
        ],
        'web.assets_common': [
            'universal_request_manager/static/src/css/universal_request.css',
        ]
    },
    'installable': True,
    'application': True,
}
