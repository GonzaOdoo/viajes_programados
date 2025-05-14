# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)
class Viajes(models.Model):
    _name = 'viajes'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Viajes'
    _order = 'sequence, name'
    
    
    # Sistema de estados
    estado = fields.Selection(
        selection=[
            ('borrador', 'Nuevo'),
            ('programado', 'Programado'),
            ('preparacion', 'En preparación'),
            ('en_viaje', 'En viaje'),
            ('finalizado', 'Finalizado')
        ],
        string='Estado',
        default='borrador',
        tracking=True,
        group_expand='_expand_states'
    )
    
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).estado.selection]
    # Campos básicos
    name = fields.Char(
        string='Referencia de viaje',
        required=True,
        readonly=True,
        default=lambda self: _('Nuevo'),
        copy=False
    )
    active = fields.Boolean('Active', default=True)
    
    # Campos de capacidad
    capacidad_kg = fields.Float('Capacidad (kg)')
    capacidad_m = fields.Float('Capacidad (m²)')
    
    # Campos de relación
    conductor = fields.Many2one(
        'res.partner', 
        'Conductor',
        related='vehiculo.driver_id'
    )
    vehiculo = fields.Many2one(
        'fleet.vehicle',
        'Vehículo',
        ondelete='set null'
    )
    
    # Campos de fecha/hora
    fecha = fields.Date('Fecha')
    fecha_inicio = fields.Datetime('Fecha Programada',required = True,)
    fecha_finalizacion = fields.Datetime('Fecha de finalización')
    
    # Campos de disponibilidad (readonly)
    capacidad_kg = fields.Float(
        'Capacidad en kg',
        related='vehiculo.x_studio_capacidad_de_carga',
    )
    disponible_kg = fields.Float(
        'Capacidad en kg',
        compute='_compute_disponibles',
        store = True,
    )
    capacidad_m3 = fields.Float(
        'Capacidad en m³',
        related='vehiculo.x_studio_capacidad_volumetrica',
    )
    disponible_m3 = fields.Float(
        'Capacidad en m³',
        compute='_compute_disponibles',
        store = True,
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
    priority = fields.Selection(
    selection=[
        ('0', 'Ninguna'),
        ('1', 'Baja'),
        ('2', 'Media'),
        ('3', 'Alta'),
    ],
    string='Prioridad',
    default='0',
    tracking=True
)
    # Campos adicionales
    notes = fields.Html('Notas')
    sequence = fields.Integer('Secuencia')
    sale_ids = fields.One2many(
        'sale.order',
        'viaje_id',
        string='Órdenes de venta asociadas',
        help="Seleccione órdenes de venta existentes para asociar a este viaje"
    )

    @api.depends('sale_ids.x_studio_total_de_kg', 'sale_ids.x_studio_total_de_m_1', 'capacidad_kg', 'capacidad_m3')
    def _compute_disponibles(self):
        for viaje in self:
            # Sumar todos los kg de las órdenes asociadas
            total_kg = sum(viaje.sale_ids.mapped('x_studio_total_de_kg')) if viaje.sale_ids else 0
            
            # Sumar todos los m³ de las órdenes asociadas
            total_m3 = sum(viaje.sale_ids.mapped('x_studio_total_de_m_1')) if viaje.sale_ids else 0
            
            # Calcular disponibilidad (capacidad - total asignado)
            viaje.disponible_kg = viaje.capacidad_kg - total_kg
            viaje.disponible_m3 = viaje.capacidad_m3 - total_m3
            
            # Asegurar que no sean negativos
            if viaje.disponible_kg < 0:
                viaje.disponible_kg = 0
            if viaje.disponible_m3 < 0:
                viaje.disponible_m3 = 0
                
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('viajes') or _('Nuevo')
        return super(Viajes, self).create(vals)
        
    def write(self, vals):
        """Sobreescribimos write para actualizar commitment_date en las sale orders"""
        # 1. Pre-procesamiento antes de escribir
        if 'estado' in vals:
            # Validación para estado no borrador
            if vals['estado'] != 'borrador':
                for viaje in self:
                    if not viaje.fecha_inicio and 'fecha_inicio' not in vals:
                        raise UserError("Debe establecer una fecha de inicio antes de cambiar el estado")
            
        
        # 2. Escribir los valores (incluyendo los que acabamos de añadir)
        result = super(Viajes, self).write(vals)
        
        # 3. Post-procesamiento después de escribir
        if 'estado' in vals:
            # Actualizar commitment_date cuando deja de ser borrador
            if vals['estado'] != 'borrador':
                for viaje in self:
                    if viaje.sale_ids:
                        viaje.sale_ids.write({'commitment_date': viaje.fecha_inicio})
                        viaje.message_post(body=f"Fecha compromiso actualizada en {len(viaje.sale_ids)} órdenes de venta")
        
        return result

    #@api.onchange('estado')
    #def _onchange_estado(self):
    #   """Actualiza fecha_finalizacion cuando el estado cambia a 'finalizado'"""
    #    if self.estado == 'finalizado':
    #       self.fecha_finalizacion = fields.Datetime.now()

    def action_programar(self):
        for viaje in self:
            if viaje.estado != 'borrador':
                raise UserError('Solo puedes programar viajes en estado "Nuevo"')
            if not viaje.vehiculo:
                raise UserError('Debes asignar un vehículo antes de programar el viaje')
            if not viaje.fecha_inicio:
                raise UserError('Debes establecer una fecha de inicio antes de programar el viaje')
            viaje.write({
                'estado': 'programado',
                'kanban_state': 'normal'
            })
            viaje.message_post(body="Viaje programado")
        return True

    # Acción para iniciar preparación
    def action_preparar(self):
        for viaje in self:
            if viaje.estado != 'programado':
                raise UserError('Solo puedes preparar viajes en estado "Programado"')
                
            viaje.write({
                'estado': 'preparacion',
                'kanban_state': 'normal'
            })
            viaje.message_post(body="Preparación de viaje iniciada")
        return True

    # Acción para iniciar el viaje
    def action_iniciar_viaje(self):
        for viaje in self:
            if viaje.estado != 'preparacion':
                raise UserError('Solo puedes iniciar viajes en estado "En preparación"')
            if not viaje.conductor:
                raise UserError('Debes asignar un conductor antes de iniciar el viaje')
                
            viaje.write({
                'estado': 'en_viaje',
                'kanban_state': 'normal'
            })
            viaje.message_post(body="Viaje iniciado")
        return True

    # Acción para finalizar el viaje
    def action_finalizar(self):
        for viaje in self:
            if viaje.estado != 'en_viaje':
                raise UserError('Solo puedes finalizar viajes en estado "En viaje"')
                
            viaje.write({
                'estado': 'finalizado',
                'kanban_state': 'done',
                'fecha_finalizacion': fields.Datetime.now()
            })
            viaje.message_post(body="Viaje finalizado con éxito")
        return True

    # Acción para cancelar/reiniciar
    def action_cancelar(self):
        for viaje in self:
            viaje.write({
                'estado': 'borrador',
                'kanban_state': 'blocked'
            })
            # Opcional: Limpiar commitment_date al cancelar
            viaje.sale_ids.write({
                'commitment_date': False
            })
            viaje.message_post(body="Viaje cancelado y reiniciado")
        return True