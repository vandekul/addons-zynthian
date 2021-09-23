#******************************************************************************
# PAYMENT STRIPE FOR ODOO
# 
# Copyright (C) 2021 Susanna Fort <susannafm@gmail.com>
#
#******************************************************************************
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the LICENSE.txt file.
# 
#******************************************************************************

{
<<<<<<< HEAD
    'name': "Gateway Stripe",

    'summary': """This module integrates Stripe with Odoo v9.0""",
    'author': "Vandekul",
    'website': "https://github.com/vandekul",
    'category': 'Website',
    'version': '9.0',
    'license': 'GPL-3',
    'price':'100',
    'application': True,
    'depends': ['base', 'payment'],
=======
    'name': 'Paypal as a Friend Payment Acquirer',
    'author':'mumaker',
    'category': 'Accounting',
    'summary': 'Payment Acquirer: Paypal as a Friend Implementation',
    'version': '1.0',
    'description': """Paypal as a Friend Payment Acquirer
    201910
    It includes changing status in transaction payment when quotation is confirm/cancell/draft manually.
    This changing will afect wire transfer and paypal as a friend payment acquirer and they need to select
    'At payment with acquirer confirmation' option in Order Confirmation field in Payment Acquirer Configuration.

    """,
    'website': 'https://github.com/vandekul',
    'depends': ['payment', 'sale'],
>>>>>>> 30020cc9ff6ca4f67e679a3a1a53f72cd2d3edd5
    'data': [
        'views/payment_stripe_templates.xml',
        'views/stripe_configuration_view.xml',
        'data/payment_acquirer_data.xml'
    ],
    'installable': True,
    'auto_install': False,
    'description': 'static/description/index.html',
    'images': ['static/description/icon.png'],
}