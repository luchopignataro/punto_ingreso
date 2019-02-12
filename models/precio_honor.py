# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta, date, datetime, time
import logging
_logger = logging.getLogger(__name__)


class PrecioHonor(models.Model):
    _inherit = 'product.pricelist.item'


    min_quantity = fields.Float('Precio honorario/Galeno', required=True)
    costo = fields.Float('Precio costo', required=True)

    modulada = fields.Boolean('Es tarifa modulada?', store=True)
    codigo_servicio = fields.Char('Código de servicio',store=True)

    @api.onchange('min_quantity','costo')
    @api.depends('fixed_price','name','product_id')
    def _calcular_precio_final(self):

        prod_name = self.name.split('(')
        prod_name = prod_name[0]

        _logger.info('tarifa_modulada')
        _logger.info(self.modulada)

        if self.modulada == False:
            _logger.info('NO_tarifa_modulada')
            c = self.env['product.product'].browse(self.product_id.id).product_tmpl_id

            _logger.info(c.id)
            _logger.info(self.name)
            _logger.info(prod_name)

            multi_h = self.env['product.template'].browse(c.id).multi_honor
            multi_c = self.env['product.template'].browse(c.id).multi_costo
            # h = self.env['product.product'].search([('name', '=', self.name)]).multi_costo
            # c = self.env['product.product'].search([('name', '=', self.name)]).multi_costo

            self.fixed_price = (multi_c * self.costo) + (multi_h * self.min_quantity)
        else:
            _logger.info('es_tarifa_modulada')
            self.min_quantity = 0
            self.fixed_price = self.costo

