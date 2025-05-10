from odoo import fields,models,api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    capacidad_m3 = fields.Float('Capacidad m3')
    capacidad_kg = fields.Float('Capacidad kg')