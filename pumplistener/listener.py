########################################################################################################################################################################################

# pumplistener/listener.py

import asyncio
import websockets
import json
import os
import httpx
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta

from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from dotenv import load_dotenv

from .models import Token, TokenDataPoint
from . import trade
# from . import trade4

import collections

# --- Load Environment Variables ---
load_dotenv()

# --- CONFIGURATION ---
PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"
HELIUS_API_KEY = os.environ.get('HELIUS_API_KEY')
HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
PUBLIC_KEY = os.getenv("WALLET_PUBLIC_KEY")
PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")
watchlist_str = os.environ.get('CREATOR_WATCHLIST', '')
# WATCHLIST_CREATORS = set(filter(None, watchlist_str.split(',')))
WATCHLIST_CREATORS = set(watchlist_str.split(','))

# [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]
# --- NEW: Load Multiple Seller URLs ---
seller_urls_str = os.getenv("SELLER_SERVICE_URLS", "")
SELLER_URLS = [url.strip() for url in seller_urls_str.split(',') if url.strip()]

if not SELLER_URLS:
    raise ValueError("🚨 CRITICAL: SELLER_SERVICE_URLS environment variable is not set or empty in the Buyer app!")

print(f"✅ Loaded {len(SELLER_URLS)} Seller Service URLs for rotation: {SELLER_URLS}")

# --- NEW: Rotation Logic ---
seller_index_lock = asyncio.Lock()
current_seller_index = 0

async def get_next_seller_url():
    """Gets the next seller URL from the list in rotation (task-safe)."""
    global current_seller_index
    async with seller_index_lock:
        if not SELLER_URLS:
            return None # Should not happen based on check above, but safety first
        
        url = SELLER_URLS[current_seller_index]
        current_seller_index = (current_seller_index + 1) % len(SELLER_URLS) # Move to next index and wrap around
        return url
# --- END NEW ---

# [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]

moralis_keys_str = os.environ.get('MORALIS_API_KEYS', '')
MORALIS_API_KEYS = [key.strip() for key in moralis_keys_str.split(',') if key.strip()]
if not MORALIS_API_KEYS:
    raise ValueError("🚨 No Moralis API keys found. Please set MORALIS_API_KEYS in .env file.")
print(f"✅ Loaded {len(MORALIS_API_KEYS)} Moralis API keys.")
moralis_key_lock = asyncio.Lock()
current_moralis_key_index = 0

# --- HELPER & API FUNCTIONS ---
async def get_next_moralis_key():
    """Gets the next Moralis API key from the list in a task-safe way."""
    global current_moralis_key_index
    async with moralis_key_lock:
        key = MORALIS_API_KEYS[current_moralis_key_index]
        current_moralis_key_index = (current_moralis_key_index + 1) % len(MORALIS_API_KEYS)
        return key

@sync_to_async
def save_token_to_db(token_data):
    """Saves token data to the database, getting or creating the token."""
    token, created = Token.objects.get_or_create(
        mint_address=token_data['mint_address'],
        defaults=token_data
    )
    
    # if created:
        # print(f"✅ Saved to DB: {token.name} ({token.symbol})")

    return token

@sync_to_async
def save_data_point(token: Token, api_data: dict):
    """MODIFIED: Saves a new data point and returns the created object."""
    data_point = TokenDataPoint.objects.create(token=token, data=api_data)
    print(f"💾 Saved data point for {token.symbol}: {api_data.get('source')}")
    return data_point

@sync_to_async
def send_trade_notification_email(token, buy_sig, sell_sig, combined_log):
    # The parameter name is updated here as well
    recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
    if not recipient_email:
        print("⚠️ Cannot send trade notification, REPORT_RECIPIENT_EMAIL not set.")
        return

    print(f"📧 Preparing trade notification email for {token.symbol}...")
    try:
        subject = f"Watchlist Trade Alert: ${token.symbol}"
        html_message = render_to_string('pumplistener/trade_notification_email.html', {
            'token': token, 
            'buy_sig': buy_sig, 
            'sell_sig': sell_sig,
            'combined_log': combined_log, # Pass the new log to the template
        })
        send_mail(
            subject=subject, message="This email requires an HTML-compatible client.",
            from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[recipient_email],
            html_message=html_message
        )
        print(f"✅ Trade notification for ${token.symbol} sent to {recipient_email}")
    except Exception as e:
        print(f"🚨 Failed to send trade notification email: {e}")

