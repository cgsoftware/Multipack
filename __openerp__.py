# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Gestione Aricoli in Kit alla Vendita',
    'version': '1.0',
    'category': 'Generic Modules/Base',
    'description': """
     Permette di Gestire un elenco di articoli in kit alla Vendita
    """,
    'author': 'C & G Software',
    "depends" : ['base', 'sale','product','ItalianFiscalDocument'],
    "update_xml" : [ 'product_view.xml', 
                   ],
                    
    'website': 'http://www.cgsoftware.it',
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
