{
    'name': 'DIGIMEN',
    'version': '16.0.1.0.0',
    'summary': 'Digitalni menadžer',
    'depends': ['project', 'base', 'mail', 'hr', 'auth_signup', 'web'],
    'data': [
        'security/security.xml',
        'security/demo_users.xml',
        'security/ir.model.access.csv',
        'views/universal_request_views.xml',
        'views/request_type_views.xml',
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