async def get_helius_top_holders_count(mint_address: str):
    """Fetches the top 20 largest accounts from Helius."""
    payload = {"jsonrpc": "2.0", "id": "helius-v1", "method": "getTokenLargestAccounts", "params": [mint_address]}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(HELIUS_RPC_URL, json=payload, timeout=10)
            response.raise_for_status()
            return {"source": "helius_getTokenLargestAccounts", "data": response.json()}
        except Exception as e:
            print(f"🚨 Error fetching from Helius: {e}")
            return {"source": "helius_getTokenLargestAccounts", "error": str(e)}

async def get_moralis_metadata(mint_address: str):
    """Fetches metadata including FDV from Moralis using key rotation."""
    url = f"https://solana-gateway.moralis.io/token/mainnet/{mint_address}/metadata"
    api_key = await get_next_moralis_key()
    headers = {"Accept": "application/json", "X-API-Key": api_key}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return {"source": "moralis_metadata", "data": response.json()}
        except Exception as e:
            print(f"🚨 Error fetching from Moralis (Metadata) with key ending in ...{api_key[-4:]}: {e}")
            return {"source": "mora3lis_metadata", "error": str(e)}

async def get_moralis_holder_stats(mint_address: str):
    """Fetches detailed holder statistics from Moralis using key rotation."""
    url = f"https://solana-gateway.moralis.io/token/mainnet/holders/{mint_address}"
    api_key = await get_next_moralis_key()
    headers = {"Accept": "application/json", "X-API-Key": api_key}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return {"source": "moralis_holder_stats", "data": response.json()}
        except Exception as e:
            print(f"🚨 Error fetching from Moralis (Holders) with key ending in ...{api_key[-4:]}: {e}")
            return {"source": "moralis_holder_stats", "error": str(e)}

async def refresh_token_state(token: Token):
    """MODIFIED: Returns the two data point objects it creates."""
    try:
        metadata, holders = await asyncio.gather(
            get_moralis_metadata(token.mint_address),
            get_moralis_holder_stats(token.mint_address)
        )
        metadata_point = await save_data_point(token, metadata)
        holders_point = await save_data_point(token, holders)

        if 'error' in metadata or 'error' in holders:
            print(f"  -> Skipping state update for {token.symbol} due to API error.")
            return metadata_point, holders_point

        current_mc_str = metadata.get('data', {}).get('fullyDilutedValue')
        current_holders_str = holders.get('data', {}).get('totalHolders')

        if current_mc_str and current_holders_str is not None:
            current_mc = float(current_mc_str)
            current_holders = int(current_holders_str)

            @sync_to_async
            def update_db():
                # #### START OF FIX ####
                # Removed .select_for_update() to resolve the transaction error.
                t = Token.objects.get(pk=token.pk)
                # #### END OF FIX ####
                
                t.current_market_cap = current_mc
                t.current_holder_count = current_holders
                if not t.initial_market_cap:
                    t.initial_market_cap = current_mc
                if not t.highest_market_cap or current_mc > t.highest_market_cap:
                    t.highest_market_cap = current_mc
                if not t.peak_holder_count or current_holders > t.peak_holder_count:
                    t.peak_holder_count = current_holders
                t.save()
            
            await update_db()
            print(f"  -> Refreshed data for {token.symbol}: MC=${current_mc}, Holders={current_holders}")
        
        return metadata_point, holders_point
    except Exception as e:
        print(f"  -> Could not parse API data during refresh for {token.symbol}: {e}")
        return None, None
    
