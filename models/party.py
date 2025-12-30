"""Modelo de Emisor/Adquiriente"""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Party:
    nit: str
    dv: str
    razon_social: str
    tipo_persona: str = 'NATURAL'  # NATURAL, JURIDICA
    tipo_regimen: str = '49'
    responsabilidades: List[str] = None
    direccion: str = ''
    ciudad: str = ''
    departamento: str = ''
    codigo_municipio: str = ''
    pais: str = 'CO'
    telefono: str = ''
    email: str = ''
    
    def __post_init__(self):
        if self.responsabilidades is None:
            self.responsabilidades = ['O-13']