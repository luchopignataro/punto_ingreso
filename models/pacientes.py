# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _
import logging
_logger = logging.getLogger(__name__)

#class Patient(models.Model):
#   _name = 'puntoingreso.patient'
#   responsible_id = fields.Many2one('res.users', ondelete='set null', string='Responsible', index=True)
#   session_ids = fields.One2many('openacademy.session', 'course_id', string='Sessions')


class Partner(models.Model):
    _inherit = 'res.partner'

    # is_doctor = fields.Boolean('Is doctor', default=False)
    # is_patient = fields.Boolean('Is patient', default=False)
    # is_visitor = fields.Boolean('Is visitor', default=False)

    first_name = fields.Char(string='First name')#, required=True)
    last_name = fields.Char(string='Last name')#, required=True)
    dni = fields.Char('DNI')#, required=True)
    birthdate = fields.Date('Fecha de nacimiento')#, required=True)
    age = fields.Integer('Edad', default=0, compute='_get_age_from_date', readonly=True)
    input_date = fields.Date('Input date', default=fields.Date.today())
    is_alergic = fields.Boolean('Is alergic', default=False)
    phone = fields.Char('Phone')
    # mamotest_ids = fields.One2many('puntoingreso.mamotest', 'dni', string='Mamotest')

    category = fields.Selection([('asd', "asd"),('confirmed', "Confirmed"),('done', "Done")])

    comments = fields.Text('Comments')
    speciality = fields.Char('Speciality')

    level = fields.Selection([('asd', "asd"),('confirmed', "Confirmed"),('done', "Done")])

    osocial = fields.Char('Obra Social')
    sex = fields.Selection([('male','Male'),('female','Female'),('other','Other')])

    profile = fields.Selection([('student','Student'),('worker','Worker'),('other','Other')])

    square = fields.Char('Square')
    present_product = fields.Char('Present product')


    @api.onchange('birthdate')
    @api.depends('birthdate')
    def _get_age_from_date(self):
        for r in self:
            hoy = date.today()
            _logger.info(type(hoy))
            if not (r.birthdate):
                r.age = None
            else:
                asd = fields.Date.from_string(r.birthdate)
                _logger.info(type(r.birthdate))
                if (asd < hoy):
                    d1 = asd
                    d1 = int(d1.year)
                    d2 = int(hoy.year)

                    r.age = d2 - d1

    city = fields.Many2one('res.ciudades', 'Ciudad')

    @api.onchange('state_id')
    @api.depends('state_id')
    def _get_ciudades_from_provincia(self):
        for r in self:
            if not r.state_id:
                return False
            else:
                ciudades = self.env['res.ciudades'].search([('provincia_id','=',r.state_id.id)]).mapped('id')
                _logger.info('ciudades')
                _logger.info(ciudades)

            return {
                'domain': {
                    'city': [
                        ('id', 'in', ciudades)
                    ]
                }
            }


