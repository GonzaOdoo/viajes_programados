from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    viaje_id = fields.Many2one(
        'viajes',
        string='Viaje',
        ondelete='set null'
    )