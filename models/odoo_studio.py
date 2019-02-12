# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta, date, datetime, time
import logging
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'
    #_rec_name = 'nombre_completo'

    property_product_pricelist = fields.Many2one('product.pricelist', store=True)

    x_DNI = fields.Char('DNI')
    x_Nombre = fields.Char('Nombre', required=True)
    x_Apellido = fields.Char('Apellido', required=True)
    x_alergico = fields.Boolean('Alergico')
    x_categoria = fields.Selection([('cat1','Oro'),('cat2','Plata'),('cat3','Bronce')])
    x_comentarios = fields.Text('Comentarios')
    x_edad = fields.Integer('Edad')
    x_especialidad = fields.Char('Especialidad')
    x_fecnac = fields.Datetime('Fecha de Nacimiento')
    x_is_doctor = fields.Boolean('Es doctor')
    x_is_patient = fields.Boolean('Es Paciente')
    x_is_visitor = fields.Boolean('Es Visitador')
    x_is_osocial = fields.Boolean('Es Obra social')
    x_is_colegio = fields.Boolean('Es Colegio médico')
    medico_interno = fields.Boolean('Es médico interno')
    x_matricula = fields.Char('Matrícula', domain="[('x_is_doctor','=', True)]")
    x_nivel = fields.Selection([('cat1','Categoria 1'),('cat2','Categoria 2'),('cat3','Categoria 3')])
    x_osocial = fields.Many2one('res.partner', string="Obra social", domain="[('x_is_osocial', '=', True)]")
    name_osocial = fields.Char('Obra social')
    n_afiliado = fields.Char('Número de socio')

    x_perfil = fields.Selection([('cat1','Categoria 1'),('cat2','Categoria 2'),('cat3','Categoria 3')])
    x_plaza = fields.Char('Plaza')
    x_producto_p = fields.Char('Producto a presentar')
    x_sexo = fields.Selection([('male','Masculino'),('female','Femenino')])
    x_telefono = fields.Char('Teléfono')
    x_services_id = fields.One2many('puntoingreso.service', 'patient_ids', string='Estudios')
    #x_centro = fields.Selection([('corrientes','Corrientes'),('bellavista','Bella Vista'),('saenzpenia','Saenz Peña'),('obera','Oberá'),('ceginjujuy','CEGIN-Jujuy'),('posadas','Posadas'),('curuzucuatia','Curuzú Cuatia')], string="Centro")
    x_centro = fields.Selection('_select_centros_from_variantes')

    x_etiquetas_id = fields.Many2many('puntoingreso.etiquetas', string='Etiquetas')

    x_informe = fields.Selection([('entregado','Entregado'),('pendiente','Pendiente de entrega')], string="Informe", default="pendiente")

    x_fuente = fields.Selection([('web','Web'),('facebook','Facebook'),('mailing','Médico'),('folleto','Folleto'),('diario','Diario'),('rev_tv','Revista o TV'),('fam_amigo','Familiar o amigo'),('osocial','Obra social'),('evento','Evento')], string="Origen lead")

    # SUBEstados del paciente

    x_subestado_ac = fields.Selection([('ac1','Acercamiento 1'),('ac2','Acercamiento 2'),('ac3','Acercamiento 3')], string="Subestado")
    x_subestado_ng = fields.Selection([('os1','OS - Trámite orden médica'),('os2','OS - Trámite autorización orden'),('os3','OS - Trámite plan asistencial'),('os4','OS - Trámite consulta médico'),('p1','Particular - consulta médico'),('p2','Particular - cuando tenga la plata')], string="Subestado")
    x_subestado_sv = fields.Selection([('nv1','No es target (Edad - Hombres - Otras consultas médicas)'),('nv2','Vive lejos (no es target)'),('nv3','No le autorizaron el trámite de Plan asistencial'),('nv4','Otro centro donde se realiza'),('nv5','No tiene OS y no puede pagar')], string="Subestado")

    # FIN SUBEstados del paciente


    # FICHA del paciente

    x_antecedentes_cancer = fields.Boolean('¿Tiene antecedentes familiares con cáncer de mama?')
    x_quien = fields.Char('¿Quién?')

    x_cirugias_mamas = fields.Boolean('¿Tiene cirugías de mamas?')
    x_cirugias_mamas_anio = fields.Char('Año')

    x_radiacion_mamas = fields.Boolean('¿Se ha realizado tratamiento con radiaciones de las mamas?')
    x_radiacion_mamas_anio = fields.Char('Año')

    x_tratamiento_hormonal = fields.Boolean('¿Realiza en la actualidad tratamiento hormonal?')
    x_tratamiento_hormonal_cuando = fields.Date('¿Desde cuándo?')

    x_secrecion_mamaria = fields.Boolean('¿Presenta secreción mamaria?')

    x_lunares_verrugas = fields.Boolean('¿Presenta lunares o verrugas en la zona de las mamas?')

    x_primera_vez = fields.Boolean('¿Se realiza el estudio por primera vez?')
    x_estudios_anteriores = fields.Boolean('¿Trajo estudios anteriores?')



    # FIN FICHA del paciente

    # Estados del paciente

    x_estado = fields.Selection([('potencial','Prospect'),('contactado','Acercamiento'),('negociacion','Negociación'),('spam','Spam'),('venta','Con venta'),('noventa','Sin venta')], string="Estado", default='potencial')


    @api.multi
    def action_potencial(self):
        self.x_estado = 'potencial'

    @api.multi
    def action_contactado(self):
        self.x_estado = 'contactado'

    @api.multi
    def action_negociacion(self):
        self.x_estado = 'negociacion'

    @api.multi
    def action_spam(self):
        self.x_estado = 'spam'

    @api.multi
    def action_venta(self):
        self.x_estado = 'venta'

    @api.multi
    def action_noventa(self):
        self.x_estado = 'noventa'

    # FIN Estados del paciente


    def _select_centros_from_variantes(self):
        centro = self.env['product.attribute'].search([('name','=','Centro')]).id
        centros = self.env['product.attribute.value'].search([('attribute_id', '=', centro)])
        _logger.info(centro)
        _logger.info(centros)

        centross = []

        for c in centros:
            centross.append((str(c.id),c.name))

        _logger.info(centross)
        return centross



    nombre_completo = fields.Char('Nombre completo', compute="_complete_name")
    #name = fields.Char('Nombre entero', compute="_complete_name", required=False)
    display_name = fields.Char('Nombre entero')

    @api.multi
    @api.onchange('x_Nombre','x_Apellido')
    def _complete_name(self):
        for r in self:
            if r.x_Nombre and r.x_Apellido:
                r.name = '%s %s' % (r.x_Nombre, r.x_Apellido)
                r.display_name = '%s %s' % (r.x_Nombre, r.x_Apellido)


    @api.multi
    @api.onchange('x_osocial')
    def _onchange_osocial(self):
         osocial_nombre = self.x_osocial.name
         self.name_osocial = '%s' % (osocial_nombre)
