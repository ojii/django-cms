from cms.models import Page
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import NoArgsCommand
from django.db import DatabaseError
import os

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        try:
            Page.objects.all().count()
            self.update()
        except DatabaseError:
            self.setup()
            
    def setup(self):
        call_command('syncdb', migrate_all=True, interactive=False)
        call_command('migrate', fake=True)
        call_command('symlinkmedia')
        call_command('loaddata', os.path.join(settings.PROJECT_DIR, 'fixtures/simple.json'))
        
    def update(self):
        call_command('syncdb')
        call_command('migrate')
        call_command('symlinkmedia')