# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.tools.float_utils import float_round as round
import math
import logging
_logger = logging.getLogger(__name__)

class EstudiosReport(models.AbstractModel):

    _name = 'report.puntoingreso.report_estudios_data'

    @api.multi
    #@api.one
    #@api.model

    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('puntoingreso.report_estudios_data')


        pacientes = self.env['puntoingreso.service'].search([('id', 'in', docids)], order="patient_ids").mapped('patient_ids')
        _logger.info('pacientes_1ro')
        _logger.info(pacientes)
        estudio_paciente = []
        gastos = []
        honors = []
        gastos_por = 0
        honors_por = 0
        tarifa = 0
        osocial = ''
        gastos_prom = 0
        honors_prom = 0
        total_h_paciente = 0
        total_g_paciente = 0

        for est in pacientes:

            servicios = self.env['puntoingreso.service'].search([('id', 'in', docids), ('patient_ids', '=', est.id)], order="patient_ids")
            _logger.info('servicios_2do')
            _logger.info(servicios)

            paciente = servicios[0].patient_ids.id
            total_h_paciente = 0
            total_g_paciente = 0
            _logger.info('cambia')
            _logger.info(paciente)
            ptg = 0
            pth = 0
            for serv in servicios:

                p_g = self.env['puntoingreso.service'].search([('id', 'in', docids), ('patient_ids', '=', serv.patient_ids.id)])

                _logger.info('p_g_estudios_tildados_paciente')
                _logger.info(p_g)

                for p in p_g:
                    ptg = ptg + p.costos
                    pth = pth + p.galeno



                if serv.variant_id.inc_subservicio:
                    _logger.info('incluye_subservicios')
                    osocial = serv.osocial
                    subservis = self.env['product.product'].search([('parent_id', '=', serv.variant_id.id)])
                    _logger.info(subservis)

                    for ss in subservis:
                        #ss_final = serv.copy()
                        _logger.info('type(serv)')
                        _logger.info(type(serv))
                        ss_final = dict({
                            'center': serv.center,
                            'codigo_servicio': serv.codigo_servicio,
                            'doctor_ids_internos': serv.doctor_ids_internos,
                            'doctor_ids': serv.doctor_ids,
                            'patient_ids': serv.patient_ids,
                            'variant_id': 0,
                            'costos': 0,
                            'galeno': 0,
                            'tarifa': 0,
                            'total_g': 0,
                            'total_h': 0,
                            'total_t': 0
                            })

                        # traemos logica de estudios.py
                        lista_precio_obrasocial = self.env['res.partner'].search([('name', '=', osocial.name),('x_is_osocial','=', True)]).property_product_pricelist.id

                        n_tarifa = None

                        tarifa_estudio = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id)])

                        if tarifa_estudio:
                            for x in tarifa_estudio:
                                if (x.date_start != False and x.date_end != False and x.date_start <= serv.input_date and x.date_end >= serv.input_date) or (x.date_end != False and x.date_end >= serv.input_date and x.date_start == False) or (x.date_start != False and x.date_start <= serv.input_date and x.date_end == False) or (x.date_start == False and x.date_end == False):

                                    n_tarifa = x.id
                                    fecha_inicio = x.date_start
                                    fecha_fin = x.date_end
                                    honor = x.min_quantity
                                    costo = x.costo

                        if n_tarifa is None:
                            fecha_inicio = None
                            fecha_fin = None
                            honor = 0
                            costo = 0
                        else:
                            fecha_inicio = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).date_start


                            fecha_fin = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).date_end


                            honor = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).min_quantity

                            costo = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).costo

                            t_modulada = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).modulada

                            if t_modulada:

                                tarifa_total = costo
                                costo_total = costo
                                honor_total = 0

                            else:
                                #sino todo como estaba
                                multi_costo = self.env['product.template'].browse(ss.product_tmpl_id.id).multi_costo
                                multi_honor = self.env['product.template'].browse(ss.product_tmpl_id.id).multi_honor

                                costo_total = multi_costo * costo
                                honor_total = multi_honor * honor

                                tarifa_total =  costo_total + honor_total

                        #costos
                        ss_final['costos'] = costo_total
                        ss_final['galeno'] = honor_total
                        ss_final['tarifa'] = tarifa_total
                        #datos generales
                        ss_final['service_id'] = ss.product_tmpl_id.id
                        ss_final['variant_id'] = ss.id

                        _logger.info('ss_final')
                        _logger.info(ss_final)


                        ss_final['total_g'] = costo_total
                        ss_final['total_h'] = honor_total
                        ss_final['total_t'] = tarifa_total

                        gastos.append(ss_final['costos'])
                        honors.append(ss_final['galeno'])

                        estudio_paciente.append(ss_final)

                        #ss_final.unlink()

                else:
                    _logger.info('NO_incluye_subservicios')

                    serv.total_g = ptg
                    serv.total_h = pth
                    serv.total_t = pth + ptg
                    _logger.info(ptg)
                    _logger.info(pth)

                    gastos.append(serv.costos)
                    honors.append(serv.galeno)
                    tarifa = serv.tarifa
                    osocial = serv.osocial

                    gastos_prom = gastos_prom+serv.costos
                    honors_prom = honors_prom+serv.galeno

                    _logger.info('mismo')
                    _logger.info(serv)
                    _logger.info(serv.service_id.display_name)
                    #_logger.info(serv.service_id.default_code)

                    estudio_paciente.append(serv)

            #estudio_paciente.append(servicios)
            #estudio_paciente.append(serv)

        _logger.info('estudio_paciente')
        _logger.info(estudio_paciente)


        total_total = gastos_prom + honors_prom

        if total_total != 0:
            gastos_por = (gastos_prom * 100) / total_total
            honors_por = (honors_prom * 100) / total_total
        else:
            gastos_por = 0
            honors_por = 0



        #Redondeo a 2 decimales de porcentaje
        gastos_por = math.ceil(gastos_por*100)/100
        honors_por = math.ceil(honors_por*100)/100



        gastos_prom = gastos_prom / len(gastos)
        honors_prom = honors_prom / len(honors)

        #Redondeo a 2 decimales de promedio
        # gastos_prom = math.ceil(gastos_prom*100)/100
        # honors_prom = math.ceil(honors_prom*100)/100
        gastos_prom = round(gastos_prom,2)
        honors_prom = round(honors_prom,2)


        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': pacientes,
            'docs_p': estudio_paciente,
            'gastos_prom': gastos_prom,
            'honors_prom': honors_prom,
            'gastos_por': gastos_por,
            'honors_por': honors_por,
            'osocial': osocial.display_name,
        }
        return report_obj.render('puntoingreso.report_estudios_data', docargs)