# #### START OF NEW CODE ####
# Add this new helper function near your other async DB functions
@sync_to_async
def mark_token_as_sold(token_id: int, final_market_cap: float):
    """
    Safely finds a token by its ID and updates its status to 'sold'.
    """
    try:
        # Use .get() to find the specific token
        token = Token.objects.get(id=token_id)
        token.is_sold = True
        token.is_active_trade = False # If you have this field
        token.sell_timestamp = timezone.now()
        token.sell_market_cap = final_market_cap # Store the MC at the time of sale
        token.save()
        print(f"  -> 💾 Marked {token.symbol} as SOLD in the database.")
    except Token.DoesNotExist:
        # This handles the case where the token might have been deleted for some other reason
        print(f"  -> ⚠️ Could not mark token ID {token_id} as sold, it was not found in DB.")


async def collect_data_for_watchlist_coin(token: Token, public_key: str, private_key: str, rpc_url: str):
    """
    Monitors a token for 10 minutes, sells at the first trigger, and continues
    monitoring for post-trade analysis. If no trigger occurs, it sells at the end.
    """
    print(f"📊 Starting LIVE TRADE & POST-SELL monitoring for {token.symbol}...")

    combined_log = []
    holder_history = collections.deque(maxlen=4)
    sell_signature = None
    has_sold = False

    # Monitor for up to 10 minutes (40 checks x 15 seconds)
    for i in range(40):
    # 000000000000000000000000000000000000000000000000000000
    # for i in range(3):
    # 000000000000000000000000000000000000000000000000000000
        await asyncio.sleep(15)
        check_time = (i + 1) * 15
        print(f"  -> [{token.symbol}] Running T+{check_time}s check...")

        metadata_point, holders_point = await refresh_token_state(token)
        refreshed_token = await Token.objects.aget(pk=token.pk)

        if refreshed_token.current_holder_count is not None:
            holder_history.append(refreshed_token.current_holder_count)

        current_reason = None
        # --- Sell Strategy Rules ---
        if (i == 1 and refreshed_token.current_holder_count is not None and refreshed_token.current_market_cap is not None
                and refreshed_token.current_holder_count < 12 and refreshed_token.current_market_cap < 12000):
            current_reason = f"Failed 30-Second Viability Gate. Holders: {refreshed_token.current_holder_count}, MC: ${refreshed_token.current_market_cap:,.2f}"
        elif refreshed_token.current_market_cap is not None and refreshed_token.current_market_cap < 12000:
            current_reason = f"Absolute Market Cap Stop-Loss (< $12k). MC: ${refreshed_token.current_market_cap:,.2f}"
        elif (refreshed_token.highest_market_cap is not None and refreshed_token.current_market_cap is not None
              and refreshed_token.current_market_cap < (refreshed_token.highest_market_cap * 0.55)):
            current_reason = f"Trailing MC Stop-Loss (>45% drop from peak of ${refreshed_token.highest_market_cap:,.2f})."
        elif (refreshed_token.peak_holder_count is not None and refreshed_token.current_holder_count is not None
              and refreshed_token.current_holder_count < (refreshed_token.peak_holder_count * 0.60)):
            current_reason = f"Peak Holder Stop-Loss (>40% drop from peak of {refreshed_token.peak_holder_count})."
        elif len(holder_history) >= 4:
            lowest_in_last_3 = min(list(holder_history)[:3])
            if refreshed_token.current_holder_count is not None and refreshed_token.current_holder_count < (lowest_in_last_3 * 0.75):
                current_reason = f"Rapid Holder Decline (>25% drop from recent low of {lowest_in_last_3})."

        decision = None

        if not has_sold and current_reason:
            print(f"  -> 🚨 SELL TRIGGERED for {refreshed_token.symbol} | Reason: {current_reason}")
            temp_sell_sig = await asyncio.to_thread(
                trade.sell, public_key, private_key, refreshed_token.mint_address, rpc_url
            )
            if temp_sell_sig:
                print(f"  -> ✅ SELL SUCCESSFUL for {token.symbol}. Now entering post-sell monitoring.")
                sell_signature = temp_sell_sig
                has_sold = True
                decision = {"action": "SELL", "reason": current_reason, "signature": sell_signature}
                await mark_token_as_sold(refreshed_token.id, refreshed_token.current_market_cap)
            else:
                print(f"  -> ❌ SELL FAILED for {token.symbol}.")
                decision = {"action": "SELL_FAILED", "reason": current_reason}
        else:
            if has_sold:
                if current_reason:
                    print(f"  -> ⚪️ POST-SELL SIMULATION: Would have sold again. Reason: {current_reason}")
                    decision = {"action": "SELL (SIMULATED)", "reason": current_reason}
                else:
                    print(f"  -> ⚪️ POST-SELL SIMULATION: Would be holding.")
                    mc_display = f"${refreshed_token.current_market_cap:,.2f}" if refreshed_token.current_market_cap is not None else "N/A"
                    holders_display = refreshed_token.current_holder_count if refreshed_token.current_holder_count is not None else "N/A"
                    decision = {"action": "HOLD (POST-SELL)", "reason": f"All checks passed. MC: {mc_display}, Holders: {holders_display}"}
            else:
                print(f"  -> ✅ HOLD {refreshed_token.symbol}")
                mc_display = f"${refreshed_token.current_market_cap:,.2f}" if refreshed_token.current_market_cap is not None else "N/A"
                holders_display = refreshed_token.current_holder_count if refreshed_token.current_holder_count is not None else "N/A"
                decision = {"action": "HOLD", "reason": f"All checks passed. MC: {mc_display}, Holders: {holders_display}"}

        if metadata_point and decision:
            combined_log.append({
                "timestamp": metadata_point.timestamp, "metadata_point": metadata_point,
                "holders_point": holders_point, "decision": decision
            })

    if not has_sold:
        print(f"  -> ⏰ Monitoring time ended for {token.symbol}. Executing final sell.")
        final_sell_sig = await asyncio.to_thread(
            trade.sell, public_key, private_key, token.mint_address, rpc_url
        )
        if final_sell_sig:
            sell_signature = final_sell_sig
            decision = {"action": "SELL", "reason": "End of 10-minute monitoring period."}
            refreshed_token = await Token.objects.aget(pk=token.pk)
            await mark_token_as_sold(token.id, refreshed_token.current_market_cap)
            combined_log.append({
                "timestamp": timezone.now(), "metadata_point": None,
                "holders_point": None, "decision": decision
            })
        else:
             print(f"  -> ❌ FINAL SELL FAILED for {token.symbol}.")

    print(f"✅ Finished full monitoring period for {token.symbol}")
    return sell_signature, combined_log


