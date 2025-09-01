# # pumplistener/management/commands/delete_old_tokens.py

# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from datetime import timedelta
# from pumplistener.models import Token

# class Command(BaseCommand):
#     help = 'Deletes token records older than 6 hours.'

#     def handle(self, *args, **options):
#         # cutoff_time = timezone.now() - timedelta(hours=6)
#         cutoff_time = timezone.now() - timedelta(minutes=15)

#         self.stdout.write(f"Looking for tokens created before {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}...")

#         old_tokens = Token.objects.filter(timestamp__lt=cutoff_time)

#         deleted_count, _ = old_tokens.delete()

#         if deleted_count > 0:
#             self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} old token(s).'))
#         else:
#             self.stdout.write(self.style.SUCCESS('No old tokens to delete.'))


#############################################################################################################################

# pumplistener/management/commands/delete_old_tokens.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from pumplistener.models import Token
# --- ADD THESE IMPORTS ---
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import os
# --- END IMPORTS ---

class Command(BaseCommand):
    help = 'Emails a report of all tokens, then deletes records older than a set duration.'

    def handle(self, *args, **options):
        # --- PART 1: SEND THE EMAIL REPORT ---
        self.stdout.write("Fetching all tokens for the report...")
        # ... (The entire email sending part remains exactly the same) ...
        all_tokens = Token.objects.order_by('-timestamp')
        recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
        
        if all_tokens.exists() and recipient_email:
            report_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')
            html_message = render_to_string('pumplistener/email_report.html', {
                'tokens': all_tokens,
                'report_time': report_time_str
            })
            subject = f"Pump.fun Token Report - {report_time_str}"
            try:
                send_mail(
                    subject,
                    "Please view this email in an HTML-compatible client.",
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],
                    html_message=html_message
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully sent report to {recipient_email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send email: {e}'))
        else:
            self.stdout.write("No tokens to report or no recipient email configured.")

        # --- PART 2: DELETE OLD TOKENS (WITH CORRECTED TIME LOGIC) ---
        
        # Manually calculate the current naive IST time, just like in the listener
        current_ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        
        # Set your desired duration (e.g., 2 hours)
        cutoff_duration = timedelta(hours=4)
        # cutoff_duration = timedelta(minutes=30)
        
        # Calculate the cutoff time based on the correct IST time
        cutoff_time = current_ist_time - cutoff_duration
        
        self.stdout.write(f"Looking for tokens created before {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}...")
        
        old_tokens = Token.objects.filter(timestamp__lt=cutoff_time)
        deleted_count, _ = old_tokens.delete()
        
        if deleted_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} old token(s).'))
        else:
            self.stdout.write(self.style.SUCCESS('No old tokens to delete.'))