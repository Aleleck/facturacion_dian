"""Script principal para generar facturas de prueba"""
import json
from pathlib import Path
from config import settings
from models import Party, InvoiceItem
from generators import InvoiceGenerator
import zipfile

def cargar_emisor():
    return Party(
        nit=settings.NIT_EMISOR,
        dv=settings.DV_EMISOR,
        razon_social=settings.RAZON_SOCIAL,
        tipo_persona='NATURAL',
        tipo_regimen=settings.TIPO_REGIMEN,
        responsabilidades=['O-13', 'O-15'],
        direccion=settings.DIRECCION,
        ciudad=settings.CIUDAD,
        departamento=settings.DEPARTAMENTO,
        codigo_municipio=settings.CODIGO_MUNICIPIO,
        email=settings.EMAIL
    )

def cargar_clientes():
    with open('data/clientes.json') as f:
        data = json.load(f)
    return [Party(**c) for c in data]

def cargar_productos():
    return [
        InvoiceItem('P001', 'Arroz Diana 500g', 2, 2500, tarifa_iva=0.19),
        InvoiceItem('P002', 'Aceite Gourmet 1L', 1, 8900, tarifa_iva=0.19),
        InvoiceItem('P003', 'Azúcar 1kg', 3, 3200, tarifa_iva=0.05),
    ]

def generar_facturas(cantidad=30):
    """Genera facturas de venta"""
    emisor = cargar_emisor()
    clientes = cargar_clientes()
    productos = cargar_productos()
    
    gen = InvoiceGenerator(emisor)
    
    Path('output/xml').mkdir(parents=True, exist_ok=True)
    
    facturas = []
    for i in range(cantidad):
        numero = settings.RANGO_DESDE + i
        cliente = clientes[i % len(clientes)]
        items = productos
        
        filename, xml, cufe = gen.generate(numero, items, cliente)
        
        # Guardar XML
        with open(f'output/xml/{filename}', 'wb') as f:
            f.write(xml)
        
        facturas.append(filename)
        print(f"✓ {filename} - CUFE: {cufe[:20]}...")
    
    print(f"\n✓ {cantidad} facturas generadas en output/xml/")
    return facturas

def generar_notas_credito(cantidad=10, inicio=30):
    """Genera notas crédito"""
    print("\n=== GENERANDO NOTAS CRÉDITO ===")
    emisor = cargar_emisor()
    clientes = cargar_clientes()
    productos = cargar_productos()
    
    gen = InvoiceGenerator(emisor)
    
    notas = []
    for i in range(cantidad):
        numero = settings.RANGO_DESDE + inicio + i
        cliente = clientes[i % len(clientes)]
        # Para NC, usamos menos cantidad (devolución parcial)
        items = [InvoiceItem('P001', 'Devolución Arroz Diana 500g', 1, 2500, tarifa_iva=0.19)]
        
        filename, xml, cufe = gen.generate(numero, items, cliente)
        
        # Cambiar prefijo a NC en el nombre del archivo
        filename_nc = filename.replace('.xml', '_NC.xml')
        
        with open(f'output/xml/{filename_nc}', 'wb') as f:
            f.write(xml)
        
        notas.append(filename_nc)
        print(f"✓ {filename_nc} - CUDE: {cufe[:20]}...")
    
    print(f"\n✓ {cantidad} notas crédito generadas")
    return notas

def crear_zip_envio():
    """Crea el ZIP con todos los documentos para enviar a DIAN"""
    print("\n=== CREANDO ARCHIVO ZIP ===")
    
    Path('output/zip').mkdir(parents=True, exist_ok=True)
    
    zip_path = f'output/zip/{settings.TEST_SET_ID}.zip'
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Agregar todos los XMLs
        xml_dir = Path('output/xml')
        for xml_file in xml_dir.glob('*.xml'):
            zipf.write(xml_file, xml_file.name)
            print(f"  + {xml_file.name}")
    
    print(f"\n✓ ZIP creado: {zip_path}")
    print(f"  Tamaño: {Path(zip_path).stat().st_size / 1024:.2f} KB")
    
    return zip_path

def generar_notas_debito(cantidad=10, inicio=40):
    """Genera notas débito"""
    print("\n=== GENERANDO NOTAS DÉBITO ===")
    emisor = cargar_emisor()
    clientes = cargar_clientes()
    
    gen = InvoiceGenerator(emisor)
    
    notas = []
    for i in range(cantidad):
        numero = settings.RANGO_DESDE + inicio + i
        cliente = clientes[i % len(clientes)]
        # Para ND, agregamos intereses o ajustes
        items = [InvoiceItem('ND001', 'Intereses de mora', 1, 5000, tarifa_iva=0.19)]
        
        filename, xml, cufe = gen.generate(numero, items, cliente)
        
        # Cambiar prefijo a ND en el nombre del archivo
        filename_nd = filename.replace('.xml', '_ND.xml')
        
        with open(f'output/xml/{filename_nd}', 'wb') as f:
            f.write(xml)
        
        notas.append(filename_nd)
        print(f"✓ {filename_nd} - CUDE: {cufe[:20]}...")
    
    print(f"\n✓ {cantidad} notas débito generadas")
    return notas

if __name__ == '__main__':
    print("=" * 80)
    print("SISTEMA DE FACTURACIÓN ELECTRÓNICA DIAN")
    print("=" * 80)
    print(f"Emisor: {settings.NIT_EMISOR} - {settings.RAZON_SOCIAL}")
    print(f"Rango: {settings.PREFIJO}{settings.RANGO_DESDE} - {settings.RANGO_HASTA}")
    print("=" * 80)
    print()
    
    # Generar los 50 documentos requeridos
    facturas = generar_facturas(30)
    notas_credito = generar_notas_credito(10)
    notas_debito = generar_notas_debito(10)
    
    total = len(facturas) + len(notas_credito) + len(notas_debito)

    print("\n" + "=" * 80)
    print(f"✅ RESUMEN: {total} documentos generados")
    print(f"   - 30 Facturas de Venta")
    print(f"   - 10 Notas Crédito")
    print(f"   - 10 Notas Débito")
    print("=" * 80)
    print("\n📁 Todos los archivos están en: output/xml/")

    # Crear ZIP
    zip_path = crear_zip_envio()
    
    print("\n" + "=" * 80)
    print("🎯 SIGUIENTE PASO:")
    print("   1. Verificar los XMLs generados")
    print("   2. Firmar los documentos con tu certificado")
    print(f"   3. Subir {zip_path} al portal de la DIAN")
    print("=" * 80)