async def run_trade_cycle(public_key, private_key, mint_address, rpc_url):
    """A dedicated async function just for the buy/sell logic."""
    # buy_sig = await asyncio.to_thread(trade3.buy, public_key, private_key, mint_address, rpc_url)
    # The new trade.buy is async, so we call it directly with await!
    buy_sig = await trade.buy(public_key, private_key, mint_address, rpc_url)
    buy_time = timezone.now() + timedelta(hours=5, minutes=30)
    print(f"\n--- Waiting 1.5 seconds before selling ---\n")
    await asyncio.sleep(1.5)
    # sell_sig = await asyncio.to_thread(trade.sell, public_key, private_key, mint_address, rpc_url)
    sell_sig = await asyncio.to_thread(trade.sell, public_key, private_key, mint_address, rpc_url)
    return buy_sig, sell_sig, buy_time

async def monitor_and_report(token_id, buy_signature, public_key, private_key, rpc_url):
    """
    MODIFIED: Now accepts a token_id and fetches the object itself.
    This completely resolves the race condition.
    """
    try:
        # The first thing we do is get the token object.
        token_object = await Token.objects.aget(id=token_id)
        print(f"✅ Background task started for {token_object.symbol} (ID: {token_id}). Starting monitoring...")
        
        sell_signature, combined_log = await collect_data_for_watchlist_coin(
            token_object, public_key, private_key, rpc_url
        )
        
        print(f"📧 Monitoring for {token_object.symbol} finished. Preparing final email report...")
        await send_trade_notification_email(token_object, buy_signature, sell_signature, combined_log)

    except Token.DoesNotExist:
        print(f"🚨 CRITICAL: Background task failed to find Token with ID {token_id}. Cannot monitor or report.")
    except Exception as e:
        print(f"🚨 An unexpected error occurred in the background task for token ID {token_id}: {e}")


