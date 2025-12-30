"""Calculadora de CUFE/CUDE según especificación DIAN"""
from .crypto import CryptoService

class CUFECalculator:
    @staticmethod
    def calculate(
        numero_factura: str,
        fecha_factura: str,
        valor_factura: str,
        cod_imp_1: str, val_imp_1: str,
        cod_imp_2: str, val_imp_2: str,
        cod_imp_3: str, val_imp_3: str,
        valor_total: str,
        nit_emisor: str,
        nit_adquiriente: str,
        clave_tecnica: str,
        ambiente: str
    ) -> str:
        """Calcula CUFE según fórmula DIAN"""
        cufe_string = (
            f"{numero_factura}"
            f"{fecha_factura}"
            f"{valor_factura}"
            f"{cod_imp_1}{val_imp_1}"
            f"{cod_imp_2}{val_imp_2}"
            f"{cod_imp_3}{val_imp_3}"
            f"{valor_total}"
            f"{nit_emisor}"
            f"{nit_adquiriente}"
            f"{clave_tecnica}"
            f"{ambiente}"
        )
        return CryptoService.sha384(cufe_string)