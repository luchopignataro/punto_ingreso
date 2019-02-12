# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, _


class ObrasSociales(models.Model):
    _name = 'puntoingreso.obras_sociales'

    #paciente_id = fields.Many2one('res.partner', string="Paciente")

    name = fields.Many2one('res.partner', string="Obra social", domain="[('x_is_osocial', '=', True)]")





