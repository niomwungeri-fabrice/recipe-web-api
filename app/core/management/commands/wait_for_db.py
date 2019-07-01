import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **operations):
        self.stdout.write('Waiting for db to be available...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('DB not available, waiting for 1 second')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!!'))
