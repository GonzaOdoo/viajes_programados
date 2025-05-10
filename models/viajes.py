# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Viajes(models.Model):
    _name = 'viajes'
    _description = 'Viajes'
    
    # Campos básicos
    name = fields.Char('Referencia de viaje')
    active = fields.Boolean('Active', default=True)
    
    # Campos de capacidad
    capacidad_kg = fields.Float('Capacidad (kg)')
    capacidad_m = fields.Float('Capacidad (m²)')
    
    # Campos de relación
    conductor = fields.Many2one(
        'res.partner', 
        'Conductor',
        ondelete='set null'
    )
    vehiculo = fields.Many2one(
        'fleet.vehicle',
        'Vehículo',
        ondelete='set null'
    )
    
    # Campos de fecha/hora
    fecha = fields.Date('Fecha')
    fecha_inicio = fields.Datetime('Fecha de inicio')
    fecha_finalizacion = fields.Datetime('Fecha de finalización')
    
    # Campos de disponibilidad (readonly)
    disponibilidad_kg = fields.Float(
        'Disponibilidad en kg',
        readonly=True
    )
    disponibilidad_m = fields.Float(
        'Disponibilidad en m³',
        readonly=True
    )
    
    # Campos de estado y prioridad
    kanban_state = fields.Selection(
        selection=[
            ('normal', 'En progreso'),
            ('done', 'Listo'),
            ('blocked', 'Bloqueado')
        ],
        string='Estado de kanban',
        default='normal'
    )
    priority = fields.Boolean('Alta prioridad')
    
    # Campos adicionales
    notes = fields.Html('Notas')
    sequence = fields.Integer('Secuencia')
    sale_ids = fields.One2many(
        'sale.order',
        'viaje_id',
        string='Líneas de venta'
    )