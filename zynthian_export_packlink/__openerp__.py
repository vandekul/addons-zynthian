{
    'name': "Sale package label",
    'version': '1.0',
    'category' : 'Website',
    'website' : 'http://www.zynthian.org',
    'summary': 'Package Label to paste in the package. Included FROM and TO address',
    'description': """
        Modification of:
        Create a new report that contain package report.  
        It creates two columns: first one with shipping address, second one with Company address.
        Can be access from Print menu, and allow to create one label or all that you select.
        """,
    'author': 'mumaker',
    'depends': ['website'],
    'data': [
        'views/sale_package_label_report.xml',
        'views/sale_package_label_template.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