async def execute_trade_strategy(token_websocket_data, public_key, private_key, rpc_url):
    """Handles the entire lifecycle for a watchlist token: buy -> monitor -> sell -> report."""
    mint_address = token_websocket_data.get('mint')
    if not mint_address:
        print("🚨 Cannot execute trade, mint address is missing from websocket data.")
        return

    # 1. Execute the BUY transaction first.
    print(f"📈 Watchlist hit for {token_websocket_data.get('symbol')}. Executing BUY immediately...")
    buy_signature = await asyncio.to_thread(trade.buy, public_key, private_key, mint_address, rpc_url)
    buy_timestamp = timezone.now()

    if not buy_signature:
        print(f"🚨 BUY FAILED for {mint_address}. Aborting strategy for this token.")
        return

    # 2. Save the initial token data to the database.
    token_db_data = {
        'timestamp': buy_timestamp, 'name': token_websocket_data.get('name', 'N/A'),
        'symbol': token_websocket_data.get('symbol', 'N/A'), 'mint_address': mint_address,
        'sol_amount': token_websocket_data.get('solAmount') or 0,
        'creator_address': token_websocket_data.get('traderPublicKey', 'N/A'),
        'pump_fun_link': f"https://pump.fun/{mint_address}", 'is_from_watchlist': True,
        'buy_timestamp': buy_timestamp
    }
    token_object = await save_token_to_db(token_db_data)
    
    # 3. If the token was saved, start the background monitoring & selling task.
    if token_object:
        # --- THIS IS THE FIX ---
        # Pass the token's ID (token_object.id), which is a number.
        print(f"✅ DB save complete for {token_object.symbol}. Firing background monitoring task with ID: {token_object.id}")
        asyncio.create_task(
            monitor_and_report(token_object.id, buy_signature, public_key, private_key, rpc_url)
        )
    else:
        print(f"🚨 Could not save token {mint_address} to DB. Cannot start monitoring.")




# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789


# --- ADD THESE NEW FUNCTIONS TO YOUR LISTENER.PY ---

# IMPORTANT: Add the URL for your new Seller service to your environment variables
SELLER_SERVICE_URL = os.getenv("SELLER_SERVICE_URL")

@sync_to_async
def save_buy_record_to_db(token_data):
    """
    Saves a simple record of the buy transaction. 
    The full token state is now managed by the Seller service.
    """
    token, created = Token.objects.get_or_create(
        mint_address=token_data['mint_address'],
        defaults=token_data
    )
    if created:
        print(f"✅ Saved BUY record to local DB: {token.symbol}")
    return token


SELLER_SERVICE_URL = os.getenv("SELLER_SERVICE_URL") # Ensure this is defined

