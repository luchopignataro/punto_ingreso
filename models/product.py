# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, exceptions, _

class Product(models.Model):
    _inherit = 'product.template'
    # _parent_store = True

    multi_honor = fields.Float('Multiplicador honorario', required=True)
    multi_costo = fields.Float('Multiplicador costo', required=True)

    default_code = fields.Char(
        'Internal Reference', compute='_compute_default_code',
        inverse='_set_default_code', store=True)


    # inc_subservicio = fields.Boolean('Incluye subservicios?', store=True)

    # # Hierarchy fields
    # parent_id = fields.Many2one('product.template', 'Servicio principal', ondelete='restrict', store=True)

    # # Optional but good to have:
    # child_ids = fields.One2many('product.template', 'parent_id', 'Sub Servicios')



class ProductProduct(models.Model):
    _inherit = 'product.product'

    inc_subservicio = fields.Boolean('Incluye subservicios?', store=True)

    # Hierarchy fields
    parent_id = fields.Many2one('product.product', 'Servicio principal', ondelete='restrict', store=True)

    # Optional but good to have:
    child_ids = fields.One2many('product.product', 'parent_id', 'Sub Servicios')

    # sub_servicio = fields.Boolean('Es subservicio?', store=True)
    # subservicios = fields.Many2one('puntoingreso.subservicios', string='Sub servicios')

# class ProductProduct(models.Model):
#     _name = 'puntoingreso.subservicios'

    # servicio_principal = fields.Many2one('product.template', string='Estudio principal')
    # sub_servicios_ids = fields.One2many('product.template', 'subservicios', string='Sub Estudios')




