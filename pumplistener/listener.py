# import asyncio
# import websockets
# import json
# import time

# from datetime import datetime    # <--- ADD THIS
# from zoneinfo import ZoneInfo    # <--- ADD THIS

# # --- CONFIGURATION ---
# PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"

# ########################################################################################################################
# # async def pump_fun_listener():
# #     """
# #     Connects to the PumpPortal WebSocket, listens for new token events,
# #     and prints the data for every creation event.
# #     """
# #     print("🚀 Starting Basic Pump.fun New Token Monitor...")
# #     print(f"Connecting to WebSocket: {PUMPORTAL_WSS}")

# #     try:
# #         async with websockets.connect(PUMPORTAL_WSS) as websocket:
# #             print("✅ Successfully connected to WebSocket.")
# #             subscribe_message = {"method": "subscribeNewToken"}
# #             await websocket.send(json.dumps(subscribe_message))
# #             print("✅ Subscribed to new token stream. Waiting for launches...\n")

# #             while True:
# #                 try:
# #                     message = await websocket.recv()
# #                     data = json.loads(message)

# #                     if data and data.get('txType') == 'create':
# #                         print("=============================================")
# #                         print(f"🔥 New Token Creation Detected!")
# #                         print(f"   -> Name: {data.get('name', 'N/A')} (${data.get('symbol', 'N/A')})")
# #                         print(f"   -> Mint Address: {data.get('mint', 'N/A')}")
# #                         print(f"   -> Creator Invested: {data.get('solAmount', 0):.2f} SOL")
# #                         print(f"   -> Creator: {data.get('traderPublicKey', 'N/A')}")
# #                         print(f"   -> Link: https://pump.fun/{data.get('mint', '')}")
# #                         print("=============================================\n")

# #                 except websockets.ConnectionClosed:
# #                     print("⚠️ WebSocket connection closed. Will attempt to reconnect...")
# #                     break
# #                 except Exception as e:
# #                     print(f"💥 An error occurred while processing a message: {e}")

# #     except Exception as e:
# #         print(f"💥 Failed to connect to WebSocket: {e}")

# # *********************************************************************************************************************

# async def pump_fun_listener():
#     print("🚀 Starting Pump.fun listener (in-thread)...")
#     try:
#         async with websockets.connect(PUMPORTAL_WSS) as websocket:
#             print("✅ WebSocket Connected (in-thread).")
#             subscribe_message = {"method": "subscribeNewToken"}
#             await websocket.send(json.dumps(subscribe_message))
#             print("✅ Subscribed to new tokens (in-thread).")
#             while True:
#                 try:
#                     message = await websocket.recv()
#                     data = json.loads(message)
#                     if data and data.get('txType') == 'create':
#                         # --- GET THE CURRENT TIME IN IST ---
#                         timestamp_ist = datetime.now(ZoneInfo("Asia/Kolkata"))

#                         print("=============================================")
#                         # --- ADD THE NEW PRINT STATEMENT FOR THE TIME ---
#                         print(f"🔥 New Token Detected at {timestamp_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                        
#                         # print(f"   -> Name: {data.get('name', 'N/A')}")
#                         # print(f"   -> Mint: {data.get('mint', 'N/A')}")
#                         print(f"   -> Name: {data.get('name', 'N/A')} (${data.get('symbol', 'N/A')})")
#                         print(f"   -> Mint Address: {data.get('mint', 'N/A')}")
#                         print(f"   -> Creator Invested: {data.get('solAmount', 0):.2f} SOL")
#                         print(f"   -> Creator: {data.get('traderPublicKey', 'N/A')}")
#                         print(f"   -> Link: https://pump.fun/{data.get('mint', '')}")
#                         print("=============================================\n")

#                 except websockets.ConnectionClosed:
#                     print("⚠️ WebSocket connection closed. Reconnecting...")
#                     break
#     except Exception as e:
#         print(f"💥 Listener thread error: {e}")

# ########################################################################################################################

# def run_listener_in_new_loop():
#     """
#     Wrapper to run the async listener in a new asyncio event loop.
#     This is necessary to run in a separate thread.
#     """
#     while True:
#         try:
#             # Create and run a new event loop for the async function
#             asyncio.run(pump_fun_listener())
#         except Exception as e:
#             print(f"💥 Main listener loop crashed: {e}")
        
