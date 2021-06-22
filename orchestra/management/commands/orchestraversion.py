from django.core.management.base import BaseCommand

from orchestra import get_version


class Command(BaseCommand):
    help = 'Shows django-orchestra version'

    def handle(self, *args, **options):
        self.stdout.write(get_version())
