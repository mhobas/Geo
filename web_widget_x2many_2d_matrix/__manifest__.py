# Copyright 2015 Holger Brunn <hbrunn@therp.nl>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2018 Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "2D matrix for x2many fields test",
    "version": "14.0.1.0.1",
    "author": (
        "Therp BV, "
        "Tecnativa, "
        "Camptocamp, "
        "CorporateHub, "
        "Odoo Community Association (OCA)"
    ),
    "website": "https://github.com/OCA/web",
    "license": "AGPL-3",
    "category": "Hidden/Dependency",
    "summary": "Show list fields as a matrix",
    "depends": ["web"],
    # "data": ["views/assets.xml"],
    "installable": True,
    'assets': {
        'web.assets_backend': [
            'web_widget_x2many_2d_matrix/static/src/js/*',
            'web_widget_x2many_2d_matrix/static/src/scss/web_widget_x2many_2d_matrix.scss',
        ],

    },
}
