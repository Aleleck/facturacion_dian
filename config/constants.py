"""Constantes para facturación electrónica DIAN"""

# Namespaces UBL 2.1
NAMESPACES = {
    None: 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
    'xades': 'http://uri.etsi.org/01903/v1.3.2#',
    'xades141': 'http://uri.etsi.org/01903/v1.4.1#',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'ds': 'http://www.w3.org/2000/09/xmldsig#'
}

# Tipos de documento
DOC_TYPE_INVOICE = '01'
DOC_TYPE_CREDIT_NOTE = '91'
DOC_TYPE_DEBIT_NOTE = '92'

# Códigos de impuestos
TAX_IVA = '01'
TAX_INC = '04'
TAX_ICA = '03'

# Tarifas de IVA
IVA_0 = 0.00
IVA_5 = 0.05
IVA_19 = 0.19

# Unidades de medida
UNIT_EA = 'EA'   # Unidad
UNIT_KG = 'KGM'  # Kilogramo
UNIT_LT = 'LTR'  # Litro

# Tipos de identificación
ID_NIT = '31'
ID_CC = '13'
ID_CE = '22'
ID_TI = '11'