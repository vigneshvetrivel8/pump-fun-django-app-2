from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from pumplistener.models import Token
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Sends an email report of all currently active trades.'

    def handle(self, *args, **options):
        active_trades = Token.objects.filter(is_from_watchlist=True, is_sold=False)

        if not active_trades.exists():
            self.stdout.write(self.style.SUCCESS('No active trades to report. No email sent.'))
            return
        
        self.stdout.write(f"Found {active_trades.count()} active trade(s). Preparing email...")
        
        # Add age calculation for the template
        now = timezone.now()
        for token in active_trades:
            if token.buy_timestamp:
                token.age = now - token.buy_timestamp
            else:
                token.age = "N/A"

        recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
        if not recipient_email:
            self.stdout.write(self.style.ERROR('Cannot send report, REPORT_RECIPIENT_EMAIL not set.'))
            return
            
        report_time_str = now.strftime('%Y-%m-%d %H:%M:%S UTC')
        html_message = render_to_string('pumplistener/active_trades_report.html', {
            'tokens': active_trades,
            'report_time': report_time_str
        })
        subject = f"Active Trades Status Report - {report_time_str}"

        try:
            send_mail(
                subject, "Active Trades Report",
                settings.DEFAULT_FROM_EMAIL, [recipient_email], html_message=html_message
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully sent active trades report to {recipient_email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email: {e}'))