#         print("Reconnecting in 10 seconds...")
#         time.sleep(10)

#################################################################################################################################
#################################################################################################################################
#################################################################################################################################

# pumplistener/listener.py

# import asyncio
# import websockets
# import json
# import time
# from datetime import datetime
# from zoneinfo import ZoneInfo
# from asgiref.sync import sync_to_async # <--- ADD THIS
# from .models import Token # <--- ADD THIS
# from datetime import datetime, timedelta
# import os # <--- ADD THIS

# # --- ADD THIS BLOCK: Load the watchlist from the environment variable ---
# # We load it once when the script starts. Using a set() is very fast for checking.
# watchlist_str = os.environ.get('CREATOR_WATCHLIST', '')
# WATCHLIST_CREATORS = set(watchlist_str.split(','))
# # --- END OF NEW BLOCK ---

# # --- CONFIGURATION ---
# PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"
# LOG_FILE = 'token_log.txt' # <--- CHANGED: Define the log file name

# # --- ADD THIS HELPER FUNCTION ---
# @sync_to_async
# def save_token_to_db(token_data):
#     """Safely saves a token to the database from an async context."""
#     # Check if a token with this mint address already exists
#     if not Token.objects.filter(mint_address=token_data['mint_address']).exists():
#         token = Token.objects.create(**token_data)
#         print(f"✅ Saved to DB: {token.name} ({token.symbol})")
#     else:
#         print(f"⚪️ Duplicate, not saved: {token_data['name']}")

# async def pump_fun_listener():
#     print("🚀 Starting Pump.fun listener (in-thread)...")
#     try:
#         async with websockets.connect(PUMPORTAL_WSS) as websocket:
#             print("✅ WebSocket Connected (in-thread).")
#             subscribe_message = {"method": "subscribeNewToken"}
#             await websocket.send(json.dumps(subscribe_message))
#             print("✅ Subscribed to new tokens (in-thread).")
#             while True:
#                 try:
#                     message = await websocket.recv()
#                     data = json.loads(message)
#                     if data and data.get('txType') == 'create':
#                         ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
#                         creator_address = data.get('traderPublicKey', 'N/A')

#                         # --- Check if the creator is on our watchlist ---
#                         is_on_watchlist = creator_address in WATCHLIST_CREATORS

#                         # --- THIS IS THE NEW LOGIC TO SAVE TO THE DATABASE ---
#                         token_data = {
#                             # 'timestamp': datetime.now(ZoneInfo("Asia/Kolkata")),
#                             # 'timestamp': datetime.now(),
#                             'timestamp': ist_time,
#                             'name': data.get('name', 'N/A'),
#                             'symbol': data.get('symbol', 'N/A'),
#                             'mint_address': data.get('mint', 'N/A'),
#                             'sol_amount': data.get('solAmount', 0),
#                             'creator_address': creator_address,
#                             'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
#                             'is_from_watchlist': is_on_watchlist # <--- ADD THIS
#                         }
#                         await save_token_to_db(token_data)
#                         # --- END OF NEW LOGIC ---
                        
#                         # Optional: Add a special log message for watchlist hits
#                         if is_on_watchlist:
#                             print(f"🚨🚨🚨 WATCHLIST HIT: New token '{data.get('name')}' by {creator_address}")
#                             # You could also add logic here to send an immediate, separate email alert




#                         ####################################################################################################################

#                 except websockets.ConnectionClosed:
#                     print("⚠️ WebSocket connection closed. Reconnecting...")
#                     break
#     except Exception as e:
#         print(f"💥 Listener thread error: {e}")

# # The run_listener_in_new_loop() function remains the same
# def run_listener_in_new_loop():
#     while True:
#         try:
#             asyncio.run(pump_fun_listener())
#         except Exception as e:
#             print(f"💥 Main listener loop crashed: {e}")
#         print("Reconnecting in 10 seconds...")
#         time.sleep(10)

######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################

# pumplistener/listener.py

import asyncio
import websockets
import json
import time
import os
import httpx  # For making async HTTP requests
# import base58
from django.utils import timezone
from asgiref.sync import sync_to_async
from .models import Token, TokenDataPoint
from datetime import datetime, timedelta

