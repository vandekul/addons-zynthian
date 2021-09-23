#******************************************************************************
# ZYNTHIAN MRP REPORT ODOO
# 
# Copyright (C) 2020 Susanna Fort <susannafm@gmail.com>
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
    'name': "Zynthian MRP Reports",

    'summary': """This module creates cost report for BoM Structure Odoo v9.0""",
    'author': "Vandekul",
    'website': "https://github.com/vandekul",
    'category': 'Website',
    'version': '9.0',
    'license': 'GPL-3',
    'application': True,
    'depends': ['base','mrp'],
    'data': [
        'views/cost_mrp_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'description': 'static/description/index.html',
    'images': ['static/description/icon.png'],
}