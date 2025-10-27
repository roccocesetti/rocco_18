# -*- coding: utf-8 -*-
# TODO :- <Incoterm>0</Incoterm> check this field is required
from odoo.addons.gls_italy_odoo_integration.models.gls_italy_response import Response
from odoo.exceptions import ValidationError
from odoo import fields, models, api, _
import xml.etree.ElementTree as etree
from requests import request
import binascii
import logging
import time
import urllib.parse
import requests

_logger = logging.getLogger("GLS Italy")


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[("gls_italy", "GLS Italy")], ondelete={'gls_italy': 'set default'})
    gls_italy_modalitaIncasso = fields.Selection([('CONT', 'CONT , Contante'),
                                                  ('AC', 'AC, Assegno circolare'), ('AB', 'AB, Assegno bancario'),
                                                  ('AP', 'AP, Assegno postale'),
                                                  ('ASS', 'ASS, Ass postale/bancario/circolare'),
                                                  ('ABP', 'ABP, Ass. bancario/postale'),
                                                  ('ASR', 'ASR, Ass. come rilasciato'),
                                                  ('ARM', 'ARM, Ass. come rilasciato int. Mittente'),
                                                  ('ABC', 'ABC, Ass. bancario/circolare - no postale'),
                                                  ('ASRP', 'ASRP,Ass. come rilasciato - no postale'),
                                                  ('ARMP', 'ARMP, Ass. come rilasciato int. Mittente – no postale ')])

    gls_italy_port_type = fields.Selection([('F', 'F, Franco'), ('A', 'A, Assegnato')], string="GLS Italy Port Type",
                                           help="Select GLS Port Type")

    gls_italy_shipping_type = fields.Selection([('N', 'N, Nazionale'), ('P', 'P, Parcel Europa e Extracee')],
                                               string="GLS Italy Shipping Type", help="Choose Shipping Type",
                                               default="N")
    gls_packaging_id = fields.Many2one('stock.package.type', string="Default Package Type")
    gls_italy_cod = fields.Boolean(string="Cash On Delivery")
    gls_flex_delivery_service = fields.Boolean(string="Use Flex Delivery", default=False)

    def gls_itlay_request_quotation_request_data(self, order):
        """
        :parameter: order
        :return request data for RequestQuotation API
        """
        SedeGls = order and order.company_id and order.company_id.gls_italy_sede
        CodiceClienteGls = order and order.company_id and order.company_id.gls_italy_customer_code
        PasswordClienteGls = order and order.company_id and order.company_id.gls_italy_password

        receiver_id = order.partner_id
        contract_code = order.company_id and order.company_id.gls_italy_contract_code
        total_weight = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line]) or 0
        if total_weight > 0:
            total_weight = round(total_weight, 2)

        Info = etree.Element('Info')
        etree.SubElement(Info, 'SedeGls').text = "{}".format(SedeGls)
        etree.SubElement(Info, 'CodiceClienteGls').text = "{}".format(CodiceClienteGls)
        etree.SubElement(Info, 'PasswordClienteGls').text = "{}".format(PasswordClienteGls)
        Quotation = etree.SubElement(Info, 'Quotation')
        etree.SubElement(Quotation, 'CodiceContrattoGls').text = "{}".format(contract_code)
        etree.SubElement(Quotation, 'RagioneSociale').text = "{}".format(receiver_id.name if receiver_id.company_type == 'company' else receiver_id.parent_id.name)
        etree.SubElement(Quotation, 'Indirizzo').text = "{}".format(receiver_id.street)
        etree.SubElement(Quotation, 'Localita').text = "{}".format(receiver_id.city)
        etree.SubElement(Quotation, 'Zipcode').text = "{}".format(receiver_id.zip)
        etree.SubElement(Quotation, 'Provincia').text = "{}".format(receiver_id.state_id.code)
        etree.SubElement(Quotation, 'Colli').text = "1"
        etree.SubElement(Quotation, 'PesoReale').text = "{}".format(total_weight)
        if self.gls_italy_cod:
            etree.SubElement(Quotation, 'ImportoContrassegno').text = "{}".format(order.amount_total)
        # etree.SubElement(Quotation, 'ServiziAccessori').text = ""
        etree.SubElement(Quotation, 'TipoSpedizione').text = "{}".format(self.gls_italy_shipping_type)
        request_data = etree.tostring(Info)

        encode_data = "XMLInfoQuotation=%s" % urllib.parse.quote(request_data)
        try:
            url = "{}/RequestQuotation".format(order.company_id and order.company_id.gls_italy_api_url)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            response_data = requests.request(method="POST", url=url, headers=headers, data=encode_data)

            if response_data.status_code in [200, 201, 202]:
                _logger.info(":: get successfully response from {}".format(url))
                response_data = Response(response_data)
                result = response_data.dict()
                if result['QuotationRequests']:
                    return result['QuotationRequests']['QuotationRequest']['Token']
            else:
                raise ValidationError(_('getting some error from %s \n response data %s') % (url, response_data.text))
        except Exception as error:
            if result['DescrizioneErrore']:
                raise ValidationError(_(result.get('DescrizioneErrore')))
            else:
                raise ValidationError("Getting Some Error From {} \n response data {}".format(url, response_data.text))

    def gls_italy_rate_shipment(self, order):

        request_quotation_token = self.gls_itlay_request_quotation_request_data(order)
        if not request_quotation_token:
            raise ValidationError("Request Token not found.")

        SedeGls = order and order.company_id and order.company_id.gls_italy_sede
        CodiceClienteGls = order and order.company_id and order.company_id.gls_italy_customer_code
        PasswordClienteGls = order and order.company_id and order.company_id.gls_italy_password

        Info = etree.Element('Info')
        etree.SubElement(Info, 'SedeGls').text = "{}".format(SedeGls)
        etree.SubElement(Info, 'CodiceClienteGls').text = "{}".format(CodiceClienteGls)
        etree.SubElement(Info, 'PasswordClienteGls').text = "{}".format(PasswordClienteGls)
        Request = etree.SubElement(Info, 'Request')
        etree.SubElement(Request, 'CodiceRichiesta').text = "{}".format(request_quotation_token)
        request_data = etree.tostring(Info)

        encode_data = "XMLQuotationRequest=%s" % urllib.parse.quote(request_data)

        try:
            url = "{}/GetQuotation".format(order.company_id and order.company_id.gls_italy_api_url)
            headers = {'Content-Type': 'application/x-www-form-urlencoded',}
            time.sleep(4)
            response_data = requests.request(method="POST", url=url, headers=headers, data=encode_data)

            if response_data.status_code in [200, 201, 202]:
                _logger.info(":: get successfully response from {}".format(url))
                response_data = Response(response_data)
                result = response_data.dict()
                rate = result['Quotations']['Quotation']['CostiImponibile'] if result['Quotations'] else 0.00
                if float(rate) > 0:
                    return {'success': True, 'price': float(rate), 'error_message': False, 'warning_message': False}
                else:
                    return {'success': False, 'price': 0.0,
                            'error_message': ('getting some error from %s \n response data %s') % (
                                url, response_data.text), 'warning_message': False}
            else:
                return {'success': False, 'price': 0.0,
                        'error_message': ('getting some error from %s \n response data %s') % (url, response_data.text),
                        'warning_message': False}
        except Exception as error:
            if result['DescrizioneErrore']:
                raise ValidationError(_(result.get('DescrizioneErrore')))
            else:
                raise ValidationError("Getting Some Error From {} \n response data {}".format(url, response_data.text))

    def gls_itlay_create_order_request_data(self, pickings):
        """
        :parameter pickings
        :return request data for AddParcel API

        """
        sede_gls = pickings.company_id and pickings.company_id.gls_italy_sede
        customer_code = pickings.company_id and pickings.company_id.gls_italy_customer_code
        password_gls = pickings.company_id and pickings.company_id.gls_italy_password
        receiver_id = pickings.partner_id
        contract_code = pickings.company_id and pickings.company_id.gls_italy_contract_code
        bulk_weight = pickings.weight_bulk
        parcel_info = ""
        parcel_value = pickings.sale_id and pickings.sale_id.amount_total or 0.00
        package_ids = pickings.move_line_ids.mapped('result_package_id')
        for package_data in package_ids:
            if package_data.shipping_weight == 0:
                raise ValidationError(_('package weight must be greater than 0'))
            parcel_data = etree.Element('Parcel')
            etree.SubElement(parcel_data, 'CodiceContrattoGls').text = "{}".format(contract_code)
            etree.SubElement(parcel_data, 'RagioneSociale').text = "{}".format(
                receiver_id.display_name.replace('&', ''))
            etree.SubElement(parcel_data, 'Indirizzo').text = "{}".format(receiver_id.street)
            etree.SubElement(parcel_data, 'Localita').text = "{}".format(receiver_id.city)
            etree.SubElement(parcel_data, 'Zipcode').text = "{}".format(receiver_id.zip)
            etree.SubElement(parcel_data, 'Provincia').text = "{}".format(receiver_id.country_id.code)
            etree.SubElement(parcel_data, 'Bda').text = "{}".format(package_data.name)
            etree.SubElement(parcel_data, 'Colli').text = "1"
            etree.SubElement(parcel_data, 'PesoReale').text = "{}".format(package_data.shipping_weight)
            if self.gls_italy_cod:
                etree.SubElement(parcel_data, 'ImportoContrassegno').text = "{}".format(parcel_value)
            etree.SubElement(parcel_data, 'TipoPorto').text = "{}".format(self.gls_italy_port_type)
            etree.SubElement(parcel_data, 'CodiceClienteDestinatario').text = ""
            etree.SubElement(parcel_data, 'Email').text = "{}".format(receiver_id.email or " ")
            etree.SubElement(parcel_data, 'Cellulare1').text = "{}".format(receiver_id.phone.replace(' ','') or '')
            etree.SubElement(parcel_data, 'ModalitaIncasso').text = "{}".format(self.gls_italy_modalitaIncasso)
            etree.SubElement(parcel_data, 'DataPrenotazioneGDO').text = ""
            etree.SubElement(parcel_data, 'OrarioNoteGDO').text = ""
            etree.SubElement(parcel_data, 'GeneraPdf').text = "4"
            etree.SubElement(parcel_data, 'FormatoPdf').text = ""
            etree.SubElement(parcel_data, 'ContatoreProgressivo').text = "{}".format(time.strftime("%d%m%M%S"))
            etree.SubElement(parcel_data, 'NumDayListSped').text = ""
            etree.SubElement(parcel_data, 'IdentPIN').text = ""
            etree.SubElement(parcel_data, 'AssicurazioneIntegrativa').text = ""
            etree.SubElement(parcel_data, 'ServiziAccessori').text = "31" if self.gls_flex_delivery_service else ""
            etree.SubElement(parcel_data, 'TipoSpedizione').text = "{}".format(self.gls_italy_shipping_type)
            etree.SubElement(parcel_data, 'ValoreDichiarato').text = ""
            etree.SubElement(parcel_data, 'PersonaRiferimento').text = "{}".format(
                receiver_id.name.replace('&', '') or '')
            etree.SubElement(parcel_data, 'Contenuto').text = ""
            etree.SubElement(parcel_data, 'TelefonoDestinatario').text = "{}".format(receiver_id.phone.replace(' ','') or '')
            etree.SubElement(parcel_data, 'CategoriaMerceologica').text = ""
            etree.SubElement(parcel_data, 'FatturaDoganale').text = ""
            etree.SubElement(parcel_data, 'DataFatturaDoganale').text = ""
            etree.SubElement(parcel_data, 'PezziDichiarati').text = ""
            etree.SubElement(parcel_data, 'NazioneOrigine').text = ""
            etree.SubElement(parcel_data, 'TelefonoMittente').text = ""
            etree.SubElement(parcel_data, 'NumeroFatturaCOD').text = ""
            etree.SubElement(parcel_data, 'DataFatturaCOD').text = ""
            etree.SubElement(parcel_data, 'NoteIncoterm').text = ""
            parcel = etree.tostring(parcel_data, encoding='unicode')
            parcel_info += parcel
        if bulk_weight:
            parcel_data = etree.Element('Parcel')
            etree.SubElement(parcel_data, 'CodiceContrattoGls').text = "{}".format(contract_code)
            etree.SubElement(parcel_data, 'RagioneSociale').text = "{}".format(
                receiver_id.display_name.replace('&', ''))
            etree.SubElement(parcel_data, 'Indirizzo').text = "{}".format(receiver_id.street)
            etree.SubElement(parcel_data, 'Localita').text = "{}".format(receiver_id.city)
            etree.SubElement(parcel_data, 'Zipcode').text = "{}".format(receiver_id.zip)
            etree.SubElement(parcel_data, 'Provincia').text = "{}".format(receiver_id.country_id.code)
            etree.SubElement(parcel_data, 'Bda').text = "{}".format(self.gls_packaging_id.name)
            etree.SubElement(parcel_data, 'Colli').text = "1"
            etree.SubElement(parcel_data, 'Incoterm').text = "0"
            etree.SubElement(parcel_data, 'PesoReale').text = "{}".format(bulk_weight)
            if self.gls_italy_cod:
                etree.SubElement(parcel_data, 'ImportoContrassegno').text = "{}".format(parcel_value)
            etree.SubElement(parcel_data, 'TipoPorto').text = "{}".format(self.gls_italy_port_type)
            etree.SubElement(parcel_data, 'CodiceClienteDestinatario').text = ""
            etree.SubElement(parcel_data, 'Email').text = "{}".format(receiver_id.email or " ")
            etree.SubElement(parcel_data, 'Cellulare1').text = "{}".format(receiver_id.phone.replace(' ','') or '')
            etree.SubElement(parcel_data, 'ModalitaIncasso').text = "{}".format(self.gls_italy_modalitaIncasso)
            etree.SubElement(parcel_data, 'DataPrenotazioneGDO').text = ""
            etree.SubElement(parcel_data, 'OrarioNoteGDO').text = ""
            etree.SubElement(parcel_data, 'GeneraPdf').text = "4"
            etree.SubElement(parcel_data, 'FormatoPdf').text = ""
            etree.SubElement(parcel_data, 'ContatoreProgressivo').text = "{}".format(time.strftime("%d%m%M%S"))
            etree.SubElement(parcel_data, 'NumDayListSped').text = ""
            etree.SubElement(parcel_data, 'IdentPIN').text = ""
            etree.SubElement(parcel_data, 'AssicurazioneIntegrativa').text = ""
            etree.SubElement(parcel_data, 'ServiziAccessori').text = "31" if self.gls_flex_delivery_service else ""
            etree.SubElement(parcel_data, 'TipoSpedizione').text = "{}".format(self.gls_italy_shipping_type)
            etree.SubElement(parcel_data, 'ValoreDichiarato').text = ""
            etree.SubElement(parcel_data, 'PersonaRiferimento').text = "{}".format(
                receiver_id.name.replace('&', '') or '')
            etree.SubElement(parcel_data, 'Contenuto').text = ""
            etree.SubElement(parcel_data, 'TelefonoDestinatario').text = "{}".format(receiver_id.phone.replace(' ','') or '')
            etree.SubElement(parcel_data, 'CategoriaMerceologica').text = ""
            etree.SubElement(parcel_data, 'FatturaDoganale').text = ""
            etree.SubElement(parcel_data, 'DataFatturaDoganale').text = ""
            etree.SubElement(parcel_data, 'PezziDichiarati').text = ""
            etree.SubElement(parcel_data, 'NazioneOrigine').text = ""
            etree.SubElement(parcel_data, 'TelefonoMittente').text = ""
            etree.SubElement(parcel_data, 'NumeroFatturaCOD').text = ""
            etree.SubElement(parcel_data, 'DataFatturaCOD').text = ""
            etree.SubElement(parcel_data, 'NoteIncoterm').text = ""
            parcel = etree.tostring(parcel_data, encoding='unicode')
            parcel_info += parcel
        data = """
                <Info>
                   <SedeGls>{0}</SedeGls>
                   <CodiceClienteGls>{1}</CodiceClienteGls>
                   <PasswordClienteGls>{2}</PasswordClienteGls>
                   {3}
                </Info>
           """.format(sede_gls, customer_code, password_gls, parcel_info)
        _logger.info(":::Request data::: {0}".format(data))
        if not self._context.get('closeworkday'):
            # __ creating main xml format for call xml api(AddParcel)
            Envelope = etree.Element("Envelope")
            Envelope.attrib['xmlns'] = 'http://www.w3.org/2003/05/soap-envelope'
            Body = etree.SubElement(Envelope, "Body")
            AddParcel = etree.SubElement(Body, "AddParcel")
            AddParcel.attrib['xmlns'] = 'https://labelservice.gls-italy.com/'
            etree.SubElement(AddParcel, "XMLInfoParcel").text = data
            return etree.tostring(Envelope)
        else:
            return data

    @api.model
    def gls_italy_send_shipping(self, pickings):
        request_data = self.gls_itlay_create_order_request_data(pickings)
        try:
            url = "{}".format(pickings.company_id and pickings.company_id.gls_italy_api_url)
            headers = {'SOAPAction': 'https://labelservice.gls-italy.com/AddParcel',
                       'Content-Type': 'application/soap+xml; charset="utf-8"'}
            _logger.info("::: sending request to {0} \n request data {1}".format(url, request_data))
            response_data = request(method="POST", url=url, headers=headers, data=request_data)
            if response_data.status_code in [200, 201]:
                _logger.info("[success] Getting Successfully response from {}".format(url))
                response_data = Response(response_data)
                result = response_data.dict()
                parcel_response = result.get('Envelope') and result.get('Envelope').get('Body') and \
                                  result.get('Envelope').get('Body').get('AddParcelResponse') and \
                                  result.get('Envelope').get('Body').get('AddParcelResponse').get('AddParcelResult') and \
                                  result.get('Envelope').get('Body').get('AddParcelResponse').get(
                                      'AddParcelResult').get('InfoLabel') and \
                                  result.get('Envelope').get('Body').get('AddParcelResponse').get(
                                      'AddParcelResult').get('InfoLabel').get('Parcel')
                if isinstance(parcel_response, dict):
                    parcel_response = [parcel_response]
                if not parcel_response:
                    raise ValidationError(result)
                shipping_number_lst = []
                for parcel_data in parcel_response:
                    shipping_number = parcel_data.get('NumeroSpedizione')
                    label_data = parcel_data.get('PdfLabel')
                    if not shipping_number and label_data:
                        raise ValidationError(_('shipping number and label data not foun in response \n response '
                                                'data {}').format(result))
                    binary_data = binascii.a2b_base64(str(label_data))
                    shipping_number_lst.append(shipping_number)
                    message = (_(
                        "Label created!<br/> <b>Shipping  Number : </b>%s<br/>") % (
                                   shipping_number,))
                    pickings.message_post(body=message, attachments=[
                        ('Label-%s.%s' % (shipping_number, "pdf"), binary_data)])
                # Start Functionality for CloseWorkDay
                closeworkday_request_data = self.with_context(
                    closeworkday=True).gls_itlay_create_order_request_data(
                    pickings)

                if closeworkday_request_data:
                    encode_data = "XMLCloseInfoParcel=%s" % urllib.parse.quote(closeworkday_request_data)

                    url = "{}/CloseWorkDay".format(pickings.company_id and pickings.company_id.gls_italy_api_url)
                    headers = {'Content-Type': 'application/x-www-form-urlencoded', }

                    response_data = requests.request(method="POST", url=url, headers=headers, data=encode_data)

                    if response_data.status_code in [200, 201, 202]:
                        _logger.info(":: get successfully response from {}".format(url))
                        response_data = Response(response_data)
                        result = response_data.dict()
                        successful_message = result.get('DescrizioneErrore')
                        if successful_message == 'OK':
                            pickings.message_post(body="CloseFor Workday API Successfully Call")
                        else:
                            raise ValidationError(_(response_data))
                    else:
                        raise ValidationError(
                            "Getting Some Error From {} \n response data {}".format(url, response_data.text))
                # End Functionality for CloseWorkDay

                shipping_data = {
                    'exact_price': 0.0,
                    'tracking_number': ",".join(shipping_number_lst)}
                response = []
                response += [shipping_data]
                return response
            else:
                raise ValidationError("Getting Some Error From {} \n response data {}".format(url, response_data.text))
        except Exception as error:
            raise ValidationError(error)

    def gls_italy_cancel_shipment(self, picking):
        """
        :return this method cancel the shipment
        """
        SedeGls = picking and picking.company_id and picking.company_id.gls_italy_sede
        CodiceClienteGls = picking and picking.company_id and picking.company_id.gls_italy_customer_code
        PasswordClienteGls = picking and picking.company_id and picking.company_id.gls_italy_password

        root_node = etree.Element('soap:Envelope')
        root_node.attrib['xmlns:soap'] = 'http://schemas.xmlsoap.org/soap/envelope/'
        root_node.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
        root_node.attrib['xmlns:xsd'] = 'http://www.w3.org/2001/XMLSchema'
        soap_body = etree.SubElement(root_node, 'soap:Body')
        DeleteSped = etree.SubElement(soap_body, 'DeleteSped')
        DeleteSped.attrib['xmlns'] = 'https://labelservice.gls-italy.com/'
        etree.SubElement(DeleteSped, 'SedeGls').text = "{}".format(SedeGls)
        etree.SubElement(DeleteSped, 'CodiceClienteGls').text = "{}".format(CodiceClienteGls)
        etree.SubElement(DeleteSped, 'PasswordClienteGls').text = "{}".format(PasswordClienteGls)
        etree.SubElement(DeleteSped, 'NumSpedizione').text = "{}".format(picking.carrier_tracking_ref)
        request_data = etree.tostring(root_node)
        try:
            url = "{}".format(picking.company_id and picking.company_id.gls_italy_api_url)
            headers = {'Content-Type': 'text/xml; charset=utf-8',
                        'SOAPAction': 'https://labelservice.gls-italy.com/DeleteSped' }
            response_data = request(method="POST", url=url,data=request_data, headers=headers)
            if response_data.status_code in [200, 201, 202]:
                _logger.info(":: get successfully response from {}".format(url))
                response_data = Response(response_data)
                _logger.info("successfully delete the shipment")
            else:
                raise ValidationError(_('getting some error from %s \n response data %s') % (url, response_data.text))
        except Exception as error:
            raise ValidationError(_(error))

    def gls_italy_get_tracking_link(self, pickings):
        url = "https://www.gls-italy.com/?option=com_gls&view=track_e_trace&mode=search&numero_spedizione=%s" % pickings.carrier_tracking_ref
        return url

