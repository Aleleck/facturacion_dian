"""Generador de facturas UBL 2.1"""
from lxml import etree
from datetime import datetime
import pytz
from config import settings, NAMESPACES, DOC_TYPE_INVOICE, TAX_IVA
from core import CryptoService, CUFECalculator
from models import Party, InvoiceItem

class InvoiceGenerator:
    def __init__(self, emisor: Party):
        self.emisor = emisor
        self.timezone = pytz.timezone('America/Bogota')
        # Crear mapa de namespaces para usar con QName
        self.nsmap = NAMESPACES
    
    def generate(self, numero: int, items: list, cliente: Party) -> tuple:
        """Genera XML de factura"""
        
        # Fecha/hora actual Colombia
        now = datetime.now(self.timezone)
        fecha = now.strftime('%Y-%m-%d')
        hora = now.strftime('%H:%M:%S-05:00')
        fecha_hora = f"{fecha}T{hora}"
        
        # Calcular totales
        subtotal = sum(item.subtotal for item in items)
        iva = sum(item.iva for item in items)
        total = subtotal + iva
        
        # Formatear valores
        subtotal_str = CryptoService.format_decimal(subtotal)
        iva_str = CryptoService.format_decimal(iva)
        total_str = CryptoService.format_decimal(total)
        
        # Número de factura
        numero_factura = f"{settings.PREFIJO}{numero}"
        
        # Calcular CUFE
        cufe = CUFECalculator.calculate(
            numero_factura=numero_factura,
            fecha_factura=fecha_hora,
            valor_factura=subtotal_str,
            cod_imp_1=TAX_IVA, val_imp_1=iva_str,
            cod_imp_2='04', val_imp_2='0.00',
            cod_imp_3='03', val_imp_3='0.00',
            valor_total=total_str,
            nit_emisor=self.emisor.nit,
            nit_adquiriente=cliente.nit,
            clave_tecnica=settings.CLAVE_TECNICA,
            ambiente=settings.DIAN_AMBIENTE
        )
        
        # Crear XML con namespaces
        root = etree.Element(
            etree.QName(self.nsmap[None], 'Invoice'),
            nsmap=self.nsmap
        )
        
        # Elementos básicos
        self._add(root, 'cbc', 'UBLVersionID', 'UBL 2.1')
        self._add(root, 'cbc', 'CustomizationID', '10')
        self._add(root, 'cbc', 'ProfileID', 'DIAN 2.1')
        self._add(root, 'cbc', 'ProfileExecutionID', settings.DIAN_AMBIENTE)
        self._add(root, 'cbc', 'ID', numero_factura)
        self._add(root, 'cbc', 'UUID', cufe, {'schemeName': 'CUFE-SHA384'})
        self._add(root, 'cbc', 'IssueDate', fecha)
        self._add(root, 'cbc', 'IssueTime', hora)
        self._add(root, 'cbc', 'InvoiceTypeCode', DOC_TYPE_INVOICE)
        self._add(root, 'cbc', 'DocumentCurrencyCode', 'COP')
        self._add(root, 'cbc', 'LineCountNumeric', str(len(items)))
        
        # Emisor
        self._add_supplier(root)
        
        # Cliente
        self._add_customer(root, cliente)
        
        # Totales
        self._add_totals(root, subtotal_str, iva_str, total_str)
        
        # Líneas
        for idx, item in enumerate(items, 1):
            self._add_line(root, idx, item)
        
        xml_str = etree.tostring(root, pretty_print=True, encoding='UTF-8', xml_declaration=True)
        
        return (f"{numero_factura}.xml", xml_str, cufe)
    
    def _add(self, parent, ns_prefix, tag_name, text=None, attrib=None):
        """Agrega elemento con namespace correcto"""
        qname = etree.QName(self.nsmap[ns_prefix], tag_name)
        elem = etree.SubElement(parent, qname, attrib=attrib or {})
        if text:
            elem.text = str(text)
        return elem
    
    def _add_supplier(self, root):
        supplier = self._add(root, 'cac', 'AccountingSupplierParty')
        party = self._add(supplier, 'cac', 'Party')
        
        # ID
        pid = self._add(party, 'cac', 'PartyIdentification')
        self._add(pid, 'cbc', 'ID', self.emisor.nit, {
            'schemeID': '31', 'schemeName': '31'
        })
        
        # Nombre
        pname = self._add(party, 'cac', 'PartyName')
        self._add(pname, 'cbc', 'Name', self.emisor.razon_social)
        
        # Dirección
        addr = self._add(party, 'cac', 'PhysicalLocation')
        address = self._add(addr, 'cac', 'Address')
        self._add(address, 'cbc', 'CityName', self.emisor.ciudad)
        self._add(address, 'cbc', 'CountrySubentity', self.emisor.departamento)
        self._add(address, 'cbc', 'CountrySubentityCode', self.emisor.codigo_municipio)
        country = self._add(address, 'cac', 'Country')
        self._add(country, 'cbc', 'IdentificationCode', self.emisor.pais)
        
        # Tax
        tax = self._add(party, 'cac', 'PartyTaxScheme')
        self._add(tax, 'cbc', 'RegistrationName', self.emisor.razon_social)
        self._add(tax, 'cbc', 'CompanyID', self.emisor.nit, {
            'schemeID': '31', 'schemeName': '31'
        })
        scheme = self._add(tax, 'cac', 'TaxScheme')
        self._add(scheme, 'cbc', 'ID', '01')
        self._add(scheme, 'cbc', 'Name', 'IVA')
        
        # Legal
        legal = self._add(party, 'cac', 'PartyLegalEntity')
        self._add(legal, 'cbc', 'RegistrationName', self.emisor.razon_social)
        self._add(legal, 'cbc', 'CompanyID', self.emisor.nit, {
            'schemeID': '31', 'schemeName': '31'
        })
    
    def _add_customer(self, root, cliente):
        customer = self._add(root, 'cac', 'AccountingCustomerParty')
        party = self._add(customer, 'cac', 'Party')
        
        pid = self._add(party, 'cac', 'PartyIdentification')
        self._add(pid, 'cbc', 'ID', cliente.nit, {
            'schemeID': '31', 'schemeName': '31'
        })
        
        pname = self._add(party, 'cac', 'PartyName')
        self._add(pname, 'cbc', 'Name', cliente.razon_social)
    
    def _add_totals(self, root, subtotal, iva, total):
        monetary = self._add(root, 'cac', 'LegalMonetaryTotal')
        self._add(monetary, 'cbc', 'LineExtensionAmount', subtotal, {'currencyID': 'COP'})
        self._add(monetary, 'cbc', 'TaxExclusiveAmount', subtotal, {'currencyID': 'COP'})
        self._add(monetary, 'cbc', 'TaxInclusiveAmount', total, {'currencyID': 'COP'})
        self._add(monetary, 'cbc', 'PayableAmount', total, {'currencyID': 'COP'})
    
    def _add_line(self, root, num, item):
        line = self._add(root, 'cac', 'InvoiceLine')
        self._add(line, 'cbc', 'ID', str(num))
        self._add(line, 'cbc', 'InvoicedQuantity', f"{item.cantidad:.2f}", {
            'unitCode': item.unidad_medida
        })
        self._add(line, 'cbc', 'LineExtensionAmount', f"{item.subtotal:.2f}", {
            'currencyID': 'COP'
        })
        
        item_elem = self._add(line, 'cac', 'Item')
        self._add(item_elem, 'cbc', 'Description', item.descripcion)
        
        price = self._add(line, 'cac', 'Price')
        self._add(price, 'cbc', 'PriceAmount', f"{item.precio_unitario:.2f}", {
            'currencyID': 'COP'
        })