"""Servicios criptográficos para DIAN"""
import hashlib

class CryptoService:
    @staticmethod
    def sha384(data: str) -> str:
        """Calcula SHA-384 de una cadena"""
        return hashlib.sha384(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def software_security_code(software_id: str, pin: str) -> str:
        """Calcula Software Security Code = SHA-384(SoftwareID + PIN)"""
        return CryptoService.sha384(f"{software_id}{pin}")
    
    @staticmethod
    def format_decimal(value: float, decimals: int = 2) -> str:
        """Formatea valor decimal sin separadores de miles"""
        return f"{value:.{decimals}f}"