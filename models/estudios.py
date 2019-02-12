# -*- coding: utf-8 -*-

from datetime import timedelta, date
from odoo import models, fields, api, exceptions, _
import logging
_logger = logging.getLogger(__name__)


class Service(models.Model):
    _name = 'puntoingreso.service'

    #name = fields.Char('Name', compute='_service_name', readonly=True)

    input_date = fields.Date('Fecha del estudio', default=fields.Date.today(), readonly=True)
    # service_date = fields.Datetime('Service date', required=True)
    service_date = fields.Datetime('Fecha y hora', default=fields.Datetime.now, readonly=True)
    #service_date = fields.Datetime('Service date', default=fields.Datetime.now(), readonly=True)

    active = fields.Boolean('Active', default=True)

    doctor_ids = fields.Many2one('res.partner', string="Doctor", domain=[('x_is_doctor', '=', True)], required=True)

    doctor_ids_internos = fields.Many2one('res.partner', string="Médico interno", domain=[('x_is_doctor', '=', True),('medico_interno','=', True)])
    #patient_ids = fields.Many2one('res.partner', string="Patient", domain=[('x_is_patient', '=', True)], context="{'default_x_is_patient': 1,'search_default_x_is_patient': 1}", required=True)
    patient_ids = fields.Many2one('res.partner', string="Patient", domain=[('x_is_patient', '=', True)], required=True)

    patient_dni = fields.Char('DNI Paciente', related="patient_ids.x_DNI", store=True)

    #service_id = fields.Many2one('product.template', string="Service", required=True)
    service_id = fields.Many2one('product.template', string="Service", compute='_check_osocial_centro_facturacion')
    # variant_id = fields.Many2one('product.product', string="Variant", domain=[('parent_id', '=', False)],required=True)
    variant_id = fields.Many2one('product.product', string="Variant", required=True)

    codigo_servicio = fields.Char('Código de Servicio', store=True)

    modulada = fields.Boolean(string="Tarifa modulada?", store=True)


    inc_subservicio = fields.Boolean('Incluye subservicios?', store=True)
    # parent_id = fields.Many2one('puntoingreso.service', 'Servicio principal', ondelete='restrict', store=True)
    # child_ids = fields.One2many('puntoingreso.service', 'parent_id', 'Sub Servicios')


    center = fields.Selection('_select_centros_from_variantes', required=True)


    osocial = fields.Many2one('res.partner', string="Obra Social", domain=[('x_is_osocial', '=', True)], required=True)

    n_afiliado = fields.Char('Número de socio')

    tarifa = fields.Float('Tarifa estudio', compute="_check_osocial_centro_facturacion", store=True)
    galeno = fields.Float('Honorario/Galeno', compute="_check_osocial_centro_facturacion", store=True)
    costos = fields.Float('Costos', compute="_check_osocial_centro_facturacion", store=True)

    turno = fields.Selection([('web','Asistente virtual web'),('facebook','Facebook'),('whatsapp','Whatsapp'),('telefono','Te llamamos por teléfono'),('ll_centro','Llamaste a nuestro centro'),('email','Email'),('familiar','Lo coordinó un familiar'),('pr_centro','Te presentaste en el centro')], string="Turno vía")

    validado = fields.Boolean(string="Validado?", compute='_check_osocial_centro_facturacion', store=True)
    primera_vez = fields.Boolean(string="Es la primera vez?", store=True)

    facturado = fields.Char(string="Factura", compute='_check_osocial_centro_facturacion', store=True)

    #solo para reporte.
    total_g = fields.Float('total gastos', store=True)
    total_h = fields.Float('total honors', store=True)
    total_t = fields.Float('total total', store=True)

    #usuario_logueado = fields.Char('Usuario', compute="_get_current_user",store=True)

    # @api.depends()
    # def _get_current_user(self):
    #     for rec in self:
    #         rec.usuario_logueado = self.env.user
     # i think this work too so you don't have to loop
     #self.update({'current_user' : self.env.user.id})


    # Estado de estudio
    state = fields.Selection([('pendiente','Pendiente de entrega'),('entregado','Informe entregado')], string="Estado", default='pendiente')

    @api.multi
    def action_pending(self):
        self.state = 'pendiente'

    @api.multi
    def action_confirm(self):
        self.state = 'entregado'

    # FIN Estado de estudio

    # Actualizamos la OS del paciente

    @api.onchange('osocial')
    def update_osocial_paciente(self):
        if not self.osocial:
            paciente = self.env['res.partner'].search([('id', '=', self.patient_ids.id),('x_is_patient','=', True)])
            paciente.write({'n_afiliado': None})
            name_center = self.center
            if name_center:
                paciente.write({'x_centro': name_center})
            self.n_afiliado = None
            return

        paciente = self.env['res.partner'].search([('id', '=', self.patient_ids.id),('x_is_patient','=', True)])
        paciente.write({'x_osocial': self.osocial.id})
        paciente.write({'n_afiliado': self.n_afiliado})

    @api.onchange('n_afiliado')
    def update_n_afiliado_paciente(self):
        if not self.n_afiliado:
            return
        paciente = self.env['res.partner'].search([('id', '=', self.patient_ids.id),('x_is_patient','=', True)])
        paciente.write({'n_afiliado': self.n_afiliado})

    # @api.onchange('patient_ids')
    # @api.multi
    # def update_patient_ids_osocial_afiliado(self):
    #     if not self.patient_ids:
    #         return
    #     paciente = self.env['res.partner'].search([('id', '=', self.patient_ids.id),('x_is_patient','=', True)])

        #self.osocial = paciente.x_osocial.id
        #self.n_afiliado = paciente.n_afiliado

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


    # Validación de Obra social y centro para facturación
    # -- INICIO FUNCCION
    @api.onchange('patient_ids','variant_id','center')
    @api.depends('center', 'variant_id')
    #@api.model
    @api.multi
    #@api.one
    def _check_osocial_centro_facturacion(self):
        #self.ensure_one()
        for r in self:
            if not r.center or not r.osocial or not r.variant_id:
                return False
            else:
                #name_center = r._get_string_from_selection('center', r.center)
                #name_center = r._get_string_from_selection()
                osocial = r.osocial
                product_id = r.variant_id

                prd_tmp = self.env['product.template'].browse(r.variant_id.product_tmpl_id)



                lista_precio_obrasocial = self.env['res.partner'].search([('name', '=', osocial.name),('x_is_osocial','=', True)]).property_product_pricelist.id


                n_tarifa = None

                tarifa_estudio = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', product_id.id)])

                if tarifa_estudio:
                    for x in tarifa_estudio:

                        if (x.date_start != False and x.date_end != False and x.date_start <= r.input_date and x.date_end >= r.input_date) or (x.date_end != False and x.date_end >= r.input_date and x.date_start == False) or (x.date_start != False and x.date_start <= r.input_date and x.date_end == False) or (x.date_start == False and x.date_end == False):

                            n_tarifa = x.id
                            fecha_inicio = x.date_start
                            fecha_fin = x.date_end
                            honor = x.min_quantity
                            costo = x.costo

                            r.facturado = False
                            r.validado = False

                        else:
                            r.facturado = '%s' % ('Factura individual')
                            r.validado = True
                else:
                    r.facturado = '%s' % ('Factura individual')
                    r.validado = True

                if n_tarifa is None:
                    fecha_inicio = None
                    fecha_fin = None
                    honor = 0
                    costo = 0
                else:
                    fecha_inicio = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', product_id.id),('id','=',n_tarifa)]).date_start


                    fecha_fin = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', product_id.id),('id','=',n_tarifa)]).date_end


                    honor = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', product_id.id),('id','=',n_tarifa)]).min_quantity

                    costo = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', product_id.id),('id','=',n_tarifa)]).costo

                    t_modulada = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', product_id.id),('id','=',n_tarifa)]).modulada

                    if t_modulada:
                        r.modulada = True

                service_id_n = self.env['product.product'].search([('id', '=', product_id.id)])

                r.service_id = service_id_n.product_tmpl_id

                #si la tarifa es modulada, cargamos total = costo y los demás en 0
                if r.modulada:
                    tarifa_total = costo
                    r.galeno = 0
                    r.costos = tarifa_total
                    r.tarifa = tarifa_total
                else:
                    #sino todo como estaba
                    multi_costo = self.env['product.template'].browse(service_id_n.product_tmpl_id.id).multi_costo
                    multi_honor = self.env['product.template'].browse(service_id_n.product_tmpl_id.id).multi_honor

                    costo_total = multi_costo * costo
                    honor_total = multi_honor * honor

                    tarifa_total =  costo_total + honor_total

                    r.galeno = honor_total
                    r.costos = costo_total
                    r.tarifa = tarifa_total

    # -- FIN FUNCCION
            #return True


    #@api.onchange('center')
    def _get_string_from_selection(self):
        iddd = self.center
        #_logger.info(iddd)
        #_logger.info(str(self.env['product.attribute.value'].search([('id', '=', iddd)]).name))
        return unicode(self.env['product.attribute.value'].search([('id', '=', iddd)]).name)

    def _get_id_from_selection(self):
        iddd = self.center
        _logger.info(self.env['product.attribute.value'].search([('id', '=', iddd)]))
        return self.env['product.attribute.value'].search([('id', '=', iddd)]).id


    @api.depends('service_date')
    def _fecha_actual(self):
        for s in self:
            s.service_date = s.create_date



    # Dependemos del Centro para listar los Servicios
    @api.onchange('center')
    @api.depends('center')
    #@api.multi
    def _get_services_from_center_value(self):
        if not self.center:
            return False
        else:
            #name_center = self._get_string_from_selection('center', self.center)
            name_center = self._get_string_from_selection()
            centers = ['Oberá','Posadas']
            _logger.info('centers')
            _logger.info(centers)

            if name_center in centers:
                self.validado = True
            else:
                self.validado = False



        self.variant_id = None

        centers_ids = self.center

        name_center = self._get_string_from_selection()
        id_center = self._get_id_from_selection()
        _logger.info('id_center')
        _logger.info(id_center)
        #name_center = "%s" % (name_center)
        #_logger.info(name_center)
        #name_center = dict(self._centers_values)[self.center]

        # search_fields = [
        #     ('attribute_value_ids.name', '=', name_center)
        # ]


        # if self.service_id:
        #     search_fields.append( ('id', 'in', [product.id for product in self.service_id.product_variant_ids] ) )


        # query = """SELECT product_attribute_line_id FROM public.product_attribute_line_product_attribute_value_rel where product_attribute_value_id = %i"""
        # query = query % (id_center)
        # self.env.cr.execute(query)
        # records = self.env.cr.dictfetchall()

        # ids = '%s' % '('
        # largo = len(records)
        # i = 0
        # for r in records:
        #     i = i+1
        #     if i == largo:
        #         ids = ids+str(r['product_attribute_line_id'])+')'
        #     else:
        #         ids = ids+str(r['product_attribute_line_id'])+','


        # _logger.info('query_ids')
        # _logger.info(ids)


        # query1 = """SELECT product_tmpl_id FROM public.product_attribute_line where id in %s"""
        # query1 = query1 % (ids)
        # self.env.cr.execute(query1)
        # records1 = self.env.cr.dictfetchall()
        # product_tmpl = [result['product_tmpl_id'] for result in records1]


        # _logger.info('product_tmpl')
        # _logger.info(product_tmpl)

        search_fields = [
            #('product_tmpl_id', 'in', product_tmpl),
            ('parent_id', '=', False),
            ('attribute_value_ids.name', '=', name_center)
        ]
        _logger.info('search_fields')
        _logger.info(search_fields)

        variant_ids = self.env['product.product'].search(search_fields)
        _logger.info('variant_ids')
        _logger.info(variant_ids)

        variants = [x.id for x in variant_ids]
        services_ids = [x.product_tmpl_id.id for x in variant_ids]

        return {
            'domain': {
                # 'service_id': [
                #     ('id', 'in', services_ids)
                # ],
                'variant_id': [
                    ('id', 'in', variants)
                ]
            }
        }



    @api.onchange('variant_id')
    def _service_name(self):
        for s in self:
            #if not s.service_id or not s.variant_id:
            if not s.variant_id:
                return False
            else:
                s.name = "%s" % (s.variant_id.display_name)

    @api.onchange('variant_id')
    def _filter_osociales_variant(self):
        if not self.variant_id:
            return False
        _logger.info('entra_filter_osociales')
        _logger.info(self.variant_id.display_name)

        obras_sociales_select = []
        tarifa_item = self.env['product.pricelist.item'].search([('name', '=', self.variant_id.display_name)])


        _logger.info(tarifa_item)
        _logger.info(len(tarifa_item))
        if len(tarifa_item) > 0:
            _logger.info('tarifa_item_>_0')
            for x in tarifa_item:

                if (x.date_start != False and x.date_end != False and x.date_start <= self.input_date and x.date_end >= self.input_date) or (x.date_end != False and x.date_end >= self.input_date and x.date_start == False) or (x.date_start != False and x.date_start <= self.input_date and x.date_end == False) or (x.date_start == False and x.date_end == False):
                    _logger.info('entra_if')

                    _logger.info(x.pricelist_id.id)
                    pricelista = self.env['product.pricelist'].search([('id', '=', x.pricelist_id.id)])
                    _logger.info('pricelist')
                    _logger.info(pricelista)

                    obrasoc = self.env['res.partner'].search([('property_product_pricelist', '=', pricelista.id)])
                    _logger.info(obrasoc)

                    if len(obrasoc) > 1:
                        for os in obrasoc:
                            obras_sociales_select.append(os.id)
                    else:
                        obras_sociales_select.append(obrasoc.id)

        elif len(tarifa_item) == 0:
            item = self.env['product.product'].search([('name', '=', self.variant_id.display_name)])
            #item = self.env['product.product'].search([('id', '=', self.variant_id.id)])
            _logger.info('item')
            _logger.info(item)
            #sub_items = self.env['product.product'].search([('parent_id', '=', item.id)])
            sub_items = self.env['product.product'].search([('parent_id', '=', self.variant_id.id)])
            _logger.info('sub_items')
            _logger.info(sub_items)

            for sub in sub_items:
                tarifa_item = self.env['product.pricelist.item'].search([('name', '=', sub.display_name)])
                _logger.info('tarifa_sub_item')
                _logger.info(tarifa_item)

                if len(tarifa_item) > 0:
                    _logger.info('tarifa_item_>_0')
                    for x in tarifa_item:

                        if (x.date_start != False and x.date_end != False and x.date_start <= self.input_date and x.date_end >= self.input_date) or (x.date_end != False and x.date_end >= self.input_date and x.date_start == False) or (x.date_start != False and x.date_start <= self.input_date and x.date_end == False) or (x.date_start == False and x.date_end == False):
                            _logger.info('entra_if')

                            _logger.info(x.pricelist_id.id)
                            pricelista = self.env['product.pricelist'].search([('id', '=', x.pricelist_id.id)])
                            _logger.info('pricelist')
                            _logger.info(pricelista)

                            obrasoc = self.env['res.partner'].search([('property_product_pricelist', '=', pricelista.id)])
                            _logger.info(obrasoc)

                            if len(obrasoc) > 1:
                                for os in obrasoc:
                                    obras_sociales_select.append(os.id)
                            else:
                                obras_sociales_select.append(obrasoc.id)

        _logger.info(obras_sociales_select)

        return {
            'domain': {
                'osocial': [
                    ('id', 'in', obras_sociales_select)
                ]
            }
        }

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'


    name = fields.Char('Name', compute='_get_pricelist_item_name_price', help="Explicit rule name for this pricelist line.", store=True)