# --- MODIFIED: Core Trade & Notify Function ---
async def execute_trade_and_notify_seller(token_websocket_data, public_key, private_key, rpc_url):
    """
    Buys the token and notifies the NEXT Seller service in rotation.
    """
    mint_address = token_websocket_data.get('mint')
    if not mint_address:
        print("🚨 Cannot execute trade, mint address is missing.")
        return

    # 1. Execute BUY (unchanged)
    print(f"📈 Watchlist hit for {token_websocket_data.get('symbol')}. Executing BUY...")
    # buy_signature = await asyncio.to_thread(trade.buy, public_key, private_key, mint_address, rpc_url)
    # REPLACE IT WITH A DUMMY STRING:
    buy_signature = f"DUMMY_BUY_SIG_FOR_TESTING_{datetime.utcnow().isoformat()}"
    buy_timestamp = timezone.now() # Use Django's timezone

    if not buy_signature:
        print(f"🚨 BUY FAILED for {mint_address}. Aborting.")
        return

    # --- NEW: Get the next seller URL ---
    target_seller_url = await get_next_seller_url()
    if not target_seller_url:
        print("🚨 CRITICAL: Could not get a seller URL for rotation!")
        return
    # --- END NEW ---

    print(f"✅ BUY successful for {mint_address}. Notifying Seller at {target_seller_url} to begin monitoring...")

    # 2. Notify the SELECTED Seller Service API
    api_endpoint = f"{target_seller_url}/v1/monitor/start" # Use the rotated URL
    payload = {
        "mint_address": mint_address,
        "buy_transaction_sig": buy_signature,
        "name": token_websocket_data.get('name', 'N/A'),
        "symbol": token_websocket_data.get('symbol', 'N/A')
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_endpoint, json=payload, timeout=20.0)
            response.raise_for_status() # Raise an exception for errors

        print(f"✅ Successfully notified Seller Service at {target_seller_url} for {mint_address}. Hand-off complete.")

        # 3. Save local BUY record (unchanged)
        token_db_data = {
            'timestamp': buy_timestamp,
            'name': token_websocket_data.get('name', 'N/A'),
            'symbol': token_websocket_data.get('symbol', 'N/A'),
            'mint_address': mint_address,
            'sol_amount': token_websocket_data.get('solAmount') or 0,
            'creator_address': token_websocket_data.get('traderPublicKey', 'N/A'),
            'is_from_watchlist': True,
            'buy_timestamp': buy_timestamp,
            'buy_transaction_sig': buy_signature
        }
        await save_buy_record_to_db(token_db_data)

    except httpx.HTTPStatusError as e:
        # Log which seller failed
        print(f"🚨 Error notifying Seller Service at {target_seller_url}. Status: {e.response.status_code}, Response: {e.response.text}")
    except httpx.RequestError as e:
        # Handle connection errors etc.
        print(f"🚨 Could not connect to Seller Service at {target_seller_url}. Error: {e}")
    except Exception as e:
        print(f"🚨 An unexpected error occurred while calling Seller Service at {target_seller_url}: {e}")

# [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]

# #############################################################################################################################################################

# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789
# 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789


# --- MAIN LISTENER LOOP ---
async def pump_fun_listener():
    print("🎧 Starting Pump.fun WebSocket listener...")
    async for websocket in websockets.connect(PUMPORTAL_WSS):
        try:
            await websocket.send(json.dumps({"method": "subscribeNewToken"}))
            print("✅ WebSocket Connected and Subscribed.")
            # --- TEMPORARY TEST FLAG ---
            # 00000000000000000000000000000000000000000
            has_triggered_test = False
            # 000000000000000000000000000000000000000000
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                if data and data.get('txType') == 'create':
                    creator_address = data.get('traderPublicKey', 'N/A')
                    
                    # if creator_address in WATCHLIST_CREATORS:
                    # 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    if not has_triggered_test:
                        has_triggered_test = True # Set flag so it only runs once
                    # 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                        ############################################################################################
                        # If it's a watchlist token, start the entire non-blocking strategy.
                        # asyncio.create_task(
                        #     execute_trade_strategy(data, PUBLIC_KEY, PRIVATE_KEY, RPC_URL)
                        # )

                        asyncio.create_task(
                            execute_trade_and_notify_seller(data, PUBLIC_KEY, PRIVATE_KEY, RPC_URL)
                        )
                        ############################################################################################
                        # TO Disable trading, we may comment out the above section, and execute only data saving below.
                            # --- Add this logic to save the token and start data collection ---
                        # token_data = {
                        #     'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
                        #     'name': data.get('name', 'N/A'),
                        #     'symbol': data.get('symbol', 'N/A'),
                        #     'mint_address': data.get('mint', 'N/A'),
                        #     'sol_amount': data.get('solAmount') or 0,
                        #     'creator_address': creator_address,
                        #     'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
                        #     'is_from_watchlist': True # Still mark it as a watchlist token
                        # }
                        
                        # token_object = await save_token_to_db(token_data)

                        # 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                        # await collect_data_for_watchlist_coin(token_object)
                        # await send_trade_notification_email(token_object, "N/A", "N/A")
                        # 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

                        
                        # if token_object:
                        #     # Start the 5-minute data collection without trading
                        #     asyncio.create_task(collect_data_for_watchlist_coin(token_object))
                        ############################################################################################
                    else:
                        # If it's NOT a watchlist token, just save it to the database.
                        token_data = {
                            # 'timestamp': timezone.now(),
                            'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
                            'name': data.get('name', 'N/A'),
                            'symbol': data.get('symbol', 'N/A'),
                            'mint_address': data.get('mint', 'N/A'),
                            # 'sol_amount': data.get('solAmount', 0),
                            'sol_amount': data.get('solAmount') or 0, # <-- APPLY FIX HERE
                            'creator_address': creator_address,
                            'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
                            'is_from_watchlist': False
                        }
                        await save_token_to_db(token_data)
        except websockets.ConnectionClosed as e:
            print("⚠️ WebSocket connection closed. Reconnecting in 5 seconds...")
            print(f"Reason: {e}")
            # await asyncio.sleep(5)
            raise
        except Exception as e:
            print(f"💥 Main listener error: {e}. Reconnecting in 5 seconds...")
            # await asyncio.sleep(5)
            raise

