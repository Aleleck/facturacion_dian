"""Crea ZIP con documentos firmados para enviar a DIAN"""
import zipfile
from pathlib import Path
from config import settings

def create_signed_zip():
    signed_dir = Path('output/signed')
    zip_dir = Path('output/zip')
    zip_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = zip_dir / f"{settings.TEST_SET_ID}_firmado.zip"
    
    print("\n=== CREANDO ZIP CON DOCUMENTOS FIRMADOS ===\n")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        xml_files = list(signed_dir.glob('*.xml'))
        
        for xml_file in sorted(xml_files):
            zipf.write(xml_file, xml_file.name)
            print(f"  + {xml_file.name}")
    
    size_kb = zip_path.stat().st_size / 1024
    
    print(f"\n✓ ZIP creado: {zip_path}")
    print(f"  Tamaño: {size_kb:.2f} KB")
    print(f"\n🎯 Listo para subir a DIAN")
    
    return zip_path

if __name__ == '__main__':
    create_signed_zip()
    