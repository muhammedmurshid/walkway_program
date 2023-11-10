{
    'name': "Walkway Program",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'mail', 'logic_base'],
    'data': [
        'security/ir.model.access.csv',
        'security/walkway_rules.xml',
        'views/walkway_views.xml',
        'data/activity.xml',

    ],

    'demo': [],
    'summary': "logic_walkway_program",
    'description': "logic_walkway_program",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': False
}
