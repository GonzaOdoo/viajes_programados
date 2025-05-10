from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    viaje_id = fields.Many2one(
        'viajes',
        string='Viaje',
        readonly=True,
        ondelete='set null'
    )
    fecha_programada = fields.Datetime('Fecha programada',related='viaje_id.fecha_inicio')