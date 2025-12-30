"""Modelo de producto/servicio"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class InvoiceItem:
    codigo: str
    descripcion: str
    cantidad: float
    precio_unitario: float
    unidad_medida: str = 'EA'
    gtin: Optional[str] = None
    tarifa_iva: float = 0.19
    
    @property
    def subtotal(self) -> float:
        return self.cantidad * self.precio_unitario
    
    @property
    def iva(self) -> float:
        return self.subtotal * self.tarifa_iva
    
    @property
    def total(self) -> float:
        return self.subtotal + self.iva