# --- MAIN LISTENER LOOP ---
async def pump_fun_listener():
    print("🎧 Starting Pump.fun WebSocket listener...")
    async for websocket in websockets.connect(PUMPORTAL_WSS):
        try:
            await websocket.send(json.dumps({"method": "subscribeNewToken"}))
            print("✅ WebSocket Connected and Subscribed.")

            # --- MODIFIED: Counter for first N trades ---
            trades_executed_count = 0
            MAX_TRADES_TO_EXECUTE = 50 # Trade the first 20 coins detected
            # -------------------------------------------

            while True:
                message = await websocket.recv() # Add try-except for JSONDecodeError if needed

                try: # Add try-except for message processing
                    data = json.loads(message)
                    if data and data.get('txType') == 'create':

                        # --- MODIFIED: Trade if counter is less than the limit ---
                        if trades_executed_count < MAX_TRADES_TO_EXECUTE:
                            print(f"✅ Detected coin #{trades_executed_count + 1} ({data.get('symbol', 'N/A')}). Executing trade...")
                            trades_executed_count += 1 # Increment BEFORE starting task

                            print("=" * 150)
                            print("data:", data)
                            print("=" * 150)

                            # Start the trade and notify task for this coin
                            asyncio.create_task(
                                execute_trade_and_notify_seller(data, PUBLIC_KEY, PRIVATE_KEY, RPC_URL)
                            )
                        # --- END MODIFIED ---
                        else:
                            # If we've already executed the max trades, just save the data
                            print(f"⚪️ Detected coin ({data.get('symbol', 'N/A')}), but already executed {MAX_TRADES_TO_EXECUTE} trades. Saving to DB only.")
                            token_data = {
                                'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
                                'name': data.get('name', 'N/A'),
                                'symbol': data.get('symbol', 'N/A'),
                                'mint_address': data.get('mint', 'N/A'),
                                'sol_amount': data.get('solAmount') or 0,
                                'creator_address': data.get('traderPublicKey', 'N/A'),
                                'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
                                'is_from_watchlist': False # Mark appropriately
                            }
                            await save_token_to_db(token_data) # Save record without trading

                except json.JSONDecodeError as e:
                     print(f"⚠️ Error decoding JSON: {e}. Skipping message.")
                     continue # Skip to next message
                except Exception as e:
                     print(f"💥 Error processing message: {e}. Skipping message.")
                     continue # Skip to next message


        except websockets.ConnectionClosed as e:
            print(f"⚠️ WebSocket connection closed. Reconnecting...")
            print(f"Reason: {e}")
            raise # Trigger reconnection logic in wrapper
        except Exception as e:
            print(f"💥 Main listener error: {e}. Reconnecting...")
            raise # Trigger reconnection logic in wrapper


import time

# --- MODIFIED: Wrapper with Exponential Backoff Logic ---
def run_listener_in_new_loop():
    """
    Wrapper that runs the listener in a loop with a smart reconnection delay.
    """
    wait_time = 5  # Start with a 5-second wait
    while True:
        try:
            asyncio.run(pump_fun_listener())
            # If the listener exits without an error, reset the wait time
            wait_time = 5
        except Exception as e:
            # Any exception (including ConnectionClosed) will land here
            print(f"💥 Listener failed: {e}")
        
        print(f"Reconnecting in {wait_time} seconds...")
        time.sleep(wait_time)
        # Double the wait time for the next attempt, up to a maximum of 60 seconds
        wait_time = min(wait_time * 2, 60)
