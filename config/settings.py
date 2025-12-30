"""Configuración del Sistema de Facturación Electrónica DIAN"""
import os
from pathlib import Path

# Comentamos dotenv por ahora
# from dotenv import load_dotenv
# load_dotenv()

class Settings:
    """Configuración centralizada del sistema"""
    
    # DIAN
    DIAN_AMBIENTE = '2'
    DIAN_WSDL = 'https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc?wsdl'
    TEST_SET_ID = 'e6c413bf-66b6-4dd3-9dbe-4c7470c01b85'
    
    # SOFTWARE
    SOFTWARE_ID = 'efb494db-8d4a-4114-aa35-618269a07312'
    SOFTWARE_PIN = '12026'
    CLAVE_TECNICA = 'fc8eac422eba16e22ffd8c6f94b3f40a6e38162c'
    
    # NUMERACIÓN
    PREFIJO = 'SETP'
    NUMERO_AUTORIZACION = '18760000001'
    RANGO_DESDE = 990000000
    RANGO_HASTA = 995000000
    
    # EMISOR
    NIT_EMISOR = '35696051'
    DV_EMISOR = '1'
    RAZON_SOCIAL = 'FLOR MARIA PINEDA CASAMA'
    TIPO_PERSONA = 'NATURAL'
    TIPO_REGIMEN = '49'
    
    # Dirección
    DIRECCION = 'Cr 57 # 83 D - 35'
    CIUDAD = 'Medellín'
    DEPARTAMENTO = 'Antioquia'
    CODIGO_MUNICIPIO = '05001'
    PAIS = 'CO'
    TELEFONO = '+573104502683'
    EMAIL = 'autoserviciomoravia@hotmail.es'
    
    # CERTIFICADO
    CERT_PATH = './data/certificado.crt'
    CERT_PASSWORD = 'Ale1331213312*'
    
    # RUTAS
    BASE_DIR = Path(__file__).resolve().parent.parent
    OUTPUT_DIR = BASE_DIR / 'output'

settings = Settings()