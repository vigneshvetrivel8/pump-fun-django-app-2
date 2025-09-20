# pumplistener/management/commands/monitor_trades.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from pumplistener.models import Token
from pumplistener.listener import collect_data_for_watchlist_coin
import asyncio

class Command(BaseCommand):
    help = 'Monitors active trades and decides whether to sell based on a cooling-down schedule.'

    def handle(self, *args, **options):
        self.stdout.write("Running Routine Trade Monitor...")
        
        # Get all active trades that are older than the initial 5-minute high-frequency window
        five_mins_ago = timezone.now() - timedelta(minutes=5)
        active_trades = Token.objects.filter(
            is_from_watchlist=True, 
            is_sold=False,
            buy_timestamp__lt=five_mins_ago
        )

        if not active_trades.exists():
            self.stdout.write(self.style.SUCCESS('No long-term active trades to monitor.'))
            return

        now = timezone.now()
        current_minute = now.minute

        for token in active_trades:
            age = now - token.buy_timestamp
            should_check = False

            # Define the "cooling down" schedule
            if age <= timedelta(minutes=30): # From 5 to 30 mins, check every minute
                should_check = True
            elif age <= timedelta(hours=3): # From 30 mins to 3 hours, check every 5 minutes
                if current_minute % 5 == 0:
                    should_check = True
            else: # Older than 3 hours, check every 15 minutes
                if current_minute % 15 == 0:
                    should_check = True
            
            if should_check:
                self.stdout.write(f"Checking long-term trade: {token.symbol} (Age: {age})")
                # In the future, real sell logic will go here.
                # For now, we'll just refresh its data.
                asyncio.run(self.refresh_token_data(token))
            else:
                self.stdout.write(f"Skipping check for {token.symbol} (Age: {age}) on this run.")

        self.stdout.write(self.style.SUCCESS('Finished routine trade monitor.'))

    async def refresh_token_data(self, token):
        # This reuses your existing data collection logic to update the token's state
        # We'll just run one check instead of the full 5-minute loop
        from pumplistener.listener import save_data_point, get_moralis_metadata
        
        self.stdout.write(f" -> Refreshing data for {token.symbol}...")
        api_data = await get_moralis_metadata(token.mint_address) # may require token.mint and not token.mint_address
        await save_data_point(token, api_data)