# pumplistener/management/commands/delete_old_tokens.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from pumplistener.models import Token

class Command(BaseCommand):
    help = 'Deletes token records older than 6 hours.'

    def handle(self, *args, **options):
        cutoff_time = timezone.now() - timedelta(hours=6)

        self.stdout.write(f"Looking for tokens created before {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}...")

        old_tokens = Token.objects.filter(timestamp__lt=cutoff_time)

        deleted_count, _ = old_tokens.delete()

        if deleted_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} old token(s).'))
        else:
            self.stdout.write(self.style.SUCCESS('No old tokens to delete.'))