# Solana library imports
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient

# --- CONFIGURATION ---
PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"
HELIUS_API_KEY = os.environ.get('HELIUS_API_KEY')
MORALIS_API_KEY = os.environ.get('MORALIS_API_KEY')
HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# --- Load the watchlist ---
watchlist_str = os.environ.get('CREATOR_WATCHLIST', '')
WATCHLIST_CREATORS = set(watchlist_str.split(','))

# --- Database Functions (from previous steps) ---
@sync_to_async
def save_token_to_db(token_data):
    token, created = Token.objects.get_or_create(
        mint_address=token_data['mint_address'],
        defaults=token_data
    )
    if created:
        print(f"✅ Saved to DB: {token.name} ({token.symbol})")
    return token

@sync_to_async
def save_data_point(token: Token, api_data: dict):
    TokenDataPoint.objects.create(token=token, data=api_data)
    print(f"💾 Saved data point for {token.symbol}: {api_data.get('source')}")

##################################################################################################################################################

# --- NEW: Real API Helper Functions ---
# async def get_helius_top_holders_count(mint_address: str):
#     """(Based on helius1.py) Fetches the count of the top 20 holders."""
#     payload = {
#         "jsonrpc": "2.0", "id": "helius-v1", "method": "getTokenLargestAccounts", "params": [mint_address]
#     }
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(HELIUS_RPC_URL, json=payload, timeout=10)
#             response.raise_for_status()
#             data = response.json()
#             count = len(data.get('result', {}).get('value', []))
#             return {"source": "helius_top_20_count", "holder_count": count}
#         except Exception as e:
#             print(f"🚨 Error fetching from Helius: {e}")
#             return {"source": "helius_top_20_count", "error": str(e)}

# async def get_moralis_metadata(mint_address: str):
#     """(Based on moralis1.py) Fetches metadata including FDV."""
#     url = f"https://solana-gateway.moralis.io/token/mainnet/{mint_address}/metadata"
#     headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY}
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, timeout=10)
#             response.raise_for_status()
#             data = response.json()
#             return {"source": "moralis_metadata", "fdv": data.get('fullyDilutedValuation'), "socials": data.get('associated_websites')}
#         except Exception as e:
#             print(f"🚨 Error fetching from Moralis (Metadata): {e}")
#             return {"source": "moralis_metadata", "error": str(e)}

# async def get_moralis_holder_stats(mint_address: str):
#     """(Based on moralis2.py) Fetches detailed holder statistics."""
#     url = f"https://solana-gateway.moralis.io/token/mainnet/holders/{mint_address}"
#     headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY}
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, timeout=10)
#             response.raise_for_status()
#             data = response.json()
#             return {"source": "moralis_holder_stats", "total_holders": data.get('total'), "top_10_percent": data.get('top_10_holders_percentage')}
#         except Exception as e:
#             print(f"🚨 Error fetching from Moralis (Holders): {e}")
#             return {"source": "moralis_holder_stats", "error": str(e)}

# ************************************************************************************************************************************************************

async def get_helius_top_holders_count(mint_address: str):
    """Fetches the top 20 largest accounts from Helius."""
    payload = {
        "jsonrpc": "2.0", "id": "helius-v1", "method": "getTokenLargestAccounts", "params": [mint_address]
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(HELIUS_RPC_URL, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            # --- CHANGE THIS: Return the full data payload ---
            return {"source": "helius_getTokenLargestAccounts", "data": data}
        except Exception as e:
            print(f"🚨 Error fetching from Helius: {e}")
            return {"source": "helius_getTokenLargestAccounts", "error": str(e)}

async def get_moralis_metadata(mint_address: str):
    """Fetches metadata including FDV from Moralis."""
    url = f"https://solana-gateway.moralis.io/token/mainnet/{mint_address}/metadata"
    headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY, "x-source": "pumpfun_tracker"}
    async with httpx.AsyncClient() as client:
        try:
            # response = await client.get(url, headers=headers, timeout=10)
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            # --- CHANGE THIS: Return the full data payload ---
            return {"source": "moralis_metadata", "data": data}
        except Exception as e:
            print(f"🚨 Error fetching from Moralis (Metadata): {e}")
            return {"source": "moralis_metadata", "error": str(e)}

async def get_moralis_holder_stats(mint_address: str):
    """Fetches detailed holder statistics from Moralis."""
    url = f"https://solana-gateway.moralis.io/token/mainnet/holders/{mint_address}"
    headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY, "x-source": "pumpfun_tracker"}
    async with httpx.AsyncClient() as client:
        try:
            # response = await client.get(url, headers=headers, timeout=10)
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            # --- CHANGE THIS: Return the full data payload ---
            return {"source": "moralis_holder_stats", "data": data}
        except Exception as e:
            print(f"🚨 Error fetching from Moralis (Holders): {e}")
            return {"source": "moralis_holder_stats", "error": str(e)}

