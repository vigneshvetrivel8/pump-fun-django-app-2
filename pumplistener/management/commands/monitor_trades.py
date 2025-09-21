# # pumplistener/management/commands/monitor_trades.py

# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from datetime import timedelta
# from pumplistener.models import Token
# from pumplistener.listener import collect_data_for_watchlist_coin
# import asyncio

# class Command(BaseCommand):
#     help = 'Monitors active trades and decides whether to sell based on a cooling-down schedule.'

#     def handle(self, *args, **options):
#         self.stdout.write("Running Routine Trade Monitor...")
        
#         # Get all active trades that are older than the initial 5-minute high-frequency window
#         five_mins_ago = timezone.now() - timedelta(minutes=5)
#         active_trades = Token.objects.filter(
#             is_from_watchlist=True, 
#             is_sold=False,
#             buy_timestamp__lt=five_mins_ago
#         )

#         if not active_trades.exists():
#             self.stdout.write(self.style.SUCCESS('No long-term active trades to monitor.'))
#             return

#         now = timezone.now()
#         current_minute = now.minute

#         for token in active_trades:
#             age = now - token.buy_timestamp
#             should_check = False

#             # Define the "cooling down" schedule
#             if age <= timedelta(minutes=30): # From 5 to 30 mins, check every minute
#                 should_check = True
#             elif age <= timedelta(hours=3): # From 30 mins to 3 hours, check every 5 minutes
#                 if current_minute % 5 == 0:
#                     should_check = True
#             else: # Older than 3 hours, check every 15 minutes
#                 if current_minute % 15 == 0:
#                     should_check = True
            
#             if should_check:
#                 self.stdout.write(f"Checking long-term trade: {token.symbol} (Age: {age})")
#                 # In the future, real sell logic will go here.
#                 # For now, we'll just refresh its data.
#                 asyncio.run(self.refresh_token_data(token))
#             else:
#                 self.stdout.write(f"Skipping check for {token.symbol} (Age: {age}) on this run.")

#         self.stdout.write(self.style.SUCCESS('Finished routine trade monitor.'))

#     async def refresh_token_data(self, token):
#         # This reuses your existing data collection logic to update the token's state
#         # We'll just run one check instead of the full 5-minute loop
#         from pumplistener.listener import save_data_point, get_moralis_metadata
        
#         self.stdout.write(f" -> Refreshing data for {token.symbol}...")
#         api_data = await get_moralis_metadata(token.mint_address) # may require token.mint and not token.mint_address
#         await save_data_point(token, api_data)

###########################################################################################################################
# pumplistener/management/commands/monitor_trades.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from pumplistener.models import Token
from pumplistener.listener import refresh_token_state # Import our new helper
import asyncio

class Command(BaseCommand):
    help = 'Monitors all recent watchlist trades (sold or not) and checks for sell conditions on active ones.'

    def handle(self, *args, **options):
        self.stdout.write("Running Routine Trade Monitor...")
        
        # 1. Fetch ALL recent watchlist tokens, sold or not, for data collection.
        # We'll check tokens created in the last 6 hours.
        recent_time_cutoff = timezone.now() - timedelta(hours=6)
        recent_watchlist_tokens = Token.objects.filter(
            is_from_watchlist=True,
            timestamp__gte=recent_time_cutoff
        ).order_by('timestamp')

        if not recent_watchlist_tokens.exists():
            self.stdout.write(self.style.SUCCESS('No recent watchlist tokens to process.'))
            return

        for token in recent_watchlist_tokens:
            self.stdout.write(f"Processing token: {token.symbol} (Sold: {token.is_sold})")
            
            # 2. ALWAYS refresh the data for post-sale analysis.
            asyncio.run(refresh_token_state(token))

            # 3. ONLY check sell conditions if the token is NOT already sold.
            if not token.is_sold:
                # Refresh the token object from DB to get the latest data
                token.refresh_from_db()

                # --- SIMULATION: Check sell rules ---
                # This is where your future selling logic will go.
                if token.initial_market_cap and token.current_market_cap:
                    if token.current_market_cap >= token.initial_market_cap * 2:
                        self.stdout.write(self.style.WARNING(f"  -> 🚨 SIMULATION: Would sell {token.symbol} for 2x profit!"))
                        # Real trade.sell() call would go here.
                    elif token.current_market_cap <= token.initial_market_cap * 0.5:
                         self.stdout.write(self.style.WARNING(f"  -> 🚨 SIMULATION: Would sell {token.symbol} for 50% stop-loss!"))

        self.stdout.write(self.style.SUCCESS('Finished routine trade monitor.'))