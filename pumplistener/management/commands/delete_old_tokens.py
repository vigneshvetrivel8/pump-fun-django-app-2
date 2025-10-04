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

# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from datetime import timedelta, datetime
# from pumplistener.models import Token
# # --- ADD THESE IMPORTS ---
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
# import os
# # --- END IMPORTS ---

# class Command(BaseCommand):
#     help = 'Emails a report of all tokens, then deletes records older than a set duration.'

#     def handle(self, *args, **options):
#         # --- PART 1: SEND THE EMAIL REPORT ---
#         self.stdout.write("Fetching all tokens for the report...")
#         # ... (The entire email sending part remains exactly the same) ...
#         # all_tokens = Token.objects.order_by('-timestamp')
#         #############################################################################################################
#         # all_tokens = Token.objects.prefetch_related('data_points').order_by('-timestamp')
#         # recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
        
#         # if all_tokens.exists() and recipient_email:
#         #     # report_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')
#         #     report_time_str = datetime.utcnow() + timedelta(hours=5, minutes=30)
#         #     html_message = render_to_string('pumplistener/email_report.html', {
#         #         'tokens': all_tokens,
#         #         'report_time': report_time_str
#         #     })
        
#         ###############################################################################################################
#         # --- NEW: Define a time window for the report (e.g., last 15 minutes) ---
#         report_window = timezone.now() - timedelta(minutes=15)
#         self.stdout.write(f"Fetching tokens created since {report_window} for the report...")

#         # --- MODIFIED: Filter tokens to only include recent ones ---
#         recent_tokens = Token.objects.filter(timestamp__gte=report_window).prefetch_related('data_points').order_by('-timestamp')
#         recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
        
#         if recent_tokens.exists() and recipient_email:
#             report_time_str = datetime.utcnow() + timedelta(hours=5, minutes=30)
#             html_message = render_to_string('pumplistener/email_report.html', {
#                 'tokens': recent_tokens, # <-- Use the filtered list of recent tokens
#                 'report_time': report_time_str
#             })
#             subject = f"Pump.fun Token Report - {report_time_str}"
#             try:
#                 send_mail(
#                     subject,
#                     "Please view this email in an HTML-compatible client.",
#                     settings.DEFAULT_FROM_EMAIL,
#                     [recipient_email],
#                     html_message=html_message
#                 )
#                 self.stdout.write(self.style.SUCCESS(f'Successfully sent report to {recipient_email}'))
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f'Failed to send email: {e}'))
#         else:
#             self.stdout.write("No tokens to report or no recipient email configured.")

#         # --- PART 2: DELETE OLD TOKENS (WITH CORRECTED TIME LOGIC) ---
        
#         # Manually calculate the current naive IST time, just like in the listener
#         current_ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        
#         # Set your desired duration (e.g., 2 hours)
#         # cutoff_duration = timedelta(hours=4)
#         cutoff_duration = timedelta(minutes=15)
#         # cutoff_duration = timedelta(hours=2)
        
#         # Calculate the cutoff time based on the correct IST time
#         cutoff_time = current_ist_time - cutoff_duration
        
#         self.stdout.write(f"Looking for tokens created before {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}...")
        
#         old_tokens = Token.objects.filter(timestamp__lt=cutoff_time)
#         deleted_count, _ = old_tokens.delete()
        
#         if deleted_count > 0:
#             self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} old token(s).'))
#         else:
#             self.stdout.write(self.style.SUCCESS('No old tokens to delete.'))


##########################################################################################################################################

# pumplistener/management/commands/delete_old_tokens.py

# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from datetime import timedelta, datetime
# from pumplistener.models import Token
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
# import os

# class Command(BaseCommand):
#     help = 'Emails a report of recent tokens, then deletes old, INACTIVE records.'

#     def handle(self, *args, **options):
#         # --- PART 1: SEND THE EMAIL REPORT (No changes here) ---
#         report_window = timezone.now() - timedelta(minutes=15)
#         self.stdout.write(f"Fetching tokens created since {report_window} for the report...")
#         recent_tokens = Token.objects.filter(timestamp__gte=report_window).prefetch_related('data_points').order_by('-timestamp')
#         recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
        