###################################################################################################################################

# --- NEW: The 5-minute data collection task using the real APIs ---
async def collect_data_for_watchlist_coin(token: Token):
    mint = token.mint_address
    print(f"📈 Starting 5-minute data collection for watchlist coin: {token.symbol} ({mint})")
    
    # T+30s check
    await asyncio.sleep(30)
    print(f"  -> [{token.symbol}] Running T+30s check...")
    helius_data = await get_helius_top_holders_count(mint)
    await save_data_point(token, helius_data)
    moralis_fdv = await get_moralis_metadata(mint)
    await save_data_point(token, moralis_fdv)
    
    # Loop for the next 4.5 minutes, checking every 30 seconds
    for i in range(9):
        await asyncio.sleep(30)
        check_time = (i + 2) * 30
        print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
        
        moralis_stats = await get_moralis_holder_stats(mint)
        await save_data_point(token, moralis_stats)

    print(f"✅ Finished 5-minute data collection for {token.symbol}")


# --- Main listener function (from previous steps) ---
async def pump_fun_listener():
    print("🎧 Starting Pump.fun WebSocket listener...")
    async for websocket in websockets.connect(PUMPORTAL_WSS):
        try:
            subscribe_message = {"method": "subscribeNewToken"}
            await websocket.send(json.dumps(subscribe_message))
            print("✅ WebSocket Connected and Subscribed.")
            
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                if data and data.get('txType') == 'create':
                    # creator_address = data.get('creator', 'N/A')
                    # is_on_watchlist = creator_address in WATCHLIST_CREATORS
                    
                    # token_data = {
                    #     'timestamp': timezone.now(),
                    #     'name': data.get('name', 'N/A'),
                    #     'symbol': data.get('symbol', 'N/A'),
                    #     'mint_address': data.get('mint', 'N/A'),
                    #     'sol_amount': data.get('solAmount', 0),
                    #     'creator_address': creator_address,
                    #     'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
                    #     'is_from_watchlist': is_on_watchlist
                    # }

                    ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
                    creator_address = data.get('traderPublicKey', 'N/A')

                    # --- Check if the creator is on our watchlist ---
                    is_on_watchlist = creator_address in WATCHLIST_CREATORS

                    # --- THIS IS THE NEW LOGIC TO SAVE TO THE DATABASE ---
                    token_data = {
                        # 'timestamp': datetime.now(ZoneInfo("Asia/Kolkata")),
                        # 'timestamp': datetime.now(),
                        'timestamp': ist_time,
                        'name': data.get('name', 'N/A'),
                        'symbol': data.get('symbol', 'N/A'),
                        'mint_address': data.get('mint', 'N/A'),
                        'sol_amount': data.get('solAmount', 0),
                        'creator_address': creator_address,
                        'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
                        'is_from_watchlist': is_on_watchlist # <--- ADD THIS
                    }
                    
                    token_object = await save_token_to_db(token_data)

                    if token_object and token_object.is_from_watchlist:
                        asyncio.create_task(collect_data_for_watchlist_coin(token_object))
        except websockets.ConnectionClosed:
            print("⚠️ WebSocket connection closed. Reconnecting in 10 seconds...")
            await asyncio.sleep(10)
        except Exception as e:
            print(f"💥 Main listener error: {e}. Reconnecting in 10 seconds...")
            await asyncio.sleep(10)


# --- Wrapper function to keep the listener running ---
def run_listener_in_new_loop():
    asyncio.run(pump_fun_listener())