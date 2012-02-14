# -*- encoding: utf-8 -*-

import netsvc
import pooler, tools
import math
from tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import decimal_precision as dp
import time


from osv import fields, osv

class product_multipack(osv.osv):
    _name = 'product.multipack'
    _description = 'Kit confezione a Vendita Unica'
    _columns = {
                'name' : fields.many2one('product.product', 'Articolo Madre', required=True, ondelete='cascade', select=True, readonly=True),
                'product_id' : fields.many2one('product.product', 'Componente', required=True, ondelete='cascade', select=True),
                'price_version_id_pub': fields.many2one('product.pricelist.version', 'Listino Pubblico', required=True, select=True),
                'price_version_id_riv': fields.many2one('product.pricelist.version', 'Listino Rivenditore', required=True, select=True),
                }


product_multipack()

class product_product(osv.osv):
    _inherit = 'product.product'

    

    
    _columns = {
                'righe_multipack': fields.one2many('product.multipack', 'name', 'Righe Articoli in MultiPack', required=False),
               }

product_product()


