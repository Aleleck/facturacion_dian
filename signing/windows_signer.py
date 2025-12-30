"""
Firmador XAdES-EPES usando certificado del almacén de Windows
Versión corregida con API correcta de win32crypt
"""
from lxml import etree
from pathlib import Path
import hashlib
import base64
from datetime import datetime
import uuid
import subprocess
import tempfile
import os

class WindowsCertSigner:
    def __init__(self, cert_thumbprint: str):
        """
        Args:
            cert_thumbprint: Huella digital SHA1 del certificado (sin espacios)
                            Ejemplo: "bfb07d309f71a917da837ea0fb36b91b92cf0022"
        """
        self.thumbprint = cert_thumbprint.replace(" ", "").replace(":", "").upper()
        print(f"Buscando certificado: {self.thumbprint}")
        self._verify_certificate()
    
    def _verify_certificate(self):
        """Verifica que el certificado existe usando PowerShell"""
        ps_script = f'''
$cert = Get-ChildItem -Path Cert:\\CurrentUser\\My | Where-Object {{$_.Thumbprint -eq "{self.thumbprint}"}}
if ($cert) {{
    Write-Output "FOUND:$($cert.Subject)"
}} else {{
    Write-Output "NOT_FOUND"
}}
'''
        try:
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout.strip()
            
            if output.startswith("FOUND:"):
                subject = output.replace("FOUND:", "")
                print(f"✓ Certificado encontrado: {subject}")
            else:
                raise Exception(f"Certificado con huella {self.thumbprint} no encontrado en el almacén")
                
        except Exception as e:
            print(f"✗ Error al verificar certificado: {e}")
            raise
    
    def _sign_data_with_powershell(self, data_path: str, output_path: str) -> bool:
        """Firma datos usando PowerShell y el certificado de Windows"""
        
        ps_script = f'''
$cert = Get-ChildItem -Path Cert:\\CurrentUser\\My | Where-Object {{$_.Thumbprint -eq "{self.thumbprint}"}}

if (-not $cert) {{
    Write-Error "Certificado no encontrado"
    exit 1
}}

# Leer datos a firmar
$data = [System.IO.File]::ReadAllBytes("{data_path}")

# Crear objeto de firma
$contentInfo = New-Object System.Security.Cryptography.Pkcs.ContentInfo -ArgumentList (,$data)
$signedCms = New-Object System.Security.Cryptography.Pkcs.SignedCms $contentInfo, $false

# Crear firmante
$signer = New-Object System.Security.Cryptography.Pkcs.CmsSigner $cert

# Firmar
try {{
    $signedCms.ComputeSignature($signer)
    $signature = $signedCms.Encode()
    [System.IO.File]::WriteAllBytes("{output_path}", $signature)
    Write-Output "SUCCESS"
}} catch {{
    Write-Error $_.Exception.Message
    exit 1
}}
'''
        try:
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True
            )
            
            return "SUCCESS" in result.stdout
            
        except Exception as e:
            print(f"Error al firmar con PowerShell: {e}")
            return False
    
    def sign_xml(self, xml_path: str, output_path: str) -> bool:
        """
        Firma un XML con estructura XAdES-EPES básica usando PowerShell
        
        Args:
            xml_path: Ruta del XML a firmar
            output_path: Ruta donde guardar el XML firmado
        
        Returns:
            bool: True si la firma fue exitosa
        """
        try:
            # Cargar XML
            tree = etree.parse(xml_path)
            root = tree.getroot()
            
            # Obtener UUID del documento (CUFE/CUDE)
            ns = {'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'}
            uuid_elem = root.find('.//cbc:UUID', namespaces=ns)
            document_id = uuid_elem.text if uuid_elem is not None else str(uuid.uuid4())
            
            # Canonicalizar el XML (C14N)
            canonical_xml = etree.tostring(root, method='c14n', exclusive=False)
            
            # Calcular digest (hash) del documento
            digest = hashlib.sha256(canonical_xml).digest()
            digest_b64 = base64.b64encode(digest).decode('utf-8')
            
            # Crear archivo temporal con los datos a firmar
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.dat') as tmp_in:
                tmp_in.write(canonical_xml)
                tmp_in_path = tmp_in.name
            
            # Archivo temporal para la firma
            tmp_out_path = tmp_in_path + '.sig'
            
            # Firmar usando PowerShell
            if not self._sign_data_with_powershell(tmp_in_path, tmp_out_path):
                raise Exception("Error al generar la firma con PowerShell")
            
            # Leer firma generada
            with open(tmp_out_path, 'rb') as f:
                signature_bytes = f.read()
            
            signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
            
            # Limpiar archivos temporales
            os.unlink(tmp_in_path)
            os.unlink(tmp_out_path)
            
            # Obtener certificado en base64
            cert_data = self._get_certificate_base64()
            if not cert_data:
                raise Exception("Error al obtener datos del certificado")
            
            # Crear estructura de firma XAdES-EPES
            self._add_signature_to_xml(
                root,
                document_id,
                digest_b64,
                signature_b64,
                cert_data
            )
            
            # Guardar XML firmado
            tree.write(
                output_path,
                pretty_print=True,
                xml_declaration=True,
                encoding='UTF-8'
            )
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_certificate_base64(self) -> str:
        """Obtiene el certificado en formato base64 usando PowerShell"""
        ps_script = f'''
$cert = Get-ChildItem -Path Cert:\\CurrentUser\\My | Where-Object {{$_.Thumbprint -eq "{self.thumbprint}"}}
if ($cert) {{
    $base64 = [Convert]::ToBase64String($cert.RawData)
    Write-Output $base64
}}
'''
        try:
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout.strip()
            
        except Exception as e:
            print(f"Error al obtener certificado: {e}")
            return None
    
    def _add_signature_to_xml(self, root, doc_id, digest, signature, cert_data):
        """Agrega el nodo de firma XAdES-EPES al XML"""
        
        # Namespaces
        ns_ds = 'http://www.w3.org/2000/09/xmldsig#'
        ns_ext = 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
        ns_xades = 'http://uri.etsi.org/01903/v1.3.2#'
        
        # Buscar o crear UBLExtensions
        ext_elem = root.find(f'{{{ns_ext}}}UBLExtensions')
        if ext_elem is None:
            ext_elem = etree.Element(f'{{{ns_ext}}}UBLExtensions')
            root.insert(0, ext_elem)
        
        # Crear UBLExtension para la firma
        ubl_ext = etree.SubElement(ext_elem, f'{{{ns_ext}}}UBLExtension')
        ext_content = etree.SubElement(ubl_ext, f'{{{ns_ext}}}ExtensionContent')
        
        # Signature
        sig = etree.SubElement(ext_content, f'{{{ns_ds}}}Signature', attrib={'Id': 'xmldsig-signature'})
        
        # SignedInfo
        signed_info = etree.SubElement(sig, f'{{{ns_ds}}}SignedInfo')
        
        # CanonicalizationMethod
        etree.SubElement(
            signed_info,
            f'{{{ns_ds}}}CanonicalizationMethod',
            attrib={'Algorithm': 'http://www.w3.org/TR/2001/REC-xml-c14n-20010315'}
        )
        
        # SignatureMethod
        etree.SubElement(
            signed_info,
            f'{{{ns_ds}}}SignatureMethod',
            attrib={'Algorithm': 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'}
        )
        
        # Reference al documento
        ref = etree.SubElement(
            signed_info,
            f'{{{ns_ds}}}Reference',
            attrib={'Id': f'xmldsig-ref-{doc_id}', 'URI': ''}
        )
        
        # Transforms
        transforms = etree.SubElement(ref, f'{{{ns_ds}}}Transforms')
        etree.SubElement(
            transforms,
            f'{{{ns_ds}}}Transform',
            attrib={'Algorithm': 'http://www.w3.org/2000/09/xmldsig#enveloped-signature'}
        )
        
        # DigestMethod
        etree.SubElement(
            ref,
            f'{{{ns_ds}}}DigestMethod',
            attrib={'Algorithm': 'http://www.w3.org/2001/04/xmlenc#sha256'}
        )
        
        # DigestValue
        digest_elem = etree.SubElement(ref, f'{{{ns_ds}}}DigestValue')
        digest_elem.text = digest
        
        # SignatureValue
        sig_value = etree.SubElement(sig, f'{{{ns_ds}}}SignatureValue', attrib={'Id': 'xmldsig-signature-value'})
        sig_value.text = signature
        
        # KeyInfo
        key_info = etree.SubElement(sig, f'{{{ns_ds}}}KeyInfo')
        x509_data = etree.SubElement(key_info, f'{{{ns_ds}}}X509Data')
        x509_cert = etree.SubElement(x509_data, f'{{{ns_ds}}}X509Certificate')
        x509_cert.text = cert_data
        
        # Object con QualifyingProperties (XAdES)
        obj = etree.SubElement(sig, f'{{{ns_ds}}}Object')
        qual_props = etree.SubElement(
            obj,
            f'{{{ns_xades}}}QualifyingProperties',
            attrib={'Target': '#xmldsig-signature'}
        )
        
        # SignedProperties
        signed_props = etree.SubElement(
            qual_props,
            f'{{{ns_xades}}}SignedProperties',
            attrib={'Id': 'xmldsig-signed-properties'}
        )
        
        # SignedSignatureProperties
        sig_props = etree.SubElement(signed_props, f'{{{ns_xades}}}SignedSignatureProperties')
        
        # SigningTime
        signing_time = etree.SubElement(sig_props, f'{{{ns_xades}}}SigningTime')
        signing_time.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def sign_all_documents(thumbprint: str, input_dir: str, output_dir: str):
    """
    Firma todos los XMLs en un directorio
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Crear instancia del firmador
    signer = WindowsCertSigner(thumbprint)
    
    # Obtener todos los XMLs
    xml_files = list(input_path.glob('*.xml'))
    total = len(xml_files)
    
    print(f"\n{'='*80}")
    print(f"FIRMANDO {total} DOCUMENTOS")
    print(f"{'='*80}\n")
    
    firmados = 0
    errores = 0
    
    for i, xml_file in enumerate(xml_files, 1):
        output_file = output_path / xml_file.name
        
        print(f"[{i}/{total}] {xml_file.name}... ", end='', flush=True)
        
        if signer.sign_xml(str(xml_file), str(output_file)):
            print("✓")
            firmados += 1
        else:
            print("✗")
            errores += 1
    
    print(f"\n{'='*80}")
    print(f"✅ RESUMEN:")
    print(f"   Total: {total}")
    print(f"   Firmados: {firmados}")
    print(f"   Errores: {errores}")
    print(f"{'='*80}\n")
    print(f"📁 XMLs firmados en: {output_path}")


if __name__ == '__main__':
    # Huella digital del certificado (en MAYÚSCULAS)
    THUMBPRINT = "BFB07D309F71A917DA837EA0FB36B91B92CF0022"
    
    # Firmar todos los documentos
    sign_all_documents(
        thumbprint=THUMBPRINT,
        input_dir='output/xml',
        output_dir='output/signed'
    )