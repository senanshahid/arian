# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    @api.model
    def create(self, values):
        t_uid = self.env.uid
        if self.user_has_groups('de_product_enhancement.group_stock_quant_restrict'):
            raise exceptions.ValidationError('You are not allowed to create Stock')    
        res = super(StockQuant, self).create(values)
        return res
    
    
#     @api.multi
    def write(self, values):
        t_uid = self.env.uid
        if self.user_has_groups('de_product_enhancement.group_stock_quant_restrict'):
            raise exceptions.ValidationError('You are not allowed to update Stock')
           
        res = super(StockQuant, self).write(values)
        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def action_done(self):
        res = super(StockPicking, self).action_done()
        if self.state != 'done':
            self.update({
                'state': 'done'
            })
      
        return res



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    
    
    bill_amount = fields.Monetary(string="Amount Billed", compute='_compute_bill_amount')
    remaining_bill_amount = fields.Monetary(string="Remaining Amount to bill", compute='_compute_bill_amount')

    
    def _compute_bill_amount(self):
        sum_invoice_amount = 0
        order_bill = self.env['account.move'].search([('invoice_origin','ilike',self.name)])
        for invoice in order_bill:
            sum_invoice_amount = sum_invoice_amount + invoice.amount_total
        self.bill_amount = sum_invoice_amount
        self.remaining_bill_amount = self.amount_total - sum_invoice_amount
    
    
    
    
    
    def button_done(self):
        res = super(PurchaseOrder, self).button_done()
        picking = self.env['stock.picking'].search([('origin','=',self.name)])
        for pick in picking:
            if pick.state != 'done':
                pick.update({
                    'state': 'cancel'
                })
      
        return res     
    
    receipt_date = fields.Date(string='Receipt Date')
    payment_term_date =  fields.Date(string='Expected Payment Date')
    is_received = fields.Boolean(string="Is Received")
    
    @api.onchange('receipt_date','payment_term_id')
    def _check_change(self):
        current_date = date.today()
        if self.receipt_date:
            date_1= (datetime.strptime(str(self.receipt_date), '%Y-%m-%d')+relativedelta(days =+ self.payment_term_id.line_ids.days))
            self.payment_term_date =date_1
        else:    
            date_2= (datetime.strptime(str(current_date), '%Y-%m-%d')+relativedelta(days =+ self.payment_term_id.line_ids.days))
            self.payment_term_date =date_2
    
    @api.onchange('receipt_date')
    def onchange_receipt_date(self):
        if self.receipt_date:
            self.date_planned = self.receipt_date


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    purchase_id = fields.Char(string='Customer PO Number', required=True)

    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
#     @api.model
#     def create(self, values):
#         res = super(ProductProduct, self).create(values)
#         pg1 = self.env['procurement.group'].create({})
#         reordring_rule = self.env['stock.warehouse.orderpoint']
#         reordring_rule.create ({
#           'name': res.id,
#           'product_id': res.id,
# #           'product_uom':  values['uom_id'],
#           'warehouse_id':1,
#            'company_id': 1,
#           'product_min_qty': 0,
#           'product_max_qty': 0,
#           'location_id': 8, 
#            'lead_type': 'supplier', 
#           'qty_multiple': 1,
#           'group_id': pg1.id,
#          })
#         return res
    
    
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    
    
    def action_update_quantity_on_hand(self):
        res = super(ProductTemplate, self).action_update_quantity_on_hand()
        pg1 = self.env['procurement.group'].create({})
        self.env['stock.warehouse.orderpoint'].create({
            'name': 'test',
            'product_id': self.id,
            'product_min_qty': 0,
            'product_max_qty': 0,
            'location_id': self.env.user.company_id.subcontracting_location_id.id,
            'allowed_location_ids': self.env.user.company_id.subcontracting_location_id.id, 
            'group_id': pg1.id,
        })
#         vals =  ({
#           'name': self.id,
#           'product_id': self.id,
#            'active': True, 
#           'product_uom': self.uom_po_id.id,
#           'warehouse_id':1,
#            'company_id': 1,
#           'product_min_qty': 0,
#           'product_max_qty': 0,
#           'location_id': 8, 
#            'lead_type': 'supplier', 
#           'qty_multiple': 1,
#          })
#         reordring_rule = self.env['stock.warehouse.orderpoint'].create(vals)
        return res
    
    
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        # TDE FIXME: should probably be copy_data
        self.ensure_one()
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)") % self.name
            default['seller_ids'] = self.seller_ids
        return super(ProductTemplate, self).copy(default=default)
    
    @api.model
    def create(self, values):
        res = super(ProductTemplate, self).create(values)
        reordring_rule = self.env['stock.warehouse.orderpoint']
        reordring_rule.create ({
          'name': res.id,
          'product_id': res.id,
          'active': True, 
          'product_uom':  values['uom_po_id'],
          'warehouse_id':1,
           'company_id': 1,
          'product_min_qty': 0,
          'product_max_qty': 0,
          'location_id': 8,
           'lead_days': 1, 
           'lead_type': 'supplier', 
          'qty_multiple': 1,
         })
        
        try:
            if values['purchase_ok'] == True:
                if values['seller_ids']:
                    pass
        except:
            raise exceptions.ValidationError('Please Select Vendor On Purchase Tab.')    
        
        return res
    
    

    
    allow_location = fields.Boolean(string="Is Finish or Un-Finished")    
    
    @api.onchange('allow_location')
    def onchange_location(self):
        if self.allow_location == True:
            if self.property_stock_production.id == 15:
                self.property_stock_production = 22
        elif self.allow_location == False:        
            if self.property_stock_production.id == 22:
                self.property_stock_production = 15    
    