#         if recent_tokens.exists() and recipient_email:
#             report_time_str = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S IST')
#             html_message = render_to_string('pumplistener/email_report.html', {
#                 'tokens': recent_tokens,
#                 'report_time': report_time_str
#             })
#             subject = f"Pump.fun Token Report - {report_time_str}"
#             try:
#                 send_mail(
#                     subject,
#                     "Please view this email in an HTML-compatible client.",
#                     settings.DEFAULT_FROM_EMAIL,
#                     [recipient_email],
#                     html_message=html_message
#                 )
#                 self.stdout.write(self.style.SUCCESS(f'Successfully sent report to {recipient_email}'))
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f'Failed to send email: {e}'))
#         else:
#             self.stdout.write("No tokens to report or no recipient email configured.")

#         # --- PART 2: DELETE OLD TOKENS (WITH MODIFIED LOGIC) ---
        
#         # cutoff_duration = timedelta(minutes=15)
#         # cutoff_time = timezone.now() - cutoff_duration

#         current_ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
#         cutoff_duration = timedelta(minutes=15)
#         cutoff_time = current_ist_time - cutoff_duration
        
#         self.stdout.write(f"Looking for inactive tokens created before {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}...")
        
#         # #### START OF FIX ####
#         # The query now finds old tokens BUT excludes any that are from the 
#         # watchlist and are not yet marked as sold.
#         old_tokens = Token.objects.filter(
#             timestamp__lt=cutoff_time
#         ).exclude(
#             is_from_watchlist=True, 
#             is_sold=False
#         )
#         # #### END OF FIX ####
        
#         deleted_count, _ = old_tokens.delete()
        
#         if deleted_count > 0:
#             self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} old inactive token(s).'))
#         else:
#             self.stdout.write(self.style.SUCCESS('No old inactive tokens to delete.'))


########################################################################################################################################

# pumplistener/management/commands/delete_old_tokens.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from pumplistener.models import Token
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import os
from django.db.models import Q # Import Q objects for complex queries

class Command(BaseCommand):
    help = 'Emails a report of recent tokens, then deletes old, INACTIVE records.'

    def handle(self, *args, **options):
        # --- PART 1: SEND THE EMAIL REPORT (No changes here) ---
        report_window = timezone.now() - timedelta(minutes=15)
        self.stdout.write(f"Fetching tokens created since {report_window} for the report...")
        recent_tokens = Token.objects.filter(timestamp__gte=report_window).prefetch_related('data_points').order_by('-timestamp')
        recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
        
        if recent_tokens.exists() and recipient_email:
            report_time_str = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S IST')
            html_message = render_to_string('pumplistener/email_report.html', {
                'tokens': recent_tokens,
                'report_time': report_time_str
            })
            subject = f"Pump.fun Token Report - {report_time_str}"
            try:
                send_mail(
                    subject, "Please view this email in an HTML-compatible client.",
                    settings.DEFAULT_FROM_EMAIL, [recipient_email], html_message=html_message
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully sent report to {recipient_email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send email: {e}'))
        else:
            self.stdout.write("No tokens to report or no recipient email configured.")

        # --- PART 2: DELETE OLD TOKENS (WITH NEW, ROBUST LOGIC) ---
        
        # #### START OF FIX 1: Use timezone-aware datetimes ####
        # Always use Django's timezone.now() to avoid naive datetime warnings.
        now = timezone.now()
        # now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        cleanup_cutoff_time = now - timedelta(minutes=15)
        # Define a separate cutoff for the active monitoring period (10 mins + 2 min buffer)
        monitoring_cutoff_time = now - timedelta(minutes=12)
        # #### END OF FIX 1 ####
        
        self.stdout.write(f"Looking for inactive tokens created before {cleanup_cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}...")
        
        # #### START OF FIX 2: IMPROVED EXCLUSION LOGIC ####
        # The query now excludes a token if EITHER of these is true:
        # 1. It's an unsold watchlist trade (same as before).
        # 2. It was BOUGHT in the last 12 minutes (protects post-sell monitoring).
        old_tokens = Token.objects.filter(
            timestamp__lt=cleanup_cutoff_time
        ).exclude(
            Q(is_from_watchlist=True, is_sold=False) |
            Q(buy_timestamp__gte=monitoring_cutoff_time)
        )
        # #### END OF FIX 2 ####
        
        deleted_count, _ = old_tokens.delete()
        
        if deleted_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} old inactive token(s).'))
        else:
            self.stdout.write(self.style.SUCCESS('No old inactive tokens to delete.'))