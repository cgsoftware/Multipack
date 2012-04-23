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


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _order = 'sequence, id asc'
    
    def button_confirm(self, cr, uid, ids, context=None):
        
        for riga in self.browse(cr,uid,ids):
            order_id = riga.order_id.id
            if riga.product_id.righe_multipack:
                # c'è un articolo che va esploso prima di fare il mov di mag se possibile
            # PRIMA SCRIVE LA RIGA DELLO STESSO ARTICOLO SENZA PREZZO
                dati_art = self.product_id_change(cr, uid, ids, False, riga.product_id.id, riga.product_uom_qty,False, riga.product_uom_qty, False, '', riga.order_id.partner_id.id,False, True, riga.order_id.date_order,False,False, False)
                row = dati_art.get('value',False)
                #import pdb;pdb.set_trace()
                if row:
                        row['order_id'] = order_id
                        row['product_id'] = riga.product_id.id
                        row['product_uom_qty'] = riga.product_uom_qty
                        #import pdb;pdb.set_trace()
                        id_row = self.create(cr,uid,row)
                
                
                for riga_multi in riga.product_id.righe_multipack:
                    if riga.order_id.pricelist_id.name[:1] == "1": # listino al pubblico 
                      dati_art = self.product_id_change(cr, uid, ids, riga_multi.price_version_id_pub.pricelist_id.id, riga_multi.product_id.id, riga.product_uom_qty,False, riga.product_uom_qty, False, '', riga.order_id.partner_id.id,False, True, riga.order_id.date_order,False,False, False)
                      #              "product_id_change(parent.pricelist_id,product_id,product_uom_qty,product_uom,product_uos_qty,product_uos,name,parent.partner_id, 'lang' in context and context['lang'], True, parent.date_order, product_packaging, parent.fiscal_position, False)"
                      # aggiunge altri dati e fa la create della riga
                    else:
                        dati_art = self.product_id_change(cr, uid, ids, riga_multi.price_version_id_riv.pricelist_id.id, riga_multi.product_id.id, riga.product_uom_qty,False, riga.product_uom_qty, False, '', riga.order_id.partner_id.id,False, True, riga.order_id.date_order,False,False, False)
                    row = dati_art.get('value',False)
                    if row:
                        row['order_id'] = order_id
                        row['product_id'] = riga_multi.product_id.id
                        row['product_uom_qty'] = riga.product_uom_qty
                        #import pdb;pdb.set_trace()
                        id_row = self.create(cr,uid,row)
                
                ok = self.unlink(cr,uid,[riga.id]) # ha aggiunto le righe in multi pack quindi cancella la riga madre    
        # ricalcola gli ids
        if order_id:
            
            ids = self.search(cr,uid,[('order_id','=',order_id)]) 
            
        return self.write(cr, uid, ids, {'state': 'confirmed'})


sale_order_line()

class FiscalDocRighe(osv.osv):
   _inherit = "fiscaldoc.righe"



   _columns = {
               'flag_multi_creato':fields.boolean('Flag Multipack Già Esploso'),
               }
   
FiscalDocRighe()
class FiscalDocHeader(osv.osv):
   _inherit = "fiscaldoc.header"
   

   def write(self, cr, uid, ids, vals, context=None):
        res = super(FiscalDocHeader, self).write(cr, uid, ids, vals, context=context)
        if res:
            riga_obj = self.pool.get('fiscaldoc.righe')
            for testa in self.pool.get('fiscaldoc.header').browse(cr,uid,ids,context=context):
                for riga in testa.righe_articoli:
                    if riga.product_id.righe_multipack and not riga.flag_multi_creato:
                        dati_art = riga_obj.onchange_articolo(cr, uid, ids, riga.product_id.id, testa.listino_id.id, riga.product_uom_qty, testa.partner_id.id, testa.data_documento, riga.product_uom.id)
                        row = dati_art.get('value',False)
                        #import pdb;pdb.set_trace()
                        if row:
                            row['name'] = testa.id
                            row['product_id'] = riga.product_id.id
                            row['product_uom_qty'] = riga.product_uom_qty   
                            row['product_prezzo_unitario'] = 0.0
                            row['prezzo_netto']= 0.0  
                            row['flag_multi_creato'] = True               
                            #import pdb;pdb.set_trace()
                            id_row = riga_obj.create(cr,uid,row)                       
                            for riga_multi in riga.product_id.righe_multipack:
                                dati_art = riga_obj.onchange_articolo(cr, uid, ids, riga_multi.product_id.id, riga_multi.price_version_id_riv.pricelist_id.id, riga.product_uom_qty, testa.partner_id.id, testa.data_documento, riga.product_uom.id)
                                row = dati_art.get('value',False)
                                #import pdb;pdb.set_trace()
                                if row:
                                    row['name'] = testa.id
                                    row['product_id'] = riga_multi.product_id.id
                                    row['product_uom_qty'] = riga.product_uom_qty                            
                                    #import pdb;pdb.set_trace()
                                    id_row = riga_obj.create(cr,uid,row)   
                        ok = riga_obj.unlink(cr,uid,[riga.id]) # ha aggiunto le righe in multi pack quindi cancella la riga madre                    
        return res
   
   
   def create(self, cr, uid, vals, context=None):
        # prima scrive i record così come sono poi si preoccupa di ricalcolare  le tasse e i campi calcolati
        #import pdb;pdb.set_trace()
        
        res = super(FiscalDocHeader, self).create(cr, uid, vals, context=context)
        if res:
            ids = res
            riga_obj = self.pool.get('fiscaldoc.righe')
            for testa in self.pool.get('fiscaldoc.header').browse(cr,uid,[ids],context=context):
                for riga in testa.righe_articoli:
                    if riga.product_id.righe_multipack and not riga.flag_multi_creato:
                        dati_art = riga_obj.onchange_articolo(cr, uid, ids, riga.product_id.id, testa.listino_id.id, riga.product_uom_qty, testa.partner_id.id, testa.data_documento, riga.product_uom.id)
                        row = dati_art.get('value',False)
                        #import pdb;pdb.set_trace()
                        if row:
                            row['name'] = testa.id
                            row['product_id'] = riga.product_id.id
                            row['product_uom_qty'] = riga.product_uom_qty   
                            row['product_prezzo_unitario'] = 0.0
                            row['prezzo_netto']= 0.0  
                            row['flag_multi_creato'] = True               
                            #import pdb;pdb.set_trace()
                            id_row = riga_obj.create(cr,uid,row)                       
                            for riga_multi in riga.product_id.righe_multipack:
                                dati_art = riga_obj.onchange_articolo(cr, uid, ids, riga_multi.product_id.id, riga_multi.price_version_id_riv.pricelist_id.id, riga.product_uom_qty, testa.partner_id.id, testa.data_documento, riga.product_uom.id)
                                row = dati_art.get('value',False)
                                #import pdb;pdb.set_trace()
                                if row:
                                    row['name'] = testa.id
                                    row['product_id'] = riga_multi.product_id.id
                                    row['product_uom_qty'] = riga.product_uom_qty                            
                                    #import pdb;pdb.set_trace()
                                    id_row = riga_obj.create(cr,uid,row)   
                        ok = riga_obj.unlink(cr,uid,[riga.id]) # ha aggiunto le righe in multi pack quindi cancella la riga madre                    
                                
        return res

          


FiscalDocHeader()