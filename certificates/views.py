from django.shortcuts import render
from django.http import HttpResponse
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization
import datetime
import zipfile
import io

def home(request):
    
    if request.method == 'POST':
        state = request.POST.get('state')
        organization = request.POST.get('organization')
        locality = request.POST.get('locality')
        country = request.POST.get('country')
        common_name = request.POST.get('common_name')
        
        """
        Generates a new RSA private key using the rsa.generate_private_key() function 
        from the cryptography.hazmat.primitives.asymmetric.rsa module
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Export the private key as PEM format string
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Subject
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        # Create a new X.509 certificate
        issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, 'GH'),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'Accra'),
            x509.NameAttribute(NameOID.LOCALITY_NAME, 'University of Ghan, Legon'),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Group 20'),
            x509.NameAttribute(NameOID.COMMON_NAME, 'www.group20/x509_certificate.com'),
        ])
        
        """
        creates an X.509 certificate using the x509.CertificateBuilder() class from the 
        cryptography.x509 module
        """
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).sign(private_key, hashes.SHA256(), default_backend())

        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="certificate_and_key.zip"'
        
        """
        certificate.crt, certificate.pem and key.pem compressed into a single file
        """
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr('certificate.crt', cert.public_bytes(serialization.Encoding.PEM))
            zip_file.writestr('certificate.pem', cert.public_bytes(serialization.Encoding.PEM))
            zip_file.writestr('key.pem', private_key_pem)
        
        # Set the ZIP archive as the response content
        response.write(zip_buffer.getvalue())

        return response
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')
    