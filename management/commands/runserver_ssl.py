from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand
from django.core.management.base import CommandError
import os
import ssl

class Command(RunserverCommand):
    help = 'Runs Django development server with SSL/TLS enabled'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--cert',
            default='/home/mo_vee/Documents/Development/Python/web_development/rep_app/cert.crt',
            help='Path to SSL certificate file (.crt)'
        )
        parser.add_argument(
            '--key',
            default='/home/mo_vee/Documents/Development/Python/web_development/rep_app/key.pem',
            help='Path to SSL key file (.pem)'
        )

    def handle(self, *args, **options):
        if not os.path.exists(options['cert']):
            raise CommandError(f'Certificate file not found: {options["cert"]}')
        if not os.path.exists(options['key']):
            raise CommandError(f'Private key file not found: {options["key"]}')

        # Enable HTTPS
        os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
        os.environ['HTTPS'] = 'on'

        # Create SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            ssl_context.load_cert_chain(
                certfile=options['cert'],
                keyfile=options['key']
            )
        except ssl.SSLError as e:
            raise CommandError(f'SSL error: {str(e)}')
        
        # Add SSL context to options
        options['ssl_context'] = ssl_context
        
        return super().handle(*args, **options)