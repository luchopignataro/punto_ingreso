# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta, date, datetime, time
import logging
_logger = logging.getLogger(__name__)


class Ciudades(models.Model):
    _name = 'res.ciudades'

    name = fields.Char('Ciudad', required=True)

    provincia_id = fields.Many2one('res.country.state', 'Provincia', store=True)




class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    ciudades_ids = fields.One2many('res.ciudades', 'provincia_id', 'Ciudades')
