# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, _


class Etiquetas(models.Model):
    _name = 'puntoingreso.etiquetas'

    name = fields.Char('Etiqueta', required=True, index=True)

