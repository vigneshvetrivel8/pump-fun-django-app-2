# # import asyncio
# # import websockets
# # import json
# # import time

# # from datetime import datetime    # <--- ADD THIS
# # from zoneinfo import ZoneInfo    # <--- ADD THIS

# # # --- CONFIGURATION ---
# # PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"

# # ########################################################################################################################
# # # async def pump_fun_listener():
# # #     """
# # #     Connects to the PumpPortal WebSocket, listens for new token events,
# # #     and prints the data for every creation event.
# # #     """
# # #     print("🚀 Starting Basic Pump.fun New Token Monitor...")
# # #     print(f"Connecting to WebSocket: {PUMPORTAL_WSS}")

# # #     try:
# # #         async with websockets.connect(PUMPORTAL_WSS) as websocket:
# # #             print("✅ Successfully connected to WebSocket.")
# # #             subscribe_message = {"method": "subscribeNewToken"}
# # #             await websocket.send(json.dumps(subscribe_message))
# # #             print("✅ Subscribed to new token stream. Waiting for launches...\n")

# # #             while True:
# # #                 try:
# # #                     message = await websocket.recv()
# # #                     data = json.loads(message)

# # #                     if data and data.get('txType') == 'create':
# # #                         print("=============================================")
# # #                         print(f"🔥 New Token Creation Detected!")
# # #                         print(f"   -> Name: {data.get('name', 'N/A')} (${data.get('symbol', 'N/A')})")
# # #                         print(f"   -> Mint Address: {data.get('mint', 'N/A')}")
# # #                         print(f"   -> Creator Invested: {data.get('solAmount', 0):.2f} SOL")
# # #                         print(f"   -> Creator: {data.get('traderPublicKey', 'N/A')}")
# # #                         print(f"   -> Link: https://pump.fun/{data.get('mint', '')}")
# # #                         print("=============================================\n")

# # #                 except websockets.ConnectionClosed:
# # #                     print("⚠️ WebSocket connection closed. Will attempt to reconnect...")
# # #                     break
# # #                 except Exception as e:
# # #                     print(f"💥 An error occurred while processing a message: {e}")

# # #     except Exception as e:
# # #         print(f"💥 Failed to connect to WebSocket: {e}")

# # # *********************************************************************************************************************

# # async def pump_fun_listener():
# #     print("🚀 Starting Pump.fun listener (in-thread)...")
# #     try:
# #         async with websockets.connect(PUMPORTAL_WSS) as websocket:
# #             print("✅ WebSocket Connected (in-thread).")
# #             subscribe_message = {"method": "subscribeNewToken"}
# #             await websocket.send(json.dumps(subscribe_message))
# #             print("✅ Subscribed to new tokens (in-thread).")
# #             while True:
# #                 try:
# #                     message = await websocket.recv()
# #                     data = json.loads(message)
# #                     if data and data.get('txType') == 'create':
# #                         # --- GET THE CURRENT TIME IN IST ---
# #                         timestamp_ist = datetime.now(ZoneInfo("Asia/Kolkata"))

# #                         print("=============================================")
# #                         # --- ADD THE NEW PRINT STATEMENT FOR THE TIME ---
# #                         print(f"🔥 New Token Detected at {timestamp_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                        
# #                         # print(f"   -> Name: {data.get('name', 'N/A')}")
# #                         # print(f"   -> Mint: {data.get('mint', 'N/A')}")
# #                         print(f"   -> Name: {data.get('name', 'N/A')} (${data.get('symbol', 'N/A')})")
# #                         print(f"   -> Mint Address: {data.get('mint', 'N/A')}")
# #                         print(f"   -> Creator Invested: {data.get('solAmount', 0):.2f} SOL")
# #                         print(f"   -> Creator: {data.get('traderPublicKey', 'N/A')}")
# #                         print(f"   -> Link: https://pump.fun/{data.get('mint', '')}")
# #                         print("=============================================\n")

# #                 except websockets.ConnectionClosed:
# #                     print("⚠️ WebSocket connection closed. Reconnecting...")
# #                     break
# #     except Exception as e:
# #         print(f"💥 Listener thread error: {e}")

# # ########################################################################################################################

# # def run_listener_in_new_loop():
# #     """
# #     Wrapper to run the async listener in a new asyncio event loop.
# #     This is necessary to run in a separate thread.
# #     """
# #     while True:
# #         try:
# #             # Create and run a new event loop for the async function
# #             asyncio.run(pump_fun_listener())
# #         except Exception as e:
# #             print(f"💥 Main listener loop crashed: {e}")
        
# #         print("Reconnecting in 10 seconds...")
# #         time.sleep(10)

# #################################################################################################################################
# #################################################################################################################################
# #################################################################################################################################

# # pumplistener/listener.py

# # import asyncio
# # import websockets
# # import json
# # import time
# # from datetime import datetime
# # from zoneinfo import ZoneInfo
# # from asgiref.sync import sync_to_async # <--- ADD THIS
# # from .models import Token # <--- ADD THIS
# # from datetime import datetime, timedelta
# # import os # <--- ADD THIS

# # # --- ADD THIS BLOCK: Load the watchlist from the environment variable ---
# # # We load it once when the script starts. Using a set() is very fast for checking.
# # watchlist_str = os.environ.get('CREATOR_WATCHLIST', '')
# # WATCHLIST_CREATORS = set(watchlist_str.split(','))
# # # --- END OF NEW BLOCK ---

# # # --- CONFIGURATION ---
# # PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"
# # LOG_FILE = 'token_log.txt' # <--- CHANGED: Define the log file name

# # # --- ADD THIS HELPER FUNCTION ---
# # @sync_to_async
# # def save_token_to_db(token_data):
# #     """Safely saves a token to the database from an async context."""
# #     # Check if a token with this mint address already exists
# #     if not Token.objects.filter(mint_address=token_data['mint_address']).exists():
# #         token = Token.objects.create(**token_data)
# #         print(f"✅ Saved to DB: {token.name} ({token.symbol})")
# #     else:
# #         print(f"⚪️ Duplicate, not saved: {token_data['name']}")

# # async def pump_fun_listener():
# #     print("🚀 Starting Pump.fun listener (in-thread)...")
# #     try:
# #         async with websockets.connect(PUMPORTAL_WSS) as websocket:
# #             print("✅ WebSocket Connected (in-thread).")
# #             subscribe_message = {"method": "subscribeNewToken"}
# #             await websocket.send(json.dumps(subscribe_message))
# #             print("✅ Subscribed to new tokens (in-thread).")
# #             while True:
# #                 try:
# #                     message = await websocket.recv()
# #                     data = json.loads(message)
# #                     if data and data.get('txType') == 'create':
# #                         ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
# #                         creator_address = data.get('traderPublicKey', 'N/A')

# #                         # --- Check if the creator is on our watchlist ---
# #                         is_on_watchlist = creator_address in WATCHLIST_CREATORS

# #                         # --- THIS IS THE NEW LOGIC TO SAVE TO THE DATABASE ---
# #                         token_data = {
# #                             # 'timestamp': datetime.now(ZoneInfo("Asia/Kolkata")),
# #                             # 'timestamp': datetime.now(),
# #                             'timestamp': ist_time,
# #                             'name': data.get('name', 'N/A'),
# #                             'symbol': data.get('symbol', 'N/A'),
# #                             'mint_address': data.get('mint', 'N/A'),
# #                             'sol_amount': data.get('solAmount', 0),
# #                             'creator_address': creator_address,
# #                             'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
# #                             'is_from_watchlist': is_on_watchlist # <--- ADD THIS
# #                         }
# #                         await save_token_to_db(token_data)
# #                         # --- END OF NEW LOGIC ---
                        
# #                         # Optional: Add a special log message for watchlist hits
# #                         if is_on_watchlist:
# #                             print(f"🚨🚨🚨 WATCHLIST HIT: New token '{data.get('name')}' by {creator_address}")
# #                             # You could also add logic here to send an immediate, separate email alert




# #                         ####################################################################################################################

# #                 except websockets.ConnectionClosed:
# #                     print("⚠️ WebSocket connection closed. Reconnecting...")
# #                     break
# #     except Exception as e:
# #         print(f"💥 Listener thread error: {e}")

# # # The run_listener_in_new_loop() function remains the same
# # def run_listener_in_new_loop():
# #     while True:
# #         try:
# #             asyncio.run(pump_fun_listener())
# #         except Exception as e:
# #             print(f"💥 Main listener loop crashed: {e}")
# #         print("Reconnecting in 10 seconds...")
# #         time.sleep(10)

# ######################################################################################################################################################
# ######################################################################################################################################################
# ######################################################################################################################################################

# # pumplistener/listener.py

# # import asyncio
# # import websockets
# # import json
# # import time
# # import os
# # import httpx  # For making async HTTP requests
# # # import base58
# # from django.utils import timezone
# # from asgiref.sync import sync_to_async
# # from .models import Token, TokenDataPoint
# # from datetime import datetime, timedelta

# # # Solana library imports
# # from solders.keypair import Keypair
# # from solders.transaction import VersionedTransaction
# # from solana.rpc.async_api import AsyncClient
# # from dotenv import load_dotenv

# # load_dotenv()

# # # --- CONFIGURATION ---
# # PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"
# # HELIUS_API_KEY = os.environ.get('HELIUS_API_KEY')
# # MORALIS_API_KEY = os.environ.get('MORALIS_API_KEY')
# # HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# # # --- Load the watchlist ---
# # watchlist_str = os.environ.get('CREATOR_WATCHLIST', '')
# # WATCHLIST_CREATORS = set(watchlist_str.split(','))

# # ############################################################################################################################
# # # --- NEW: Load Multiple Moralis Keys ---
# # moralis_keys_str = os.environ.get('MORALIS_API_KEYS', '')
# # MORALIS_API_KEYS = [key.strip() for key in moralis_keys_str.split(',') if key.strip()]

# # if not MORALIS_API_KEYS:
# #     raise ValueError("🚨 No Moralis API keys found in .env file. Please set MORALIS_API_KEYS.")

# # print(f"✅ Loaded {len(MORALIS_API_KEYS)} Moralis API keys.")

# # # *************************************************************************************************************************

# # # --- NEW: Add this right after loading the keys ---
# # current_moralis_key_index = 0

# # def get_next_moralis_key():
# #     """Gets the next Moralis API key from the list in rotation."""
# #     global current_moralis_key_index
    
# #     # Get the current key
# #     key = MORALIS_API_KEYS[current_moralis_key_index]
    
# #     # Move to the next index for the next call, wrapping around if necessary
# #     current_moralis_key_index = (current_moralis_key_index + 1) % len(MORALIS_API_KEYS)
    
# #     return key
# # #############################################################################################################################

# # # --- Database Functions (from previous steps) ---
# # @sync_to_async
# # def save_token_to_db(token_data):
# #     token, created = Token.objects.get_or_create(
# #         mint_address=token_data['mint_address'],
# #         defaults=token_data
# #     )
# #     if created:
# #         print(f"✅ Saved to DB: {token.name} ({token.symbol})")
# #     return token

# # @sync_to_async
# # def save_data_point(token: Token, api_data: dict):
# #     TokenDataPoint.objects.create(token=token, data=api_data)
# #     print(f"💾 Saved data point for {token.symbol}: {api_data.get('source')}")

# # ##################################################################################################################################################

# # # --- NEW: Real API Helper Functions ---
# # # async def get_helius_top_holders_count(mint_address: str):
# # #     """(Based on helius1.py) Fetches the count of the top 20 holders."""
# # #     payload = {
# # #         "jsonrpc": "2.0", "id": "helius-v1", "method": "getTokenLargestAccounts", "params": [mint_address]
# # #     }
# # #     async with httpx.AsyncClient() as client:
# # #         try:
# # #             response = await client.post(HELIUS_RPC_URL, json=payload, timeout=10)
# # #             response.raise_for_status()
# # #             data = response.json()
# # #             count = len(data.get('result', {}).get('value', []))
# # #             return {"source": "helius_top_20_count", "holder_count": count}
# # #         except Exception as e:
# # #             print(f"🚨 Error fetching from Helius: {e}")
# # #             return {"source": "helius_top_20_count", "error": str(e)}

# # # async def get_moralis_metadata(mint_address: str):
# # #     """(Based on moralis1.py) Fetches metadata including FDV."""
# # #     url = f"https://solana-gateway.moralis.io/token/mainnet/{mint_address}/metadata"
# # #     headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY}
# # #     async with httpx.AsyncClient() as client:
# # #         try:
# # #             response = await client.get(url, headers=headers, timeout=10)
# # #             response.raise_for_status()
# # #             data = response.json()
# # #             return {"source": "moralis_metadata", "fdv": data.get('fullyDilutedValuation'), "socials": data.get('associated_websites')}
# # #         except Exception as e:
# # #             print(f"🚨 Error fetching from Moralis (Metadata): {e}")
# # #             return {"source": "moralis_metadata", "error": str(e)}

# # # async def get_moralis_holder_stats(mint_address: str):
# # #     """(Based on moralis2.py) Fetches detailed holder statistics."""
# # #     url = f"https://solana-gateway.moralis.io/token/mainnet/holders/{mint_address}"
# # #     headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY}
# # #     async with httpx.AsyncClient() as client:
# # #         try:
# # #             response = await client.get(url, headers=headers, timeout=10)
# # #             response.raise_for_status()
# # #             data = response.json()
# # #             return {"source": "moralis_holder_stats", "total_holders": data.get('total'), "top_10_percent": data.get('top_10_holders_percentage')}
# # #         except Exception as e:
# # #             print(f"🚨 Error fetching from Moralis (Holders): {e}")
# # #             return {"source": "moralis_holder_stats", "error": str(e)}

# # # ************************************************************************************************************************************************************

# # async def get_helius_top_holders_count(mint_address: str):
# #     """Fetches the top 20 largest accounts from Helius."""
# #     payload = {
# #         "jsonrpc": "2.0", "id": "helius-v1", "method": "getTokenLargestAccounts", "params": [mint_address]
# #     }
# #     async with httpx.AsyncClient() as client:
# #         try:
# #             response = await client.post(HELIUS_RPC_URL, json=payload, timeout=10)
# #             response.raise_for_status()
# #             data = response.json()
# #             # --- CHANGE THIS: Return the full data payload ---
# #             return {"source": "helius_getTokenLargestAccounts", "data": data}
# #         except Exception as e:
# #             print(f"🚨 Error fetching from Helius: {e}")
# #             return {"source": "helius_getTokenLargestAccounts", "error": str(e)}

# # async def get_moralis_metadata(mint_address: str):
# #     """Fetches metadata including FDV from Moralis."""
# #     url = f"https://solana-gateway.moralis.io/token/mainnet/{mint_address}/metadata"
# #     ################################################################################################################
# #     # headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY, "x-source": "pumpfun_tracker"}
# #         # --- MODIFIED LINE ---
# #     # Use the rotating key function instead of a single key variable
# #     api_key = get_next_moralis_key() 
# #     # headers = {"Accept": "application/json", "X-API-Key": api_key, "x-source": "pumpfun_tracker"}
# #     headers = {"Accept": "application/json", "X-API-Key": api_key}
# #     ##################################################################################################################
# #     async with httpx.AsyncClient() as client:
# #         try:
# #             # response = await client.get(url, headers=headers, timeout=10)
# #             response = await client.get(url, headers=headers)
# #             # response = await client.get(url, headers=headers)
# #             response.raise_for_status()
# #             data = response.json()
# #             # --- CHANGE THIS: Return the full data payload ---
# #             return {"source": "moralis_metadata", "data": data}
# #         except Exception as e:
# #             print(f"🚨 Error fetching from Moralis (Metadata): {e}")
# #             return {"source": "moralis_metadata", "error": str(e)}

# # async def get_moralis_holder_stats(mint_address: str):
# #     """Fetches detailed holder statistics from Moralis."""
# #     url = f"https://solana-gateway.moralis.io/token/mainnet/holders/{mint_address}"
# #     ##############################################################################################################################
# #     # headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY, "x-source": "pumpfun_tracker"}
# #     # --- MODIFIED LINE ---
# #     # Use the rotating key function instead of a single key variable
# #     api_key = get_next_moralis_key() 
# #     # headers = {"Accept": "application/json", "X-API-Key": api_key, "x-source": "pumpfun_tracker"}
# #     headers = {"Accept": "application/json", "X-API-Key": api_key}
# #     ###############################################################################################################################
# #     async with httpx.AsyncClient() as client:
# #         try:
# #             # response = await client.get(url, headers=headers, timeout=10)
# #             response = await client.get(url, headers=headers)
# #             # response = await client.get(url, headers=headers)
# #             response.raise_for_status()
# #             data = response.json()
# #             # --- CHANGE THIS: Return the full data payload ---
# #             return {"source": "moralis_holder_stats", "data": data}
# #         except Exception as e:
# #             print(f"🚨 Error fetching from Moralis (Holders): {e}")
# #             return {"source": "moralis_holder_stats", "error": str(e)}

# # ###################################################################################################################################

# # # --- NEW: The 5-minute data collection task using the real APIs ---
# # async def collect_data_for_watchlist_coin(token: Token):
# #     mint = token.mint_address
# #     print(f"📈 Starting 5-minute data collection for watchlist coin: {token.symbol} ({mint})")
    
# #     # T+30s check
# #     await asyncio.sleep(30)
# #     print(f"  -> [{token.symbol}] Running T+30s check...")
# #     helius_data = await get_helius_top_holders_count(mint)
# #     await save_data_point(token, helius_data)
# #     moralis_fdv = await get_moralis_metadata(mint)
# #     await save_data_point(token, moralis_fdv)
    
# #     # Loop for the next 4.5 minutes, checking every 30 seconds
# #     for i in range(9):
# #         await asyncio.sleep(30)
# #         check_time = (i + 2) * 30
# #         print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
        
# #         moralis_stats = await get_moralis_holder_stats(mint)
# #         await save_data_point(token, moralis_stats)

# #     print(f"✅ Finished 5-minute data collection for {token.symbol}")


# # # --- Main listener function (from previous steps) ---
# # async def pump_fun_listener():
# #     print("🎧 Starting Pump.fun WebSocket listener...")
# #     async for websocket in websockets.connect(PUMPORTAL_WSS):
# #         try:
# #             subscribe_message = {"method": "subscribeNewToken"}
# #             await websocket.send(json.dumps(subscribe_message))
# #             print("✅ WebSocket Connected and Subscribed.")

# #             #####################################################################
# #             # --- 1. Initialize a counter for the simulation ---
# #             token_creation_counter = 0
# #             ######################################################################

# #             while True:
# #                 message = await websocket.recv()
# #                 data = json.loads(message)
# #                 if data and data.get('txType') == 'create':
# #                     # creator_address = data.get('creator', 'N/A')
# #                     # is_on_watchlist = creator_address in WATCHLIST_CREATORS
                    
# #                     # token_data = {
# #                     #     'timestamp': timezone.now(),
# #                     #     'name': data.get('name', 'N/A'),
# #                     #     'symbol': data.get('symbol', 'N/A'),
# #                     #     'mint_address': data.get('mint', 'N/A'),
# #                     #     'sol_amount': data.get('solAmount', 0),
# #                     #     'creator_address': creator_address,
# #                     #     'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
# #                     #     'is_from_watchlist': is_on_watchlist
# #                     # }

# #                     ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
# #                     creator_address = data.get('traderPublicKey', 'N/A')

# #                     ################################################################
# #                     # --- 2. Increment the counter for each new coin ---
# #                     token_creation_counter += 1
# #                     ################################################################

# #                     # --- Check if the creator is on our watchlist ---
# #                     ################################################################
# #                     # is_on_watchlist = creator_address in WATCHLIST_CREATORS
# #                     # is_on_watchlist = True
# #                     is_on_watchlist = (token_creation_counter % 15 == 0)
# #                     #################################################################
# #                     ##################################################################

# #                     # --- THIS IS THE NEW LOGIC TO SAVE TO THE DATABASE ---
# #                     token_data = {
# #                         # 'timestamp': datetime.now(ZoneInfo("Asia/Kolkata")),
# #                         # 'timestamp': datetime.now(),
# #                         'timestamp': ist_time,
# #                         'name': data.get('name', 'N/A'),
# #                         'symbol': data.get('symbol', 'N/A'),
# #                         'mint_address': data.get('mint', 'N/A'),
# #                         'sol_amount': data.get('solAmount', 0),
# #                         'creator_address': creator_address,
# #                         'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
# #                         'is_from_watchlist': is_on_watchlist # <--- ADD THIS
# #                     }
                    
# #                     token_object = await save_token_to_db(token_data)

# #                     if token_object and token_object.is_from_watchlist:
# #                         asyncio.create_task(collect_data_for_watchlist_coin(token_object))
# #         except websockets.ConnectionClosed:
# #             print("⚠️ WebSocket connection closed. Reconnecting in 10 seconds...")
# #             await asyncio.sleep(10)
# #         except Exception as e:
# #             print(f"💥 Main listener error: {e}. Reconnecting in 10 seconds...")
# #             await asyncio.sleep(10)


# # # --- Wrapper function to keep the listener running ---
# # def run_listener_in_new_loop():
# #     asyncio.run(pump_fun_listener())

# ######################################################################################################################################################
# ######################################################################################################################################################
# ######################################################################################################################################################
# # pumplistener/listener.py

# import asyncio
# import websockets
# import json
# import time
# import os
# import httpx 	# For making async HTTP requests
# import base58
# from django.utils import timezone
# from asgiref.sync import sync_to_async
# from .models import Token, TokenDataPoint
# from datetime import datetime, timedelta

# # Solana library imports
# from solders.keypair import Keypair
# from solders.transaction import VersionedTransaction
# from solana.rpc.async_api import AsyncClient
# from dotenv import load_dotenv

# from django.utils import timezone

# # ====================================================================================================
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
# # ====================================================================================================

# #######################################################################################################
# #######################################################################################################
# #######################################################################################################

# # Jito and Solana Imports
# # from jito_searcher.client import SearcherClient, get_solana_client
# from solders.keypair import Keypair
# from solders.pubkey import Pubkey
# from solders.transaction import VersionedTransaction
# from solders.system_program import TransferParams, transfer
# from solders.instruction import Instruction
# from solders.message import MessageV0
# from solana.rpc.async_api import AsyncClient

# # --- Solana & Jito Imports (Using the jito-py-rpc library) ---
# # from jito_rpc.jito_rpc_client import JitoRpcClient
# from solana.rpc.async_api import AsyncClient
# from solders.keypair import Keypair
# from solders.pubkey import Pubkey
# from solders.transaction import VersionedTransaction

# import random
# # import bs58

# # *****************************************************************************************************

# # Trading Configuration
# # WALLET_PRIVATE_KEY = os.environ.get('WALLET_PRIVATE_KEY')
# # JITO_BLOCK_ENGINE_URL = os.environ.get('JITO_BLOCK_ENGINE_URL')
# # JITO_RPC_URL = os.environ.get('JITO_RPC_URL')

# # Initialize Solana and Jito clients
# # solana_client = None
# # searcher_client = None
# # jito_keypair = None
# # if JITO_RPC_URL and JITO_BLOCK_ENGINE_URL and WALLET_PRIVATE_KEY:
# #     jito_keypair = Keypair.from_secret_key(base58.b58decode(WALLET_PRIVATE_KEY))
# #     solana_client = get_solana_client(JITO_RPC_URL)
# #     searcher_client = SearcherClient(JITO_BLOCK_ENGINE_URL, jito_keypair)
# #     print("✅ Jito and Solana clients initialized for trading.")
# # else:
# #     print("⚠️ Trading clients not initialized. Check environment variables.")

# from dotenv import load_dotenv
# import os
# # import trade  # Your trade module
# from . import trade
# import time

# # Load environment variables from .env file
# load_dotenv()

# # Define all your configuration variables here
# PUBLIC_KEY = os.getenv("WALLET_PUBLIC_KEY")
# PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
# # MINT_ADDRESS = "GutMnkY4y6kzWJu1P3PfCnxyEkt9veeaLj63DGM5Rh6g"
# # RPC_URL = "https://mainnet.helius-rpc.com/?api-key=5d0a2bb2-0bd2-4f5a-b581-d1785d59e26b"
# RPC_URL = os.getenv("HELIUS_RPC_URL")

# #######################################################################################################
# #######################################################################################################
# #######################################################################################################

# load_dotenv()

# # --- CONFIGURATION ---
# PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"
# HELIUS_API_KEY = os.environ.get('HELIUS_API_KEY')
# # MORALIS_API_KEY = os.environ.get('MORALIS_API_KEY') # This is no longer needed
# HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# # --- Load the watchlist ---
# watchlist_str = os.environ.get('CREATOR_WATCHLIST', '')
# WATCHLIST_CREATORS = set(watchlist_str.split(','))

# ############################################################################################################################
# # --- Load Multiple Moralis Keys ---
# moralis_keys_str = os.environ.get('MORALIS_API_KEYS', '')
# MORALIS_API_KEYS = [key.strip() for key in moralis_keys_str.split(',') if key.strip()]

# if not MORALIS_API_KEYS:
#     raise ValueError("🚨 No Moralis API keys found in .env file. Please set MORALIS_API_KEYS.")

# print(f"✅ Loaded {len(MORALIS_API_KEYS)} Moralis API keys.")

# # *************************************************************************************************************************
# # --- MODIFIED: Key rotation logic with asyncio.Lock to prevent race conditions ---

# # Create a lock to ensure only one task can get a key at a time
# moralis_key_lock = asyncio.Lock()
# current_moralis_key_index = 0

# async def get_next_moralis_key():
#     """
#     Gets the next Moralis API key from the list in a task-safe way.
#     """
#     global current_moralis_key_index

#     async with moralis_key_lock:
#         # This code is now protected. Only one task can execute it at a time.
#         key = MORALIS_API_KEYS[current_moralis_key_index]
#         current_moralis_key_index = (current_moralis_key_index + 1) % len(MORALIS_API_KEYS)
#         return key
# #############################################################################################################################

# # --- Database Functions (from previous steps) ---
# @sync_to_async
# def save_token_to_db(token_data):
#     token, created = Token.objects.get_or_create(
#         mint_address=token_data['mint_address'],
#         defaults=token_data
#     )
#     if created:
#         print(f"✅ Saved to DB: {token.name} ({token.symbol})")
#     return token

# @sync_to_async
# def save_data_point(token: Token, api_data: dict):
#     TokenDataPoint.objects.create(token=token, data=api_data)
#     print(f"💾 Saved data point for {token.symbol}: {api_data.get('source')}")

# ##################################################################################################################################################

# # --- NEW: Real API Helper Functions ---
# # async def get_helius_top_holders_count(mint_address: str):
# # 	 """(Based on helius1.py) Fetches the count of the top 20 holders."""
# # 	 payload = {
# # 		 "jsonrpc": "2.0", "id": "helius-v1", "method": "getTokenLargestAccounts", "params": [mint_address]
# # 	 }
# # 	 async with httpx.AsyncClient() as client:
# # 		 try:
# # 			 response = await client.post(HELIUS_RPC_URL, json=payload, timeout=10)
# # 			 response.raise_for_status()
# # 			 data = response.json()
# # 			 count = len(data.get('result', {}).get('value', []))
# # 			 return {"source": "helius_top_20_count", "holder_count": count}
# # 		 except Exception as e:
# # 			 print(f"🚨 Error fetching from Helius: {e}")
# # 			 return {"source": "helius_top_20_count", "error": str(e)}

# # async def get_moralis_metadata(mint_address: str):
# # 	 """(Based on moralis1.py) Fetches metadata including FDV."""
# # 	 url = f"https://solana-gateway.moralis.io/token/mainnet/{mint_address}/metadata"
# # 	 headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY}
# # 	 async with httpx.AsyncClient() as client:
# # 		 try:
# # 			 response = await client.get(url, headers=headers, timeout=10)
# # 			 response.raise_for_status()
# # 			 data = response.json()
# # 			 return {"source": "moralis_metadata", "fdv": data.get('fullyDilutedValuation'), "socials": data.get('associated_websites')}
# # 		 except Exception as e:
# # 			 print(f"🚨 Error fetching from Moralis (Metadata): {e}")
# # 			 return {"source": "moralis_metadata", "error": str(e)}

# # async def get_moralis_holder_stats(mint_address: str):
# # 	 """(Based on moralis2.py) Fetches detailed holder statistics."""
# # 	 url = f"https://solana-gateway.moralis.io/token/mainnet/holders/{mint_address}"
# # 	 headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY}
# # 	 async with httpx.AsyncClient() as client:
# # 		 try:
# # 			 response = await client.get(url, headers=headers, timeout=10)
# # 			 response.raise_for_status()
# # 			 data = response.json()
# # 			 return {"source": "moralis_holder_stats", "total_holders": data.get('total'), "top_10_percent": data.get('top_10_holders_percentage')}
# # 		 except Exception as e:
# # 			 print(f"🚨 Error fetching from Moralis (Holders): {e}")
# # 			 return {"source": "moralis_holder_stats", "error": str(e)}

# # ************************************************************************************************************************************************************

# async def get_helius_top_holders_count(mint_address: str):
#     """Fetches the top 20 largest accounts from Helius."""
#     payload = {
#         "jsonrpc": "2.0", "id": "helius-v1", "method": "getTokenLargestAccounts", "params": [mint_address]
#     }
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(HELIUS_RPC_URL, json=payload, timeout=10)
#             response.raise_for_status()
#             data = response.json()
#             # --- CHANGE THIS: Return the full data payload ---
#             return {"source": "helius_getTokenLargestAccounts", "data": data}
#         except Exception as e:
#             print(f"🚨 Error fetching from Helius: {e}")
#             return {"source": "helius_getTokenLargestAccounts", "error": str(e)}

# async def get_moralis_metadata(mint_address: str):
#     """Fetches metadata including FDV from Moralis."""
#     url = f"https://solana-gateway.moralis.io/token/mainnet/{mint_address}/metadata"
#     ################################################################################################################
#     # headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY, "x-source": "pumpfun_tracker"}
#     # --- MODIFIED LINE ---
#     # Use the rotating key function instead of a single key variable
#     api_key = await get_next_moralis_key()
#     # headers = {"Accept": "application/json", "X-API-Key": api_key, "x-source": "pumpfun_tracker"}
#     headers = {"Accept": "application/json", "X-API-Key": api_key}
#     ##################################################################################################################
#     async with httpx.AsyncClient() as client:
#         try:
#             # response = await client.get(url, headers=headers, timeout=10)
#             response = await client.get(url, headers=headers)
#             # response = await client.get(url, headers=headers)
#             response.raise_for_status()
#             data = response.json()
#             # --- CHANGE THIS: Return the full data payload ---
#             return {"source": "moralis_metadata", "data": data}
#         except Exception as e:
#             print(f"🚨 Error fetching from Moralis (Metadata) with key ending in ...{api_key[-4:]}: {e}")
#             return {"source": "moralis_metadata", "error": str(e)}

# async def get_moralis_holder_stats(mint_address: str):
#     """Fetches detailed holder statistics from Moralis."""
#     url = f"https://solana-gateway.moralis.io/token/mainnet/holders/{mint_address}"
#     ##############################################################################################################################
#     # headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY, "x-source": "pumpfun_tracker"}
#     # --- MODIFIED LINE ---
#     # Use the rotating key function instead of a single key variable
#     api_key = await get_next_moralis_key()
#     # headers = {"Accept": "application/json", "X-API-Key": api_key, "x-source": "pumpfun_tracker"}
#     headers = {"Accept": "application/json", "X-API-Key": api_key}
#     ###############################################################################################################################
#     async with httpx.AsyncClient() as client:
#         try:
#             # response = await client.get(url, headers=headers, timeout=10)
#             response = await client.get(url, headers=headers)
#             # response = await client.get(url, headers=headers)
#             response.raise_for_status()
#             data = response.json()
#             # --- CHANGE THIS: Return the full data payload ---
#             return {"source": "moralis_holder_stats", "data": data}
#         except Exception as e:
#             print(f"🚨 Error fetching from Moralis (Holders) with key ending in ...{api_key[-4:]}: {e}")
#             return {"source": "moralis_holder_stats", "error": str(e)}

# ###################################################################################################################################

# # --- NEW: The 5-minute data collection task using the real APIs ---
# async def collect_data_for_watchlist_coin(token: Token):
#     mint = token.mint_address
#     print(f"📈 Starting 5-minute data collection for watchlist coin: {token.symbol} ({mint})")
    
#     # T+30s check
#     await asyncio.sleep(30)
#     print(f" 	-> [{token.symbol}] Running T+30s check...")
#     helius_data = await get_helius_top_holders_count(mint)
#     await save_data_point(token, helius_data)
#     moralis_fdv = await get_moralis_metadata(mint)
#     await save_data_point(token, moralis_fdv)
    
#     # Loop for the next 4.5 minutes, checking every 30 seconds
#     for i in range(9):
#         await asyncio.sleep(30)
#         check_time = (i + 2) * 30
#         print(f" 	-> [{token.symbol}] Running T+{check_time}s check...")
        
#         moralis_stats = await get_moralis_holder_stats(mint)
#         await save_data_point(token, moralis_stats)

#     print(f"✅ Finished 5-minute data collection for {token.symbol}")

# ######################################################################################################################
# ######################################################################################################################
# ######################################################################################################################


# # # === REUSABLE TRADING FUNCTIONS ===
# # async def jito_buy_token(token: Token, amount_sol: str, slippage: int) -> bool:
# #     """Handles the complete logic for buying a token via Jito."""
# #     print(f"  -> Preparing BUY for {amount_sol} SOL of {token.symbol}...")
# #     try:
# #         swap_payload = {
# #             "publicKey": str(jito_keypair.pubkey()), "action": "buy", "mint": token.mint_address,
# #             "denominatedInSol": "true", "amount": amount_sol, "slippage": slippage, "priorityFee": 0.001
# #         }
# #         async with httpx.AsyncClient() as client:
# #             swap_response = await client.post("https://pumpportal.fun/api/trade-local", json=swap_payload, timeout=20)
        
# #         if swap_response.status_code != 200:
# #             print(f"    🚨 BUY FAILED: Could not get swap tx from PumpPortal. {swap_response.text}")
# #             return False

# #         swap_tx = VersionedTransaction.from_bytes(swap_response.content)
# #         swap_tx.sign([jito_keypair])
        
# #         # Use Jito's sendTransaction for fast, single-tx execution
# #         await jito_rpc_client.send_transaction(swap_tx)
# #         print(f"    ✅ BUY transaction sent successfully via Jito for {token.symbol}.")
# #         return True
# #     except Exception as e:
# #         print(f"    🚨 BUY FAILED: A critical error occurred: {e}")
# #         return False

# # async def jito_sell_token(token: Token, sell_percentage: str, slippage: int) -> bool:
# #     """Handles the complete logic for selling a token via Jito."""
# #     print(f"  -> Preparing SELL for {sell_percentage} of {token.symbol}...")
# #     try:
# #         sell_payload = {
# #             "publicKey": str(jito_keypair.pubkey()), "action": "sell", "mint": token.mint_address,
# #             "denominatedInSol": "false", "amount": sell_percentage, "slippage": slippage, "priorityFee": 0.001
# #         }
# #         async with httpx.AsyncClient() as client:
# #             sell_response = await client.post("https://pumpportal.fun/api/trade-local", json=sell_payload, timeout=20)

# #         if sell_response.status_code != 200:
# #             print(f"    🚨 SELL FAILED: Could not get sell tx from PumpPortal. {sell_response.text}")
# #             return False
            
# #         sell_tx = VersionedTransaction.from_bytes(sell_response.content)
# #         sell_tx.sign([jito_keypair])
        
# #         await jito_rpc_client.send_transaction(sell_tx)
# #         print(f"    ✅ SELL transaction sent successfully via Jito for {token.symbol}.")
# #         return True
# #     except Exception as e:
# #         print(f"    🚨 SELL FAILED: A critical error occurred: {e}")
# #         return False

# # # === ORCHESTRATOR / STRATEGY FUNCTION ===
# # async def execute_jito_flip_strategy(token: Token):
# #     """Orchestrates the buy, wait, and sell sequence using the reusable functions."""
# #     print(f"📈 Executing 1.5s Jito FLIP strategy for {token.symbol}...")
    
# #     # --- Strategy Configuration ---
# #     BUY_AMOUNT_SOL = "0.01"
# #     MAX_BUY_SLIPPAGE = 40
# #     SELL_SLIPPAGE = 25
# #     FLIP_DELAY_SECONDS = 1.5

# #     # --- Execute the Strategy ---
# #     buy_successful = await jito_buy_token(token, amount_sol=BUY_AMOUNT_SOL, slippage=MAX_BUY_SLIPPAGE)
    
# #     if buy_successful:
# #         print(f"  -> Waiting {FLIP_DELAY_SECONDS} seconds...")
# #         await asyncio.sleep(FLIP_DELAY_SECONDS)
# #         await jito_sell_token(token, sell_percentage="100%", slippage=SELL_SLIPPAGE)
# #     else:
# #         print(f"  -> Aborting flip strategy for {token.symbol} due to buy failure.")

# #     print(f"✅ Strategy finished for {token.symbol}.")

# ######################################################################################################################
# ######################################################################################################################
# ######################################################################################################################


# # ====================================================================================================================
# # --- NEW: Asynchronous function to send the trade notification email ---
# @sync_to_async
# def send_trade_notification_email(token, buy_sig, sell_sig):
#     """
#     Renders and sends an email report for a completed trade.
#     This function is decorated to run Django's sync code in an async-safe way.
#     """
#     recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
#     if not recipient_email:
#         print("⚠️ Cannot send trade notification, REPORT_RECIPIENT_EMAIL not set.")
#         return

#     print(f"📧 Preparing trade notification email for {token.symbol}...")
#     try:
#         subject = f"Watchlist Trade Alert: ${token.symbol}"
#         html_message = render_to_string('pumplistener/trade_notification_email.html', {
#             'token': token,
#             'buy_sig': buy_sig,
#             'sell_sig': sell_sig,
#         })
        
#         send_mail(
#             subject,
#             "A trade was executed for a token on your watchlist.",
#             settings.DEFAULT_FROM_EMAIL,
#             [recipient_email],
#             html_message=html_message
#         )
#         print(f"✅ Trade notification for ${token.symbol} sent to {recipient_email}")
#     except Exception as e:
#         print(f"🚨 Failed to send trade notification email: {e}")

# # ====================================================================================================================
# # --- NEW: Orchestrator to run the full trade cycle without blocking the listener ---
# # async def execute_trade_strategy(token_object, public_key, private_key, rpc_url):
# #     """
# #     Runs the entire buy -> wait -> sell -> notify sequence.
# #     """
# #     mint_address = token_object.mint_address

# #     # Run the synchronous, blocking trade.buy() in a separate thread
# #     buy_signature = await asyncio.to_thread(
# #         trade.buy, public_key, private_key, mint_address, rpc_url
# #     )

# #     # Use asyncio.sleep() which is non-blocking
# #     print(f"\n--- Waiting for 1.5 seconds before selling {token_object.symbol} ---\n")
# #     await asyncio.sleep(1.5)

# #     # Run the synchronous, blocking trade.sell() in a separate thread
# #     sell_signature = await asyncio.to_thread(
# #         trade.sell, public_key, private_key, mint_address, rpc_url
# #     )
    
# #     # After trading is complete, send the email notification
# #     await send_trade_notification_email(token_object, buy_signature, sell_signature)

# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------

# # --- STRATEGY & DATA COLLECTION FUNCTIONS ---

# # async def run_trade_cycle(public_key, private_key, mint_address, rpc_url):
# #     """A dedicated async function just for the buy/sell logic."""
# #     buy_sig = await asyncio.to_thread(trade.buy, public_key, private_key, mint_address, rpc_url)
# #     print(f"\n--- Waiting 1.5 seconds before selling ---\n")
# #     await asyncio.sleep(1.5)
# #     sell_sig = await asyncio.to_thread(trade.sell, public_key, private_key, mint_address, rpc_url)
# #     return buy_sig, sell_sig


# # # --- MODIFIED: HYPER-OPTIMIZED STRATEGY ORCHESTRATOR ---
# # async def execute_trade_strategy(token_websocket_data, public_key, private_key, rpc_url):
# #     """
# #     Handles the entire lifecycle for a watchlist token with maximum speed.
# #     """
# #     mint_address = token_websocket_data.get('mint')
# #     if not mint_address:
# #         print("🚨 Cannot execute trade, mint address is missing.")
# #         return

# #     # 1. Immediately start the trade cycle as a background task.
# #     trade_task = asyncio.create_task(
# #         run_trade_cycle(public_key, private_key, mint_address, rpc_url)
# #     )

# #     print(f"📈 Watchlist hit for {token_websocket_data.get('symbol')}. Firing trade task immediately...")

# #     # 2. In parallel, prepare and start saving the token to the database.
# #     token_db_data = {
# #         'timestamp': timezone.now(),
# #         'name': token_websocket_data.get('name', 'N/A'),
# #         'symbol': token_websocket_data.get('symbol', 'N/A'),
# #         'mint_address': mint_address,
# #         'sol_amount': token_websocket_data.get('solAmount', 0),
# #         'creator_address': token_websocket_data.get('traderPublicKey', 'N/A'),
# #         'pump_fun_link': f"https://pump.fun/{mint_address}",
# #         'is_from_watchlist': True
# #     }
# #     db_save_task = asyncio.create_task(save_token_to_db(token_db_data))

# #     # 3. Now, wait for both critical tasks to complete.
# #     trade_signatures = await trade_task
# #     token_object = await db_save_task
# #     buy_signature, sell_signature = trade_signatures

# #     # 4. Once the trade is done and the token is saved, start the post-trade tasks.
# #     if token_object:
# #         print(f"✅ Trade and DB save complete for {token_object.symbol}. Starting post-trade actions.")
# #         # These can also run in parallel for efficiency
# #         await asyncio.gather(
# #             send_trade_notification_email(token_object, buy_signature, sell_signature),
# #             collect_data_for_watchlist_coin(token_object)
# #         )
# #     else:
# #         print(f"🚨 Could not run post-trade actions for {mint_address}, token object not available.")


# # # ====================================================================================================================

# # # --- Main listener function (from previous steps) ---
# # async def pump_fun_listener():
# #     print("🎧 Starting Pump.fun WebSocket listener...")
# #     async for websocket in websockets.connect(PUMPORTAL_WSS):
# #         try:
# #             subscribe_message = {"method": "subscribeNewToken"}
# #             await websocket.send(json.dumps(subscribe_message))
# #             print("✅ WebSocket Connected and Subscribed.")

# #             #####################################################################
# #             # --- 1. Initialize a counter for the simulation ---
# #             # token_creation_counter = 0
# #             ######################################################################

# #             while True:
# #                 message = await websocket.recv()
# #                 data = json.loads(message)
# #                 if data and data.get('txType') == 'create':
# #                     # creator_address = data.get('creator', 'N/A')
# #                     # is_on_watchlist = creator_address in WATCHLIST_CREATORS
                    
# #                     # token_data = {
# #                     # 	 'timestamp': timezone.now(),
# #                     # 	 'name': data.get('name', 'N/A'),
# #                     # 	 'symbol': data.get('symbol', 'N/A'),
# #                     # 	 'mint_address': data.get('mint', 'N/A'),
# #                     # 	 'sol_amount': data.get('solAmount', 0),
# #                     # 	 'creator_address': creator_address,
# #                     # 	 'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
# #                     # 	 'is_from_watchlist': is_on_watchlist
# #                     # }

# #                     creator_address = data.get('traderPublicKey', 'N/A')
                    
# #                     if creator_address in WATCHLIST_CREATORS:
# #                         # Immediately create one task for the entire watchlist lifecycle and move on.
# #                         asyncio.create_task(
# #                             execute_trade_strategy(data, PUBLIC_KEY, PRIVATE_KEY, RPC_URL)
# #                         )

# #                     ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)

# #                     ################################################################
# #                     # --- 2. Increment the counter for each new coin ---
# #                     # token_creation_counter += 1
# #                     ################################################################

# #                     # --- Check if the creator is on our watchlist ---
# #                     ################################################################
# #                     is_on_watchlist = creator_address in WATCHLIST_CREATORS
# #                     # is_on_watchlist = True
# #                     # is_on_watchlist = (token_creation_counter % 5 == 0)
# #                     #################################################################
# #                     ##################################################################

# #                     # --- THIS IS THE NEW LOGIC TO SAVE TO THE DATABASE ---
# #                     token_data = {
# #                         # 'timestamp': datetime.now(ZoneInfo("Asia/Kolkata")),
# #                         # 'timestamp': datetime.now(),
# #                         # 'timestamp': ist_time,
# #                         'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
# #                         'name': data.get('name', 'N/A'),
# #                         'symbol': data.get('symbol', 'N/A'),
# #                         'mint_address': data.get('mint', 'N/A'),
# #                         'sol_amount': data.get('solAmount', 0),
# #                         'creator_address': creator_address,
# #                         'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
# #                         'is_from_watchlist': is_on_watchlist # <--- ADD THIS
# #                     }
                    
# #                     token_object = await save_token_to_db(token_data)

# #                     # if token_object and token_object.is_from_watchlist:
# #                     #     #########################################################################################
# #                     #     # --- CALL THE NEW FLIP STRATEGY ---
# #                     #     # asyncio.create_task(execute_jito_flip_strategy(token_object))
# #                     #     # if data.get('mint'):
# #                     #     #     MINT_ADDRESS = data.get('mint')
# #                     #     #     # Ensure all variables are loaded correctly
# #                     #     #     if not all([PUBLIC_KEY, PRIVATE_KEY, MINT_ADDRESS, RPC_URL]):
# #                     #     #         print("❌ Error: One or more environment variables are not set. Check your .env file.")
# #                     #     #     else:
# #                     #     #         # Pass the variables as arguments to the functions
# #                     #     #         trade.buy(
# #                     #     #             public_key=PUBLIC_KEY, 
# #                     #     #             private_key=PRIVATE_KEY, 
# #                     #     #             mint_address=MINT_ADDRESS, 
# #                     #     #             rpc_url=RPC_URL
# #                     #     #         )

# #                     #     #         print("\n--- Waiting for 1.5 seconds before selling ---\n")
# #                     #     #         time.sleep(1.5)

# #                     #     #         trade.sell(
# #                     #     #             public_key=PUBLIC_KEY, 
# #                     #     #             private_key=PRIVATE_KEY, 
# #                     #     #             mint_address=MINT_ADDRESS, 
# #                     #     #             rpc_url=RPC_URL
# #                     #     #         )
# #                     #     # ========================================================================================
# #                     #     # --- MODIFIED: Call the non-blocking strategy ---
# #                     #     print(f"📈 Watchlist hit for {token_object.symbol}. Starting trade strategy...")
# #                     #     asyncio.create_task(
# #                     #         execute_trade_strategy(token_object, PUBLIC_KEY, PRIVATE_KEY, RPC_URL)
# #                     #     )
                        
# #                         # Data collection can still run in parallel
# #                         # asyncio.create_task(collect_data_for_watchlist_coin(token_object))
# #                         # =======================================================================================
# #                         #########################################################################################
# #                     asyncio.create_task(collect_data_for_watchlist_coin(token_object))
# #         except websockets.ConnectionClosed:
# #             print("⚠️ WebSocket connection closed. Reconnecting in 10 seconds...")
# #             await asyncio.sleep(10)
# #         except Exception as e:
# #             print(f"💥 Main listener error: {e}. Reconnecting in 10 seconds...")
# #             await asyncio.sleep(10)

# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------


# # --- STRATEGY & DATA COLLECTION FUNCTIONS ---
# async def run_trade_cycle(public_key, private_key, mint_address, rpc_url):
#     """A dedicated async function just for the buy/sell logic."""
#     buy_sig = await asyncio.to_thread(trade.buy, public_key, private_key, mint_address, rpc_url)
#     print(f"\n--- Waiting 1.5 seconds before selling ---\n")
#     await asyncio.sleep(1.5)
#     sell_sig = await asyncio.to_thread(trade.sell, public_key, private_key, mint_address, rpc_url)
#     return buy_sig, sell_sig

# async def execute_trade_strategy(token_websocket_data, public_key, private_key, rpc_url):
#     """Handles the entire lifecycle for a watchlist token with maximum speed."""
#     mint_address = token_websocket_data.get('mint')
#     if not mint_address:
#         print("🚨 Cannot execute trade, mint address is missing.")
#         return

#     trade_task = asyncio.create_task(run_trade_cycle(public_key, private_key, mint_address, rpc_url))
    
#     print(f"📈 Watchlist hit for {token_websocket_data.get('symbol')}. Firing trade task immediately...")

#     token_db_data = {
#         'timestamp': timezone.now(),
#         'name': token_websocket_data.get('name', 'N/A'),
#         'symbol': token_websocket_data.get('symbol', 'N/A'),
#         'mint_address': mint_address,
#         'sol_amount': token_websocket_data.get('solAmount', 0),
#         'creator_address': token_websocket_data.get('traderPublicKey', 'N/A'),
#         'pump_fun_link': f"https://pump.fun/{mint_address}",
#         'is_from_watchlist': True
#     }
#     db_save_task = asyncio.create_task(save_token_to_db(token_db_data))

#     trade_signatures = await trade_task
#     token_object = await db_save_task
#     buy_signature, sell_signature = trade_signatures

#     if token_object:
#         print(f"✅ Trade and DB save complete for {token_object.symbol}. Starting post-trade actions.")
#         await asyncio.gather(
#             send_trade_notification_email(token_object, buy_signature, sell_signature),
#             collect_data_for_watchlist_coin(token_object)
#         )
#     else:
#         print(f"🚨 Could not run post-trade actions for {mint_address}, token object not available.")

# # --- CORRECTED MAIN LISTENER LOOP ---
# async def pump_fun_listener():
#     print("🎧 Starting Pump.fun WebSocket listener...")
#     async for websocket in websockets.connect(PUMPORTAL_WSS):
#         try:
#             await websocket.send(json.dumps({"method": "subscribeNewToken"}))
#             print("✅ WebSocket Connected and Subscribed.")
#             while True:
#                 message = await websocket.recv()
#                 data = json.loads(message)
#                 if data and data.get('txType') == 'create':
#                     creator_address = data.get('traderPublicKey', 'N/A')
                    
#                     # --- CORRECTED LOGIC ---
#                     if creator_address in WATCHLIST_CREATORS:
#                         # If it's a watchlist token, start the entire non-blocking strategy.
#                         asyncio.create_task(
#                             execute_trade_strategy(data, PUBLIC_KEY, PRIVATE_KEY, RPC_URL)
#                         )
#                     else:
#                         # If it's NOT a watchlist token, just save it to the database.
#                         # This 'await' is acceptable here because it's not a time-critical path.
#                         token_data = {
#                             'timestamp': timezone.now(),
#                             'name': data.get('name', 'N/A'),
#                             'symbol': data.get('symbol', 'N/A'),
#                             'mint_address': data.get('mint', 'N/A'),
#                             'sol_amount': data.get('solAmount', 0),
#                             'creator_address': creator_address,
#                             'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
#                             'is_from_watchlist': False
#                         }
#                         await save_token_to_db(token_data)

#         except websockets.ConnectionClosed:
#             print("⚠️ WebSocket connection closed. Reconnecting in 10 seconds...")
#             await asyncio.sleep(10)
#         except Exception as e:
#             print(f"💥 Main listener error: {e}. Reconnecting in 10 seconds...")
#             await asyncio.sleep(10)

# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------------------

# # --- Wrapper function to keep the listener running ---
# def run_listener_in_new_loop():
#     asyncio.run(pump_fun_listener())








































###########################################################################################################################

# pumplistener/listener.py

# import asyncio
# import websockets
# import json
# import os
# import httpx
# from asgiref.sync import sync_to_async
# from datetime import datetime, timedelta

# from django.utils import timezone
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
# from dotenv import load_dotenv

# from .models import Token, TokenDataPoint
# from . import trade

# import collections

# # --- Load Environment Variables ---
# load_dotenv()

# # --- CONFIGURATION ---
# PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"
# HELIUS_API_KEY = os.environ.get('HELIUS_API_KEY')
# HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
# PUBLIC_KEY = os.getenv("WALLET_PUBLIC_KEY")
# PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
# RPC_URL = os.getenv("RPC_URL")
# watchlist_str = os.environ.get('CREATOR_WATCHLIST', '')
# # WATCHLIST_CREATORS = set(filter(None, watchlist_str.split(',')))
# WATCHLIST_CREATORS = set(watchlist_str.split(','))
# moralis_keys_str = os.environ.get('MORALIS_API_KEYS', '')
# MORALIS_API_KEYS = [key.strip() for key in moralis_keys_str.split(',') if key.strip()]
# if not MORALIS_API_KEYS:
#     raise ValueError("🚨 No Moralis API keys found. Please set MORALIS_API_KEYS in .env file.")
# print(f"✅ Loaded {len(MORALIS_API_KEYS)} Moralis API keys.")
# moralis_key_lock = asyncio.Lock()
# current_moralis_key_index = 0

# # --- HELPER & API FUNCTIONS ---
# async def get_next_moralis_key():
#     """Gets the next Moralis API key from the list in a task-safe way."""
#     global current_moralis_key_index
#     async with moralis_key_lock:
#         key = MORALIS_API_KEYS[current_moralis_key_index]
#         current_moralis_key_index = (current_moralis_key_index + 1) % len(MORALIS_API_KEYS)
#         return key

# @sync_to_async
# def save_token_to_db(token_data):
#     """Saves token data to the database, getting or creating the token."""
#     token, created = Token.objects.get_or_create(
#         mint_address=token_data['mint_address'],
#         defaults=token_data
#     )
#     if created:
#         print(f"✅ Saved to DB: {token.name} ({token.symbol})")
#     return token

# @sync_to_async
# def send_trade_notification_email(token, buy_sig, sell_sig):
#     """Renders and sends an email report for a completed trade."""
#     recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
#     if not recipient_email:
#         print("⚠️ Cannot send trade notification, REPORT_RECIPIENT_EMAIL not set.")
#         return
#     print(f"📧 Preparing trade notification email for {token.symbol}...")
#     try:
#         subject = f"Watchlist Trade Alert: ${token.symbol}"
#         html_message = render_to_string('pumplistener/trade_notification_email.html', {
#             'token': token, 'buy_sig': buy_sig, 'sell_sig': sell_sig,
#         })
#         send_mail(
#             subject, "A trade was executed for a token on your watchlist.",
#             settings.DEFAULT_FROM_EMAIL, [recipient_email], html_message=html_message
#         )
#         print(f"✅ Trade notification for ${token.symbol} sent to {recipient_email}")
#     except Exception as e:
#         print(f"🚨 Failed to send trade notification email: {e}")

# async def get_helius_top_holders_count(mint_address: str):
#     """Fetches the top 20 largest accounts from Helius."""
#     payload = {"jsonrpc": "2.0", "id": "helius-v1", "method": "getTokenLargestAccounts", "params": [mint_address]}
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(HELIUS_RPC_URL, json=payload, timeout=10)
#             response.raise_for_status()
#             return {"source": "helius_getTokenLargestAccounts", "data": response.json()}
#         except Exception as e:
#             print(f"🚨 Error fetching from Helius: {e}")
#             return {"source": "helius_getTokenLargestAccounts", "error": str(e)}

# async def get_moralis_metadata(mint_address: str):
#     """Fetches metadata including FDV from Moralis using key rotation."""
#     url = f"https://solana-gateway.moralis.io/token/mainnet/{mint_address}/metadata"
#     api_key = await get_next_moralis_key()
#     headers = {"Accept": "application/json", "X-API-Key": api_key}
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers)
#             response.raise_for_status()
#             return {"source": "moralis_metadata", "data": response.json()}
#         except Exception as e:
#             print(f"🚨 Error fetching from Moralis (Metadata) with key ending in ...{api_key[-4:]}: {e}")
#             return {"source": "moralis_metadata", "error": str(e)}

# async def get_moralis_holder_stats(mint_address: str):
#     """Fetches detailed holder statistics from Moralis using key rotation."""
#     url = f"https://solana-gateway.moralis.io/token/mainnet/holders/{mint_address}"
#     api_key = await get_next_moralis_key()
#     headers = {"Accept": "application/json", "X-API-Key": api_key}
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers)
#             response.raise_for_status()
#             return {"source": "moralis_holder_stats", "data": response.json()}
#         except Exception as e:
#             print(f"🚨 Error fetching from Moralis (Holders) with key ending in ...{api_key[-4:]}: {e}")
#             return {"source": "moralis_holder_stats", "error": str(e)}

# # --- STRATEGY & DATA COLLECTION FUNCTIONS ---
# @sync_to_async
# def save_data_point(token: Token, api_data: dict):
#     """Saves a new data point for a given token."""
#     TokenDataPoint.objects.create(token=token, data=api_data)
#     print(f"💾 Saved data point for {token.symbol}: {api_data.get('source')}")
    
# # async def collect_data_for_watchlist_coin(token: Token):
# #     """Runs the 5-minute data collection process for a given token."""
# #     mint = token.mint_address
# #     print(f"📊 Starting 5-minute data collection for {token.symbol} ({mint})")
    
# #     await asyncio.sleep(30)
# #     print(f"  -> [{token.symbol}] Running T+30s check...")
# #     await save_data_point(token, await get_helius_top_holders_count(mint))
# #     await save_data_point(token, await get_moralis_metadata(mint))
    
# #     for i in range(9):
# #         await asyncio.sleep(30)
# #         check_time = (i + 2) * 30
# #         print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
# #         await save_data_point(token, await get_moralis_holder_stats(mint))

# #     print(f"✅ Finished 5-minute data collection for {token.symbol}")


# #######################################################################################################################
# #######################################################################################################################
# #######################################################################################################################

# # --- STRATEGY & DATA COLLECTION FUNCTIONS ---

# # async def refresh_token_state(token: Token):
# #     """Performs a single data refresh for a token and updates its state in the DB."""
# #     try:
# #         metadata, holders = await asyncio.gather(
# #             get_moralis_metadata(token.mint_address),
# #             get_moralis_holder_stats(token.mint_address)
# #         )
# #         await save_data_point(token, metadata)
# #         await save_data_point(token, holders)

# #         current_mc_str = metadata.get('data', {}).get('fullyDilutedValue')
# #         current_holders_str = holders.get('data', {}).get('total')

# #         if current_mc_str and current_holders_str:
# #             current_mc = float(current_mc_str)
# #             current_holders = int(current_holders_str)

# #             @sync_to_async
# #             def update_db():
# #                 # Use .select_for_update() to lock the row and prevent race conditions
# #                 t = Token.objects.select_for_update().get(pk=token.pk)
# #                 t.current_market_cap = current_mc
# #                 t.current_holder_count = current_holders
# #                 if not t.initial_market_cap:
# #                     t.initial_market_cap = current_mc
# #                 if not t.highest_market_cap or current_mc > t.highest_market_cap:
# #                     t.highest_market_cap = current_mc
# #                 t.save()
            
# #             await update_db()
# #             print(f"  -> Refreshed data for {token.symbol}: MC=${current_mc}, Holders={current_holders}")
# #     except Exception as e:
# #         print(f"  -> Could not parse API data during refresh for {token.symbol}: {e}")

# # 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

# # In pumplistener/listener.py

# # async def refresh_token_state(token: Token):
# #     """
# #     Performs a single data refresh for a token, fetching API data and updating its state in the DB.
# #     """
# #     try:
# #         metadata, holders = await asyncio.gather(
# #             get_moralis_metadata(token.mint_address),
# #             get_moralis_holder_stats(token.mint_address)
# #         )
# #         await save_data_point(token, metadata)
# #         await save_data_point(token, holders)

# #         # --- NEW: Check for API errors before parsing ---
# #         if 'error' in metadata or 'error' in holders:
# #             print(f"  -> Skipping state update for {token.symbol} due to API error.")
# #             return

# #         current_mc_str = metadata.get('data', {}).get('fullyDilutedValue')
# #         current_holders_str = holders.get('data', {}).get('total')

# #         if current_mc_str and current_holders_str:
# #             current_mc = float(current_mc_str)
# #             current_holders = int(current_holders_str)

# #             @sync_to_async
# #             def update_db():
# #                 t = Token.objects.select_for_update().get(pk=token.pk)
# #                 t.current_market_cap = current_mc
# #                 t.current_holder_count = current_holders
# #                 if not t.initial_market_cap:
# #                     t.initial_market_cap = current_mc
# #                 if not t.highest_market_cap or current_mc > t.highest_market_cap:
# #                     t.highest_market_cap = current_mc
# #                 t.save()
            
# #             await update_db()
# #             print(f"  -> Refreshed data for {token.symbol}: MC=${current_mc}, Holders={current_holders}")
# #     except Exception as e:
# #         print(f"  -> Could not parse API data during refresh for {token.symbol}: {e}")


# # ======================================================================================================================

# async def refresh_token_state(token: Token):
#     """Performs a single data refresh for a token and updates its state in the DB."""
#     try:
#         metadata, holders = await asyncio.gather(
#             get_moralis_metadata(token.mint_address),
#             get_moralis_holder_stats(token.mint_address)
#         )
#         await save_data_point(token, metadata)
#         await save_data_point(token, holders)

#         if 'error' in metadata or 'error' in holders:
#             print(f"  -> Skipping state update for {token.symbol} due to API error.")
#             return

#         current_mc_str = metadata.get('data', {}).get('fullyDilutedValue')
#         current_holders_str = holders.get('data', {}).get('total')

#         if current_mc_str and current_holders_str:
#             current_mc = float(current_mc_str)
#             current_holders = int(current_holders_str)

#             @sync_to_async
#             def update_db():
#                 t = Token.objects.select_for_update().get(pk=token.pk)
#                 t.current_market_cap = current_mc
#                 t.current_holder_count = current_holders
#                 if not t.initial_market_cap:
#                     t.initial_market_cap = current_mc
#                 if not t.highest_market_cap or current_mc > t.highest_market_cap:
#                     t.highest_market_cap = current_mc
#                 # --- NEW: Track peak holder count ---
#                 if not t.peak_holder_count or current_holders > t.peak_holder_count:
#                     t.peak_holder_count = current_holders
#                 t.save()
            
#             await update_db()
#             print(f"  -> Refreshed data for {token.symbol}: MC=${current_mc}, Holders={current_holders}")
#     except Exception as e:
#         print(f"  -> Could not parse API data during refresh for {token.symbol}: {e}")



# # 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000


# # async def collect_data_for_watchlist_coin(token: Token):
# #     """
# #     MODIFIED: Acts as the High-Frequency monitor for the first 10 minutes.
# #     """
# #     print(f"📊 Starting 10-MINUTE HIGH-FREQUENCY monitoring for {token.symbol} ({token.mint_address})")

# #     # Run a check every 15 seconds for 10 minutes (40 checks total)
# #     for i in range(40):
# #     # 0000000000000000000000000000000000000000000000000000000000000000000
# #     # for i in range(3):
# #     # 00000000000000000000000000000000000000000000000000000000000000000000
# #         await asyncio.sleep(15)
# #         check_time = (i + 1) * 15
# #         print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
        
# #         await refresh_token_state(token)
        
# #         # To check rules, we need the most up-to-date version from the DB
# #         refreshed_token = await Token.objects.aget(pk=token.pk)

# #         # --- SIMULATION: Check sell rules ---
# #         if refreshed_token.initial_market_cap and refreshed_token.current_market_cap:
# #             if refreshed_token.current_market_cap >= refreshed_token.initial_market_cap * 2:
# #                 print(f"  -> 🚨 SIMULATION: Would sell {refreshed_token.symbol} for 2x profit!")
# #                 # In the future, a real `trade.sell()` call and a `break` would go here.

# #     print(f"✅ Finished 10-minute high-frequency monitoring for {token.symbol}")

# # ************************************************************************************************************************

# # In pumplistener/listener.py

# async def collect_data_for_watchlist_coin(token: Token):
#     """
#     MODIFIED: Now returns the reason for a simulated sell.
#     """
#     print(f"📊 Starting 10-MINUTE HIGH-FREQUENCY monitoring for {token.symbol}...")
    
#     sell_triggered = False
#     sell_reason = None # Initialize sell_reason
#     holder_history = collections.deque(maxlen=4)
#     sell_trigger_timestamp = None # <-- Initialize timestamp variable

#     # for i in range(40):
#     # 000000000000000000000000000000000000000000000000000000000000000000000000
#     for i in range(3):
#     # 000000000000000000000000000000000000000000000000000000000000000000000000
#         # ... (rest of the loop and rules are the same) ...
#         await asyncio.sleep(15)
#         check_time = (i + 1) * 15
#         print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
        
#         await refresh_token_state(token)
        
#         refreshed_token = await Token.objects.aget(pk=token.pk)
        
#         # Add the latest holder count to our history
#         if refreshed_token.current_holder_count is not None:
#             holder_history.append(refreshed_token.current_holder_count)

#         # --- STRATEGY SIMULATION ---
#         # Only check rules if a sell hasn't already been triggered
#         if not sell_triggered:
#             sell_reason = None
            
#             # Rule 1: 30-Second "Viability Gate" (runs on the 2nd check, which is at T+30s)
#             if i == 1 and refreshed_token.current_holder_count < 12 and refreshed_token.current_market_cap < 12000:
#                 sell_reason = "Failed 30-Second Viability Gate(<12 holders & MC<$12k)"
            
#             # Rule 2: Absolute Market Cap Stop-Loss
#             elif refreshed_token.current_market_cap and refreshed_token.current_market_cap < 12000:
#                 sell_reason = "Absolute Market Cap Stop-Loss triggered(MC<$12k)"

#             # Rule 3: Trailing Market Cap Stop-Loss
#             elif refreshed_token.highest_market_cap and refreshed_token.current_market_cap < (refreshed_token.highest_market_cap * 0.55): # 45% drop
#                 sell_reason = f"Trailing MC Stop-Loss triggered (Dropped 45% from peak of ${refreshed_token.highest_market_cap:,.2f})"

#             # Rule 4: Peak Holder Stop-Loss
#             elif refreshed_token.peak_holder_count and refreshed_token.current_holder_count < (refreshed_token.peak_holder_count * 0.60): # 40% drop
#                 sell_reason = f"Peak Holder Stop-Loss triggered (Dropped 40% from peak of {refreshed_token.peak_holder_count} holders)"

#             # Rule 5: Rapid Holder Decline
#             elif len(holder_history) == 4: # Ensure we have enough data points
#                 last_3_checks = list(holder_history)[:3]
#                 lowest_in_last_3 = min(last_3_checks)
#                 if refreshed_token.current_holder_count < (lowest_in_last_3 * 0.75): # 25% drop from recent low
#                     sell_reason = f"Rapid Holder Decline detected (Dropped >25% from recent low of {lowest_in_last_3} holders in last 45s)"

#             if sell_reason:
#                 print(f"  -> 🚨 SIMULATION: SELL {refreshed_token.symbol} | Reason: {sell_reason}")
#                 sell_triggered = True
#                 sell_trigger_timestamp = timezone.now() # <-- CAPTURE the timestamp here
#             else:
#                 print(f"  -> ✅ SIMULATION: HOLD {refreshed_token.symbol}")

#     print(f"✅ Finished 10-minute high-frequency monitoring for {token.symbol}")
#     return sell_reason, sell_trigger_timestamp # <-- ADD THIS RETURN STATEMENT
# ###################################################################################################################
# ###################################################################################################################
# ###################################################################################################################
# # --- NEW: Orchestrator to run the full trade cycle without blocking the listener ---

# async def run_trade_cycle(public_key, private_key, mint_address, rpc_url):
#     """A dedicated async function just for the buy/sell logic."""
#     buy_sig = await asyncio.to_thread(trade.buy, public_key, private_key, mint_address, rpc_url)
#     buy_time = timezone.now() + timedelta(hours=5, minutes=30)
#     print(f"\n--- Waiting 1.5 seconds before selling ---\n")
#     await asyncio.sleep(1.5)
#     sell_sig = await asyncio.to_thread(trade.sell, public_key, private_key, mint_address, rpc_url)
#     return buy_sig, sell_sig, buy_time

# # 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

# # async def monitor_and_report(token_object, buy_signature, sell_signature):
# #     """
# #     A dedicated background task that first runs the 10-minute monitoring,
# #     and then sends the final summary email.
# #     """
# #     print(f"✅ Trade complete for {token_object.symbol}. Starting post-trade actions in the background...")
    
# #     # 1. First, complete the 10-minute data collection.
# #     await collect_data_for_watchlist_coin(token_object)
    
# #     # 2. THEN, send the email, which will now contain all the collected data.
# #     await send_trade_notification_email(token_object, buy_signature, sell_signature)

# async def monitor_and_report(token_object, buy_signature, sell_signature):
#     """
#     MODIFIED: Captures and passes the sell_reason and trigger_timestamp.
#     """
#     print(f"✅ Trade complete for {token_object.symbol}. Starting post-trade actions in the background...")
    
#     # 1. Capture both returned values.
#     sell_reason, sell_trigger_timestamp = await collect_data_for_watchlist_coin(token_object)
    
#     # 2. Pass both values to the email function.
#     await send_trade_notification_email(token_object, buy_signature, sell_signature, sell_reason, sell_trigger_timestamp)

# # 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# async def execute_trade_strategy(token_websocket_data, public_key, private_key, rpc_url):
#     """Handles the entire lifecycle for a watchlist token."""
#     mint_address = token_websocket_data.get('mint')
#     if not mint_address:
#         return
    
#     trade_task = asyncio.create_task(run_trade_cycle(public_key, private_key, mint_address, rpc_url))
#     print(f"📈 Watchlist hit for {token_websocket_data.get('symbol')}. Firing trade task immediately...")
    
#     token_db_data = {
#         'timestamp': timezone.now() + timedelta(hours=5, minutes=30), # Correct UTC timestamp
#         'name': token_websocket_data.get('name', 'N/A'), 
#         'symbol': token_websocket_data.get('symbol', 'N/A'),
#         'mint_address': mint_address,
#         'sol_amount': token_websocket_data.get('solAmount') or 0,
#         'creator_address': token_websocket_data.get('traderPublicKey', 'N/A'),
#         'pump_fun_link': f"https://pump.fun/{mint_address}",
#         'is_from_watchlist': True
#     }
    
#     # --- Execute Trade and DB Save in Parallel ---
#     db_save_task = asyncio.create_task(save_token_to_db(token_db_data))
#     trade_signatures = await trade_task
#     token_object = await db_save_task
    
#     # This will now work correctly without a ValueError
#     buy_signature, sell_signature, buy_timestamp = trade_signatures

#     if token_object:
#         if buy_signature:
#             token_object.buy_timestamp = buy_timestamp
#             await token_object.asave()

#         # --- Fire and forget the long-running monitoring and reporting task ---
#         # This function now exits immediately, keeping the main listener free.
#         asyncio.create_task(
#             monitor_and_report(token_object, buy_signature, sell_signature)
#         )
#     else:
#         print(f"🚨 Could not start post-trade actions for {mint_address} because token object was not saved.")

# # 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

# # In pumplistener/listener.py

# # async def execute_trade_strategy(token_websocket_data, public_key, private_key, rpc_url):
# #     """
# #     MODIFIED: Now completes monitoring BEFORE sending the email summary.
# #     """
# #     # ... (the pre-flight check and trading logic remains the same)
# #     mint_address = token_websocket_data.get('mint')
# #     if not mint_address: return
    
# #     # ... (code to check MAX_BUY_MARKET_CAP)
# #     trade_task = asyncio.create_task(run_trade_cycle(public_key, private_key, mint_address, rpc_url))

# #     print(f"📈 Watchlist hit for {token_websocket_data.get('symbol')}. Firing trade task immediately...")

# #     token_db_data = {
# #         # 'timestamp': timezone.now(),
# #         'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
# #         'name': token_websocket_data.get('name', 'N/A'),
# #         'symbol': token_websocket_data.get('symbol', 'N/A'),
# #         'mint_address': mint_address,
# #         'sol_amount': token_websocket_data.get('solAmount') or 0, # <-- APPLY FIX HERE
# #         'creator_address': token_websocket_data.get('traderPublicKey', 'N/A'),
# #         'pump_fun_link': f"https://pump.fun/{mint_address}",
# #         'is_from_watchlist': True
# #     }

# #     db_save_task = asyncio.create_task(save_token_to_db(token_db_data)) # token_db_data must be defined here

# #     trade_signatures = await trade_task
# #     token_object = await db_save_task
# #     buy_signature, sell_signature, buy_timestamp = trade_signatures

# #     if token_object:
# #         if buy_signature:
# #             token_object.buy_timestamp = buy_timestamp
# #             await token_object.asave()

# #         # --- THIS IS THE NEW SEQUENCE ---
# #         # 1. First, complete the 10-minute data collection.
# #         print(f"✅ Trade and DB save complete for {token_object.symbol}. Starting post-trade data collection...")
# #         await collect_data_for_watchlist_coin(token_object)
        
# #         # 2. THEN, send the email, which will now contain all the collected data.
# #         await send_trade_notification_email(token_object, buy_signature, sell_signature)
# #     else:
# #         print(f"🚨 Could not run post-trade actions for {mint_address}, token object not available.")

# # 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

# # async def execute_trade_strategy(token_websocket_data, public_key, private_key, rpc_url):
# #     """Handles the entire lifecycle for a watchlist token with maximum speed."""
# #     mint_address = token_websocket_data.get('mint')
# #     if not mint_address:
# #         print("🚨 Cannot execute trade, mint address is missing.")
# #         return

# #     trade_task = asyncio.create_task(run_trade_cycle(public_key, private_key, mint_address, rpc_url))

# #     print(f"📈 Watchlist hit for {token_websocket_data.get('symbol')}. Firing trade task immediately...")

# #     token_db_data = {
# #         # 'timestamp': timezone.now(),
# #         'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
# #         'name': token_websocket_data.get('name', 'N/A'),
# #         'symbol': token_websocket_data.get('symbol', 'N/A'),
# #         'mint_address': mint_address,
# #         # 'sol_amount': token_websocket_data.get('solAmount', 0),
# #         'sol_amount': token_websocket_data.get('solAmount') or 0, # <-- APPLY FIX HERE
# #         'creator_address': token_websocket_data.get('traderPublicKey', 'N/A'),
# #         'pump_fun_link': f"https://pump.fun/{mint_address}",
# #         'is_from_watchlist': True
# #     }
# #     db_save_task = asyncio.create_task(save_token_to_db(token_db_data))

# #     trade_signatures = await trade_task
# #     token_object = await db_save_task
# #     buy_signature, sell_signature = trade_signatures

# #     if token_object:
# #         print(f"✅ Trade and DB save complete for {token_object.symbol}. Starting post-trade actions.")
# #         await asyncio.gather(
# #             send_trade_notification_email(token_object, buy_signature, sell_signature),
# #             collect_data_for_watchlist_coin(token_object)
# #         )
# #     else:
# #         print(f"🚨 Could not run post-trade actions for {mint_address}, token object not available.")

# # ====================================================================================================================

# # In pumplistener/listener.py

# # async def execute_trade_strategy(token_websocket_data, public_key, private_key, rpc_url):
# #     """
# #     MODIFIED: Now completes monitoring BEFORE sending the email summary.
# #     """
# #     mint_address = token_websocket_data.get('mint')
# #     if not mint_address:
# #         print("🚨 Cannot execute trade, mint address is missing.")
# #         return

# #     trade_task = asyncio.create_task(run_trade_cycle(public_key, private_key, mint_address, rpc_url))
# #     print(f"📈 Watchlist hit for {token_websocket_data.get('symbol')}. Firing trade task immediately...")
    
# #     token_db_data = {
# #         # 'timestamp': timezone.now(),
# #         'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
# #         'name': token_websocket_data.get('name', 'N/A'),
# #         'symbol': token_websocket_data.get('symbol', 'N/A'),
# #         'mint_address': mint_address,
# #         'sol_amount': token_websocket_data.get('solAmount') or 0,
# #         'creator_address': token_websocket_data.get('traderPublicKey', 'N/A'),
# #         'pump_fun_link': f"https://pump.fun/{mint_address}",
# #         'is_from_watchlist': True
# #     }

# #     db_save_task = asyncio.create_task(save_token_to_db(token_db_data))

# #     # Wait for the trade and the initial DB save to complete
# #     trade_signatures = await trade_task
# #     token_object = await db_save_task
# #     buy_signature, sell_signature, buy_timestamp = trade_signatures

# #     if token_object:
# #         # Update the token with the buy_timestamp
# #         if buy_signature:
# #             token_object.buy_timestamp = buy_timestamp
# #             await token_object.asave()

# #         # --- NEW SEQUENCE ---
# #         # 1. First, complete the 10-minute data collection.
# #         print(f"✅ Trade and DB save complete for {token_object.symbol}. Starting post-trade data collection...")
# #         # ********************************************************************************************************
# #         # await collect_data_for_watchlist_coin(token_object)
        
# #         # # 2. THEN, send the email, which will now contain all the collected data.
# #         # await send_trade_notification_email(token_object, buy_signature, sell_signature)

# #         # ========================================================================================================
        
# #         await asyncio.gather(
# #             send_trade_notification_email(token_object, buy_signature, sell_signature),
# #             collect_data_for_watchlist_coin(token_object)
# #         )
# #         # ********************************************************************************************************
# #     else:
# #         print(f"🚨 Could not run post-trade actions for {mint_address}, token object not available.")

# ###################################################################################################################
# # In listener.py

# # async def collect_data_for_watchlist_coin(token: Token):
# #     """
# #     MODIFIED: Now acts as the High-Frequency monitor and sell-checker for the first 5 minutes.
# #     """
# #     mint = token.mint_address
# #     print(f"📊 Starting HIGH-FREQUENCY monitoring for {token.symbol} ({mint})")
    
# #     # Run a check every 30 seconds for 5 minutes (10 checks total)
# #     for i in range(10):
# #         await asyncio.sleep(30)
# #         check_time = (i + 1) * 30
# #         print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
        
# #         # Fetch latest market data
# #         metadata = await get_moralis_metadata(mint)
# #         holders = await get_moralis_holder_stats(mint)
        
# #         # Save the raw data points
# #         await save_data_point(token, metadata)
# #         await save_data_point(token, holders)

# #         # --- NEW LOGIC: Parse and update the Token's state in the DB ---
# #         try:
# #             current_mc_str = metadata.get('data', {}).get('fullyDilutedValue')
# #             current_holders_str = holders.get('data', {}).get('total')

# #             if current_mc_str and current_holders_str:
# #                 current_mc = float(current_mc_str)
# #                 current_holders = int(current_holders_str)

# #                 # Use sync_to_async to safely update the database record
# #                 @sync_to_async
# #                 def update_token_state():
# #                     # Refresh the token object from the DB to avoid race conditions
# #                     t = Token.objects.get(pk=token.pk)
# #                     t.current_market_cap = current_mc
# #                     t.current_holder_count = current_holders
                    
# #                     if not t.initial_market_cap:
# #                         t.initial_market_cap = current_mc
                    
# #                     if not t.highest_market_cap or current_mc > t.highest_market_cap:
# #                         t.highest_market_cap = current_mc
                    
# #                     t.save()
# #                     return t
                
# #                 token = await update_token_state()

# #                 # --- SIMULATION: Check sell rules ---
# #                 if token.initial_market_cap and token.current_market_cap > token.initial_market_cap * 2:
# #                     print(f"  -> 🚨 SIMULATION: Would sell {token.symbol} for 2x profit!")
# #                     # In the future, a real `trade.sell()` call would go here.
# #                     # After a successful sell, we would break the loop.
        
# #         except (ValueError, TypeError, KeyError) as e:
# #             print(f"  -> Could not parse API data for {token.symbol}: {e}")

# #     print(f"✅ Finished high-frequency monitoring for {token.symbol}")



# # ********************************************************************************************************************
# # ********************************************************************************************************************
# # Replace the old version of this function with this simpler one
# @sync_to_async
# def send_trade_notification_email(token, buy_sig, sell_sig, sell_reason, sell_trigger_timestamp):
#     """
#     Renders and sends a trade notification email using the default Mailjet backend.
#     """
#     recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
#     if not recipient_email:
#         print("⚠️ Cannot send trade notification, REPORT_RECIPIENT_EMAIL not set.")
#         return

#     print(f"📧 Preparing trade notification email for {token.symbol}...")
#     try:
#         subject = f"Watchlist Trade Alert: ${token.symbol}"
#         html_message = render_to_string('pumplistener/trade_notification_email.html', {
#             'token': token, 
#             'buy_sig': buy_sig, 
#             'sell_sig': sell_sig,
#             'sell_reason': sell_reason,
#             'sell_trigger_timestamp': sell_trigger_timestamp,
#         })
        
#         send_mail(
#             subject=subject,
#             message="This email requires an HTML-compatible client.", # Plain text fallback
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[recipient_email],
#             html_message=html_message
#         )
#         print(f"✅ Trade notification for ${token.symbol} sent to {recipient_email}")
#     except Exception as e:
#         print(f"🚨 Failed to send trade notification email: {e}")

# #####################################################################################################################

# # --- MAIN LISTENER LOOP ---
# async def pump_fun_listener():
#     print("🎧 Starting Pump.fun WebSocket listener...")
#     async for websocket in websockets.connect(PUMPORTAL_WSS):
#         try:
#             await websocket.send(json.dumps({"method": "subscribeNewToken"}))
#             print("✅ WebSocket Connected and Subscribed.")
#             # --- TEMPORARY TEST FLAG ---
#             # 0000000000000000000000000000000000000000
#             has_triggered_test = False
#             # 00000000000000000000000000000000000000000
#             while True:
#                 message = await websocket.recv()
#                 data = json.loads(message)
#                 if data and data.get('txType') == 'create':
#                     creator_address = data.get('traderPublicKey', 'N/A')
                    
#                     # if creator_address in WATCHLIST_CREATORS:
#                     # 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#                     if not has_triggered_test:
#                         has_triggered_test = True # Set flag so it only runs once
#                     # 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#                         ############################################################################################
#                         # If it's a watchlist token, start the entire non-blocking strategy.
#                         asyncio.create_task(
#                             execute_trade_strategy(data, PUBLIC_KEY, PRIVATE_KEY, RPC_URL)
#                         )
#                         ############################################################################################
#                         # TO Disable trading, we may comment out the above section, and execute only data saving below.
#                             # --- Add this logic to save the token and start data collection ---
#                         # token_data = {
#                         #     'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
#                         #     'name': data.get('name', 'N/A'),
#                         #     'symbol': data.get('symbol', 'N/A'),
#                         #     'mint_address': data.get('mint', 'N/A'),
#                         #     'sol_amount': data.get('solAmount') or 0,
#                         #     'creator_address': creator_address,
#                         #     'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
#                         #     'is_from_watchlist': True # Still mark it as a watchlist token
#                         # }
                        
#                         # token_object = await save_token_to_db(token_data)

#                         # 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#                         # await collect_data_for_watchlist_coin(token_object)
#                         # await send_trade_notification_email(token_object, "N/A", "N/A")
#                         # 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

                        
#                         # if token_object:
#                         #     # Start the 5-minute data collection without trading
#                         #     asyncio.create_task(collect_data_for_watchlist_coin(token_object))
#                         ############################################################################################
#                     else:
#                         # If it's NOT a watchlist token, just save it to the database.
#                         token_data = {
#                             # 'timestamp': timezone.now(),
#                             'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
#                             'name': data.get('name', 'N/A'),
#                             'symbol': data.get('symbol', 'N/A'),
#                             'mint_address': data.get('mint', 'N/A'),
#                             # 'sol_amount': data.get('solAmount', 0),
#                             'sol_amount': data.get('solAmount') or 0, # <-- APPLY FIX HERE
#                             'creator_address': creator_address,
#                             'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
#                             'is_from_watchlist': False
#                         }
#                         await save_token_to_db(token_data)
#         except websockets.ConnectionClosed:
#             print("⚠️ WebSocket connection closed. Reconnecting in 5 seconds...")
#             await asyncio.sleep(5)
#         except Exception as e:
#             print(f"💥 Main listener error: {e}. Reconnecting in 5 seconds...")
#             await asyncio.sleep(5)

# def run_listener_in_new_loop():
#     """Wrapper to run the async listener in a new asyncio event loop."""
#     asyncio.run(pump_fun_listener())















































































































########################################################################################################################################################################################

# pumplistener/listener.py

# import asyncio
# import websockets
# import json
# import os
# import httpx
# from asgiref.sync import sync_to_async
# from datetime import datetime, timedelta

# from django.utils import timezone
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
# from dotenv import load_dotenv

# from .models import Token, TokenDataPoint
# from . import trade

# import collections

# # --- Load Environment Variables ---
# load_dotenv()

# # --- CONFIGURATION ---
# PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"
# HELIUS_API_KEY = os.environ.get('HELIUS_API_KEY')
# HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
# PUBLIC_KEY = os.getenv("WALLET_PUBLIC_KEY")
# PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
# RPC_URL = os.getenv("RPC_URL")
# watchlist_str = os.environ.get('CREATOR_WATCHLIST', '')
# # WATCHLIST_CREATORS = set(filter(None, watchlist_str.split(',')))
# WATCHLIST_CREATORS = set(watchlist_str.split(','))
# moralis_keys_str = os.environ.get('MORALIS_API_KEYS', '')
# MORALIS_API_KEYS = [key.strip() for key in moralis_keys_str.split(',') if key.strip()]
# if not MORALIS_API_KEYS:
#     raise ValueError("🚨 No Moralis API keys found. Please set MORALIS_API_KEYS in .env file.")
# print(f"✅ Loaded {len(MORALIS_API_KEYS)} Moralis API keys.")
# moralis_key_lock = asyncio.Lock()
# current_moralis_key_index = 0

# # --- HELPER & API FUNCTIONS ---
# async def get_next_moralis_key():
#     """Gets the next Moralis API key from the list in a task-safe way."""
#     global current_moralis_key_index
#     async with moralis_key_lock:
#         key = MORALIS_API_KEYS[current_moralis_key_index]
#         current_moralis_key_index = (current_moralis_key_index + 1) % len(MORALIS_API_KEYS)
#         return key

# @sync_to_async
# def save_token_to_db(token_data):
#     """Saves token data to the database, getting or creating the token."""
#     token, created = Token.objects.get_or_create(
#         mint_address=token_data['mint_address'],
#         defaults=token_data
#     )
#     if created:
#         print(f"✅ Saved to DB: {token.name} ({token.symbol})")
#     return token

# @sync_to_async
# def send_trade_notification_email(token, buy_sig, sell_sig, sell_reason, sell_trigger_timestamp):
#     recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
#     if not recipient_email:
#         print("⚠️ Cannot send trade notification, REPORT_RECIPIENT_EMAIL not set.")
#         return

#     print(f"📧 Preparing trade notification email for {token.symbol}...")
#     subject = f"Watchlist Trade Alert: ${token.symbol}"
#     html_message = render_to_string('pumplistener/trade_notification_email.html', {
#         'token': token, 'buy_sig': buy_sig, 'sell_sig': sell_sig,
#         'sell_reason': sell_reason, 'sell_trigger_timestamp': sell_trigger_timestamp
#     })
    
#     try:
#         send_mail(
#             subject, "A trade was executed for a token on your watchlist.",
#             settings.DEFAULT_FROM_EMAIL, [recipient_email], html_message=html_message
#         )
#         print(f"✅ Trade notification for ${token.symbol} sent to {recipient_email}")
#     except Exception as e:
#         print(f"🚨 Failed to send trade notification email: {e}")

# async def get_helius_top_holders_count(mint_address: str):
#     """Fetches the top 20 largest accounts from Helius."""
#     payload = {"jsonrpc": "2.0", "id": "helius-v1", "method": "getTokenLargestAccounts", "params": [mint_address]}
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(HELIUS_RPC_URL, json=payload, timeout=10)
#             response.raise_for_status()
#             return {"source": "helius_getTokenLargestAccounts", "data": response.json()}
#         except Exception as e:
#             print(f"🚨 Error fetching from Helius: {e}")
#             return {"source": "helius_getTokenLargestAccounts", "error": str(e)}

# async def get_moralis_metadata(mint_address: str):
#     """Fetches metadata including FDV from Moralis using key rotation."""
#     url = f"https://solana-gateway.moralis.io/token/mainnet/{mint_address}/metadata"
#     api_key = await get_next_moralis_key()
#     headers = {"Accept": "application/json", "X-API-Key": api_key}
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers)
#             response.raise_for_status()
#             return {"source": "moralis_metadata", "data": response.json()}
#         except Exception as e:
#             print(f"🚨 Error fetching from Moralis (Metadata) with key ending in ...{api_key[-4:]}: {e}")
#             return {"source": "moralis_metadata", "error": str(e)}

# async def get_moralis_holder_stats(mint_address: str):
#     """Fetches detailed holder statistics from Moralis using key rotation."""
#     url = f"https://solana-gateway.moralis.io/token/mainnet/holders/{mint_address}"
#     api_key = await get_next_moralis_key()
#     headers = {"Accept": "application/json", "X-API-Key": api_key}
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers)
#             response.raise_for_status()
#             return {"source": "moralis_holder_stats", "data": response.json()}
#         except Exception as e:
#             print(f"🚨 Error fetching from Moralis (Holders) with key ending in ...{api_key[-4:]}: {e}")
#             return {"source": "moralis_holder_stats", "error": str(e)}

# # --- STRATEGY & DATA COLLECTION FUNCTIONS ---
# # @sync_to_async
# # def save_data_point(token: Token, api_data: dict):
# #     """Saves a new data point for a given token."""
# #     TokenDataPoint.objects.create(token=token, data=api_data)
# #     print(f"💾 Saved data point for {token.symbol}: {api_data.get('source')}")

# @sync_to_async
# def save_data_point(token: Token, api_data: dict):
#     """MODIFIED: Saves a new data point and returns the created object."""
#     data_point = TokenDataPoint.objects.create(token=token, data=api_data)
#     print(f"💾 Saved data point for {token.symbol}: {api_data.get('source')}")
#     return data_point

# # async def refresh_token_state(token: Token):
# #     """Performs a single data refresh for a token and updates its state in the DB."""
# #     try:
# #         metadata, holders = await asyncio.gather(
# #             get_moralis_metadata(token.mint_address),
# #             get_moralis_holder_stats(token.mint_address)
# #         )
# #         await save_data_point(token, metadata)
# #         await save_data_point(token, holders)

# #         if 'error' in metadata or 'error' in holders:
# #             print(f"  -> Skipping state update for {token.symbol} due to API error.")
# #             return

# #         current_mc_str = metadata.get('data', {}).get('fullyDilutedValue')
# #         # current_holders_str = holders.get('data', {}).get('total')
# #         current_holders_str = holders.get('data', {}).get('totalHolders')

# #         if current_mc_str and current_holders_str:
# #             current_mc = float(current_mc_str)
# #             current_holders = int(current_holders_str)

# #             @sync_to_async
# #             def update_db():
# #                 t = Token.objects.select_for_update().get(pk=token.pk)
# #                 t.current_market_cap = current_mc
# #                 t.current_holder_count = current_holders
# #                 if not t.initial_market_cap:
# #                     t.initial_market_cap = current_mc
# #                 if not t.highest_market_cap or current_mc > t.highest_market_cap:
# #                     t.highest_market_cap = current_mc
# #                 if not t.peak_holder_count or current_holders > t.peak_holder_count:
# #                     t.peak_holder_count = current_holders
# #                 t.save()
            
# #             await update_db()
# #             print(f"  -> Refreshed data for {token.symbol}: MC=${current_mc}, Holders={current_holders}")
# #     except Exception as e:
# #         print(f"  -> Could not parse API data during refresh for {token.symbol}: {e}")

# async def refresh_token_state(token: Token):
#     """MODIFIED: Returns the two data point objects it creates."""
#     try:
#         metadata, holders = await asyncio.gather(
#             get_moralis_metadata(token.mint_address),
#             get_moralis_holder_stats(token.mint_address)
#         )
#         # Capture the returned data point objects
#         metadata_point = await save_data_point(token, metadata)
#         holders_point = await save_data_point(token, holders)

#         if 'error' in metadata or 'error' in holders:
#             print(f"  -> Skipping state update for {token.symbol} due to API error.")
#             # Still return the points so they can be logged in the email
#             return metadata_point, holders_point

#         current_mc_str = metadata.get('data', {}).get('fullyDilutedValue')
#         current_holders_str = holders.get('data', {}).get('totalHolders')

#         if current_mc_str and current_holders_str is not None:
#             current_mc = float(current_mc_str)
#             current_holders = int(current_holders_str)

#             @sync_to_async
#             def update_db():
#                 t = Token.objects.select_for_update().get(pk=token.pk)
#                 t.current_market_cap = current_mc
#                 t.current_holder_count = current_holders
#                 if not t.initial_market_cap:
#                     t.initial_market_cap = current_mc
#                 if not t.highest_market_cap or current_mc > t.highest_market_cap:
#                     t.highest_market_cap = current_mc
#                 if not t.peak_holder_count or current_holders > t.peak_holder_count:
#                     t.peak_holder_count = current_holders
#                 t.save()
            
#             await update_db()
#             print(f"  -> Refreshed data for {token.symbol}: MC=${current_mc}, Holders={current_holders}")
        
#         # Return the created database objects
#         return metadata_point, holders_point
#     except Exception as e:
#         print(f"  -> Could not parse API data during refresh for {token.symbol}: {e}")
#         return None, None


# # async def collect_data_for_watchlist_coin(token: Token):
# #     """Acts as the High-Frequency monitor and returns the sell reason."""
# #     print(f"📊 Starting 10-MINUTE HIGH-FREQUENCY monitoring for {token.symbol}...")
    
# #     sell_triggered = False
# #     sell_reason = None
# #     sell_trigger_timestamp = None
# #     holder_history = collections.deque(maxlen=4)

# #     # for i in range(40):
# #     # 000000000000000000000000000000000000000000000000000000000000000000000
# #     for i in range(3):
# #     # 000000000000000000000000000000000000000000000000000000000000000000000
# #         await asyncio.sleep(15)
# #         check_time = (i + 1) * 15
# #         print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
# #         await refresh_token_state(token)
# #         refreshed_token = await Token.objects.aget(pk=token.pk)
        
# #         if refreshed_token.current_holder_count is not None:
# #             holder_history.append(refreshed_token.current_holder_count)

# #         if not sell_triggered:
# #             current_reason = None
# #             # --- FIXED: Check that values are not None before comparing ---
# #             if (i == 1 and refreshed_token.current_holder_count is not None and refreshed_token.current_market_cap is not None
# #                     and refreshed_token.current_holder_count < 12 and refreshed_token.current_market_cap < 12000):
# #                 current_reason = "Failed 30-Second Viability Gate"
# #             elif refreshed_token.current_market_cap is not None and refreshed_token.current_market_cap < 12000:
# #                 current_reason = "Absolute Market Cap Stop-Loss (< $12k)"
# #             elif (refreshed_token.highest_market_cap is not None and refreshed_token.current_market_cap is not None
# #                   and refreshed_token.current_market_cap < (refreshed_token.highest_market_cap * 0.55)):
# #                 current_reason = f"Trailing MC Stop-Loss (>45% drop from peak of ${refreshed_token.highest_market_cap:,.2f})"
# #             elif (refreshed_token.peak_holder_count is not None and refreshed_token.current_holder_count is not None
# #                   and refreshed_token.current_holder_count < (refreshed_token.peak_holder_count * 0.60)):
# #                 current_reason = f"Peak Holder Stop-Loss (>40% drop from peak of {refreshed_token.peak_holder_count})"
# #             elif len(holder_history) >= 4:
# #                 lowest_in_last_3 = min(list(holder_history)[:3])
# #                 if refreshed_token.current_holder_count < (lowest_in_last_3 * 0.75):
# #                     current_reason = f"Rapid Holder Decline (>25% drop from recent low of {lowest_in_last_3})"
            
# #             if current_reason:
# #                 sell_reason = current_reason
# #                 sell_triggered = True
# #                 sell_trigger_timestamp = timezone.now()
# #                 print(f"  -> 🚨 SIMULATION: SELL {refreshed_token.symbol} | Reason: {sell_reason}")
# #             else:
# #                 print(f"  -> ✅ SIMULATION: HOLD {refreshed_token.symbol}")
                
# #     print(f"✅ Finished 10-minute high-frequency monitoring for {token.symbol}")
#     # return sell_reason, sell_trigger_timestamp


# # ... (keep all the code above this function as is) ...

# # 11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
# # async def collect_data_for_watchlist_coin(token: Token):
# #     """
# #     MODIFIED: Captures every HOLD/SELL decision in a log and returns it.
# #     """
# #     print(f"📊 Starting 45-SECOND TEST monitoring for {token.symbol}...")
    
# #     # --- NEW: A list to store the log of each decision ---
# #     decision_log = []
# #     holder_history = collections.deque(maxlen=4)

# #     # The loop runs 3 times with a 15s sleep, for a total of 45s of monitoring
# #     for i in range(3):
# #         await asyncio.sleep(15)
# #         check_time = (i + 1) * 15
# #         print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
# #         await refresh_token_state(token)
# #         refreshed_token = await Token.objects.aget(pk=token.pk)
        
# #         if refreshed_token.current_holder_count is not None:
# #             holder_history.append(refreshed_token.current_holder_count)

# #         current_reason = None
# #         # --- FIXED: Check that values are not None before comparing ---
# #         if (i == 1 and refreshed_token.current_holder_count is not None and refreshed_token.current_market_cap is not None
# #                 and refreshed_token.current_holder_count < 12 and refreshed_token.current_market_cap < 12000):
# #             current_reason = "Failed 30-Second Viability Gate"
# #         elif refreshed_token.current_market_cap is not None and refreshed_token.current_market_cap < 12000:
# #             current_reason = "Absolute Market Cap Stop-Loss (< $12k)"
# #         elif (refreshed_token.highest_market_cap is not None and refreshed_token.current_market_cap is not None
# #               and refreshed_token.current_market_cap < (refreshed_token.highest_market_cap * 0.55)):
# #             current_reason = f"Trailing MC Stop-Loss (>45% drop from peak of ${refreshed_token.highest_market_cap:,.2f})"
# #         elif (refreshed_token.peak_holder_count is not None and refreshed_token.current_holder_count is not None
# #               and refreshed_token.current_holder_count < (refreshed_token.peak_holder_count * 0.60)):
# #             current_reason = f"Peak Holder Stop-Loss (>40% drop from peak of {refreshed_token.peak_holder_count})"
# #         elif len(holder_history) >= 4:
# #             lowest_in_last_3 = min(list(holder_history)[:3])
# #             if refreshed_token.current_holder_count < (lowest_in_last_3 * 0.75):
# #                 current_reason = f"Rapid Holder Decline (>25% drop from recent low of {lowest_in_last_3})"
        
# #         # --- NEW: Log the decision for this check ---
# #         if current_reason:
# #             print(f"  -> 🚨 SIMULATION: SELL {refreshed_token.symbol} | Reason: {current_reason}")
# #             decision_log.append({
# #                 "timestamp": timezone.now() + timedelta(hours=5, minutes=30),
# #                 "action": "SELL",
# #                 "reason": current_reason
# #             })
# #             # For testing, we can break the loop once a sell is triggered
# #             # break 
# #         else:
# #             print(f"  -> ✅ SIMULATION: HOLD {refreshed_token.symbol}")
# #             decision_log.append({
# #                 "timestamp": timezone.now(),
# #                 "action": "HOLD",
# #                 "reason": f"All checks passed. MC: ${refreshed_token.current_market_cap:,.2f}, Holders: {refreshed_token.current_holder_count}"
# #             })
            
# #     print(f"✅ Finished 45-second test monitoring for {token.symbol}")
# #     # --- MODIFIED: Return the entire log ---
# #     return decision_log

# # ********************************************************************************************************************

# # pumplistener/listener.py

# # ... (previous code in the file remains the same) ...

# # async def collect_data_for_watchlist_coin(token: Token):
# #     """
# #     MODIFIED: Captures every HOLD/SELL decision in a log and returns it.
# #     """
# #     print(f"📊 Starting 45-SECOND TEST monitoring for {token.symbol}...")
    
# #     decision_log = []
# #     holder_history = collections.deque(maxlen=4)

# #     for i in range(3):
# #         await asyncio.sleep(15)
# #         check_time = (i + 1) * 15
# #         print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
# #         await refresh_token_state(token)
# #         refreshed_token = await Token.objects.aget(pk=token.pk)
        
# #         if refreshed_token.current_holder_count is not None:
# #             holder_history.append(refreshed_token.current_holder_count)

# #         current_reason = None
# #         # ... (all of your if/elif sell conditions remain exactly the same) ...
# #         if (i == 1 and refreshed_token.current_holder_count is not None and refreshed_token.current_market_cap is not None
# #                 and refreshed_token.current_holder_count < 12 and refreshed_token.current_market_cap < 12000):
# #             current_reason = "Failed 30-Second Viability Gate"
# #         elif refreshed_token.current_market_cap is not None and refreshed_token.current_market_cap < 12000:
# #             current_reason = "Absolute Market Cap Stop-Loss (< $12k)"
# #         elif (refreshed_token.highest_market_cap is not None and refreshed_token.current_market_cap is not None
# #               and refreshed_token.current_market_cap < (refreshed_token.highest_market_cap * 0.55)):
# #             current_reason = f"Trailing MC Stop-Loss (>45% drop from peak of ${refreshed_token.highest_market_cap:,.2f})"
# #         elif (refreshed_token.peak_holder_count is not None and refreshed_token.current_holder_count is not None
# #               and refreshed_token.current_holder_count < (refreshed_token.peak_holder_count * 0.60)):
# #             current_reason = f"Peak Holder Stop-Loss (>40% drop from peak of {refreshed_token.peak_holder_count})"
# #         elif len(holder_history) >= 4:
# #             lowest_in_last_3 = min(list(holder_history)[:3])
# #             if refreshed_token.current_holder_count < (lowest_in_last_3 * 0.75):
# #                 current_reason = f"Rapid Holder Decline (>25% drop from recent low of {lowest_in_last_3})"
        
# #         if current_reason:
# #             print(f"  -> 🚨 SIMULATION: SELL {refreshed_token.symbol} | Reason: {current_reason}")
# #             decision_log.append({
# #                 "timestamp": timezone.now(),
# #                 "action": "SELL",
# #                 "reason": current_reason
# #             })
# #         else:
# #             print(f"  -> ✅ SIMULATION: HOLD {refreshed_token.symbol}")
            
# #             # #### START OF CHANGE ####
# #             # 💡 Check for None before formatting to prevent the TypeError
            
# #             mc_display = f"${refreshed_token.current_market_cap:,.2f}" if refreshed_token.current_market_cap is not None else "N/A"
# #             holders_display = refreshed_token.current_holder_count if refreshed_token.current_holder_count is not None else "N/A"
            
# #             decision_log.append({
# #                 "timestamp": timezone.now(),
# #                 "action": "HOLD",
# #                 "reason": f"All checks passed. MC: {mc_display}, Holders: {holders_display}"
# #             })
# #             # #### END OF CHANGE ####
            
# #     print(f"✅ Finished 45-second test monitoring for {token.symbol}")
# #     return decision_log

# # ... (the rest of the file remains the same) ...

# async def collect_data_for_watchlist_coin(token: Token):
#     """
#     REBUILT: Creates a combined log of data points and decisions for each time check.
#     """
#     print(f"📊 Starting 45-SECOND TEST monitoring for {token.symbol}...")
    
#     # This will be our new, structured log
#     combined_log = []
#     holder_history = collections.deque(maxlen=4)

#     for i in range(40):
#     # 0000000000000000000000000000000000000000000000000000000000000000000000000
#     # for i in range(3):
#     # 0000000000000000000000000000000000000000000000000000000000000000000000000
#         await asyncio.sleep(15)
#         check_time = (i + 1) * 15
#         print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
        
#         # Capture the data points created during the refresh
#         metadata_point, holders_point = await refresh_token_state(token)
#         refreshed_token = await Token.objects.aget(pk=token.pk)
        
#         if refreshed_token.current_holder_count is not None:
#             holder_history.append(refreshed_token.current_holder_count)

#         current_reason = None
#         # --- Sell condition logic (remains the same) ---
#         if (i == 1 and refreshed_token.current_holder_count is not None and refreshed_token.current_market_cap is not None
#                 and refreshed_token.current_holder_count < 12 and refreshed_token.current_market_cap < 12000):
#             current_reason = f"Failed 30-Second Viability Gate. Holders: {refreshed_token.current_holder_count}, MC: ${refreshed_token.current_market_cap:,.2f}"
#         elif refreshed_token.current_market_cap is not None and refreshed_token.current_market_cap < 12000:
#             current_reason = f"Absolute Market Cap Stop-Loss (< $12k). Holders: {refreshed_token.current_holder_count}, MC: ${refreshed_token.current_market_cap:,.2f}"
#         # ... (other elif conditions remain the same) ...
#         elif (refreshed_token.highest_market_cap is not None and refreshed_token.current_market_cap is not None
#               and refreshed_token.current_market_cap < (refreshed_token.highest_market_cap * 0.55)):
#             current_reason = f"Trailing MC Stop-Loss (>45% drop from peak of ${refreshed_token.highest_market_cap:,.2f}). Holders: {refreshed_token.current_holder_count}"
#         elif (refreshed_token.peak_holder_count is not None and refreshed_token.current_holder_count is not None
#               and refreshed_token.current_holder_count < (refreshed_token.peak_holder_count * 0.60)):
#             current_reason = f"Peak Holder Stop-Loss (>40% drop from peak of {refreshed_token.peak_holder_count}). Holders: {refreshed_token.current_holder_count}"
#         elif len(holder_history) >= 4:
#             lowest_in_last_3 = min(list(holder_history)[:3])
#             if refreshed_token.current_holder_count < (lowest_in_last_3 * 0.75):
#                 current_reason = f"Rapid Holder Decline (>25% drop from recent low of {lowest_in_last_3}). Holders: {refreshed_token.current_holder_count}"

#         # --- Create the decision dictionary ---
#         if current_reason:
#             print(f"  -> 🚨 SIMULATION: SELL {refreshed_token.symbol} | Reason: {current_reason}")
#             decision = {"action": "SELL", "reason": current_reason}
#         else:
#             print(f"  -> ✅ SIMULATION: HOLD {refreshed_token.symbol}")
#             mc_display = f"${refreshed_token.current_market_cap:,.2f}" if refreshed_token.current_market_cap is not None else "N/A"
#             holders_display = refreshed_token.current_holder_count if refreshed_token.current_holder_count is not None else "N/A"
#             reason_text = f"All checks passed. MC: {mc_display}, Holders: {holders_display}"
#             decision = {"action": "HOLD", "reason": reason_text}
        
#         # --- Append the combined data for this check to our new log ---
#         if metadata_point: # Ensure data points were created
#             combined_log.append({
#                 "timestamp": metadata_point.timestamp,
#                 "metadata_point": metadata_point,
#                 "holders_point": holders_point,
#                 "decision": decision
#             })
            
#     print(f"✅ Finished 45-second test monitoring for {token.symbol}")
#     return combined_log
# # 1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

# async def run_trade_cycle(public_key, private_key, mint_address, rpc_url):
#     """A dedicated async function just for the buy/sell logic."""
#     buy_sig = await asyncio.to_thread(trade.buy, public_key, private_key, mint_address, rpc_url)
#     buy_time = timezone.now() + timedelta(hours=5, minutes=30)
#     print(f"\n--- Waiting 1.5 seconds before selling ---\n")
#     await asyncio.sleep(1.5)
#     sell_sig = await asyncio.to_thread(trade.sell, public_key, private_key, mint_address, rpc_url)
#     return buy_sig, sell_sig, buy_time

# # async def monitor_and_report(token_object, buy_signature, sell_signature):
# #     """
# #     MODIFIED: Captures and passes the sell_reason and trigger_timestamp.
# #     """
# #     print(f"✅ Trade complete for {token_object.symbol}. Starting post-trade actions in the background...")
    
# #     # 1. Capture both returned values.
# #     sell_reason, sell_trigger_timestamp = await collect_data_for_watchlist_coin(token_object)
    
# #     # 2. Pass both values to the email function.
# #     await send_trade_notification_email(token_object, buy_signature, sell_signature, sell_reason, sell_trigger_timestamp)

# # 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

# # async def monitor_and_report(token_object, buy_signature, sell_signature):
# #     """
# #     MODIFIED: Captures the decision log and passes it to the email function.
# #     """
# #     print(f"✅ Trade complete for {token_object.symbol}. Starting post-trade actions in the background...")
    
# #     # 1. Capture the decision log.
# #     decision_log = await collect_data_for_watchlist_coin(token_object)
    
# #     # 2. Pass the log to the email function.
# #     await send_trade_notification_email(token_object, buy_signature, sell_signature, decision_log)


# async def monitor_and_report(token_object, buy_signature, sell_signature):
#     print(f"✅ Trade complete for {token_object.symbol}. Starting post-trade actions in the background...")
#     # The variable name is updated to reflect the new structure
#     combined_log = await collect_data_for_watchlist_coin(token_object)
#     await send_trade_notification_email(token_object, buy_signature, sell_signature, combined_log)

# # 11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

# async def execute_trade_strategy(token_websocket_data, public_key, private_key, rpc_url):
#     """Handles the entire lifecycle for a watchlist token."""
#     mint_address = token_websocket_data.get('mint')
#     if not mint_address:
#         return
    
#     trade_task = asyncio.create_task(run_trade_cycle(public_key, private_key, mint_address, rpc_url))
#     print(f"📈 Watchlist hit for {token_websocket_data.get('symbol')}. Firing trade task immediately...")
    
#     token_db_data = {
#         'timestamp': timezone.now() + timedelta(hours=5, minutes=30), # Correct UTC timestamp
#         'name': token_websocket_data.get('name', 'N/A'), 
#         'symbol': token_websocket_data.get('symbol', 'N/A'),
#         'mint_address': mint_address,
#         'sol_amount': token_websocket_data.get('solAmount') or 0,
#         'creator_address': token_websocket_data.get('traderPublicKey', 'N/A'),
#         'pump_fun_link': f"https://pump.fun/{mint_address}",
#         'is_from_watchlist': True
#     }
    
#     # --- Execute Trade and DB Save in Parallel ---
#     db_save_task = asyncio.create_task(save_token_to_db(token_db_data))
#     trade_signatures = await trade_task
#     token_object = await db_save_task
    
#     # This will now work correctly without a ValueError
#     buy_signature, sell_signature, buy_timestamp = trade_signatures

#     if token_object:
#         if buy_signature:
#             token_object.buy_timestamp = buy_timestamp
#             await token_object.asave()

#         # --- Fire and forget the long-running monitoring and reporting task ---
#         # This function now exits immediately, keeping the main listener free.
#         asyncio.create_task(
#             monitor_and_report(token_object, buy_signature, sell_signature)
#         )
#     else:
#         print(f"🚨 Could not start post-trade actions for {mint_address} because token object was not saved.")

# # Replace the old version of this function with this simpler one
# # @sync_to_async
# # def send_trade_notification_email(token, buy_sig, sell_sig, sell_reason, sell_trigger_timestamp):
# #     """
# #     Renders and sends a trade notification email using the default Mailjet backend.
# #     """
# #     recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
# #     if not recipient_email:
# #         print("⚠️ Cannot send trade notification, REPORT_RECIPIENT_EMAIL not set.")
# #         return

# #     print(f"📧 Preparing trade notification email for {token.symbol}...")
# #     try:
# #         subject = f"Watchlist Trade Alert: ${token.symbol}"
# #         html_message = render_to_string('pumplistener/trade_notification_email.html', {
# #             'token': token, 
# #             'buy_sig': buy_sig, 
# #             'sell_sig': sell_sig,
# #             'sell_reason': sell_reason,
# #             'sell_trigger_timestamp': sell_trigger_timestamp,
# #         })
        
# #         send_mail(
# #             subject=subject,
# #             message="This email requires an HTML-compatible client.", # Plain text fallback
# #             from_email=settings.DEFAULT_FROM_EMAIL,
# #             recipient_list=[recipient_email],
# #             html_message=html_message
# #         )
# #         print(f"✅ Trade notification for ${token.symbol} sent to {recipient_email}")
# #     except Exception as e:
# #         print(f"🚨 Failed to send trade notification email: {e}")

# # 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

# # --- MODIFIED: Update this function signature ---
# # @sync_to_async
# # def send_trade_notification_email(token, buy_sig, sell_sig, decision_log):
# #     """
# #     MODIFIED: Accepts a decision_log instead of individual sell reasons.
# #     """
# #     recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
# #     if not recipient_email:
# #         print("⚠️ Cannot send trade notification, REPORT_RECIPIENT_EMAIL not set.")
# #         return

# #     print(f"📧 Preparing trade notification email for {token.symbol}...")
# #     try:
# #         subject = f"Watchlist Trade Alert: ${token.symbol}"
# #         html_message = render_to_string('pumplistener/trade_notification_email.html', {
# #             'token': token, 
# #             'buy_sig': buy_sig, 
# #             'sell_sig': sell_sig,
# #             'decision_log': decision_log, # Pass the new log to the template
# #         })
        
# #         send_mail(
# #             subject=subject,
# #             message="This email requires an HTML-compatible client.",
# #             from_email=settings.DEFAULT_FROM_EMAIL,
# #             recipient_list=[recipient_email],
# #             html_message=html_message
# #         )
# #         print(f"✅ Trade notification for ${token.symbol} sent to {recipient_email}")
# #     except Exception as e:
# #         print(f"🚨 Failed to send trade notification email: {e}")

# @sync_to_async
# def send_trade_notification_email(token, buy_sig, sell_sig, combined_log):
#     # The parameter name is updated here as well
#     recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
#     if not recipient_email:
#         print("⚠️ Cannot send trade notification, REPORT_RECIPIENT_EMAIL not set.")
#         return

#     print(f"📧 Preparing trade notification email for {token.symbol}...")
#     try:
#         subject = f"Watchlist Trade Alert: ${token.symbol}"
#         html_message = render_to_string('pumplistener/trade_notification_email.html', {
#             'token': token, 
#             'buy_sig': buy_sig, 
#             'sell_sig': sell_sig,
#             'combined_log': combined_log, # Pass the new log to the template
#         })
#         send_mail(
#             subject=subject, message="This email requires an HTML-compatible client.",
#             from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[recipient_email],
#             html_message=html_message
#         )
#         print(f"✅ Trade notification for ${token.symbol} sent to {recipient_email}")
#     except Exception as e:
#         print(f"🚨 Failed to send trade notification email: {e}")

# # 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

# #####################################################################################################################

# # --- MAIN LISTENER LOOP ---
# async def pump_fun_listener():
#     print("🎧 Starting Pump.fun WebSocket listener...")
#     async for websocket in websockets.connect(PUMPORTAL_WSS):
#         try:
#             await websocket.send(json.dumps({"method": "subscribeNewToken"}))
#             print("✅ WebSocket Connected and Subscribed.")
#             # --- TEMPORARY TEST FLAG ---
#             # 0000000000000000000000000000000000000000
#             # has_triggered_test = False
#             # 00000000000000000000000000000000000000000
#             while True:
#                 message = await websocket.recv()
#                 data = json.loads(message)
#                 if data and data.get('txType') == 'create':
#                     creator_address = data.get('traderPublicKey', 'N/A')
                    
#                     if creator_address in WATCHLIST_CREATORS:
#                     # 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#                     # if not has_triggered_test:
#                     #     has_triggered_test = True # Set flag so it only runs once
#                     # 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#                         ############################################################################################
#                         # If it's a watchlist token, start the entire non-blocking strategy.
#                         asyncio.create_task(
#                             execute_trade_strategy(data, PUBLIC_KEY, PRIVATE_KEY, RPC_URL)
#                         )
#                         ############################################################################################
#                         # TO Disable trading, we may comment out the above section, and execute only data saving below.
#                             # --- Add this logic to save the token and start data collection ---
#                         # token_data = {
#                         #     'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
#                         #     'name': data.get('name', 'N/A'),
#                         #     'symbol': data.get('symbol', 'N/A'),
#                         #     'mint_address': data.get('mint', 'N/A'),
#                         #     'sol_amount': data.get('solAmount') or 0,
#                         #     'creator_address': creator_address,
#                         #     'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
#                         #     'is_from_watchlist': True # Still mark it as a watchlist token
#                         # }
                        
#                         # token_object = await save_token_to_db(token_data)

#                         # 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#                         # await collect_data_for_watchlist_coin(token_object)
#                         # await send_trade_notification_email(token_object, "N/A", "N/A")
#                         # 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

                        
#                         # if token_object:
#                         #     # Start the 5-minute data collection without trading
#                         #     asyncio.create_task(collect_data_for_watchlist_coin(token_object))
#                         ############################################################################################
#                     else:
#                         # If it's NOT a watchlist token, just save it to the database.
#                         token_data = {
#                             # 'timestamp': timezone.now(),
#                             'timestamp': timezone.now() + timedelta(hours=5, minutes=30),
#                             'name': data.get('name', 'N/A'),
#                             'symbol': data.get('symbol', 'N/A'),
#                             'mint_address': data.get('mint', 'N/A'),
#                             # 'sol_amount': data.get('solAmount', 0),
#                             'sol_amount': data.get('solAmount') or 0, # <-- APPLY FIX HERE
#                             'creator_address': creator_address,
#                             'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}",
#                             'is_from_watchlist': False
#                         }
#                         await save_token_to_db(token_data)
#         except websockets.ConnectionClosed:
#             print("⚠️ WebSocket connection closed. Reconnecting in 5 seconds...")
#             await asyncio.sleep(5)
#         except Exception as e:
#             print(f"💥 Main listener error: {e}. Reconnecting in 5 seconds...")
#             await asyncio.sleep(5)

# def run_listener_in_new_loop():
#     """Wrapper to run the async listener in a new asyncio event loop."""
#     asyncio.run(pump_fun_listener())





























































































































































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
# from . import trade
from . import trade4

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
    if created:
        print(f"✅ Saved to DB: {token.name} ({token.symbol})")

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

# @sync_to_async
# def send_trade_notification_email(token, buy_sig, sell_sig, sell_reason, sell_trigger_timestamp):
#     recipient_email = os.environ.get('REPORT_RECIPIENT_EMAIL')
#     if not recipient_email:
#         print("⚠️ Cannot send trade notification, REPORT_RECIPIENT_EMAIL not set.")
#         return

#     print(f"📧 Preparing trade notification email for {token.symbol}...")
#     subject = f"Watchlist Trade Alert: ${token.symbol}"
#     html_message = render_to_string('pumplistener/trade_notification_email.html', {
#         'token': token, 'buy_sig': buy_sig, 'sell_sig': sell_sig,
#         'sell_reason': sell_reason, 'sell_trigger_timestamp': sell_trigger_timestamp
#     })
    
#     try:
#         send_mail(
#             subject, "A trade was executed for a token on your watchlist.",
#             settings.DEFAULT_FROM_EMAIL, [recipient_email], html_message=html_message
#         )
#         print(f"✅ Trade notification for ${token.symbol} sent to {recipient_email}")
#     except Exception as e:
#         print(f"🚨 Failed to send trade notification email: {e}")

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

# async def refresh_token_state(token: Token):
#     """MODIFIED: Returns the two data point objects it creates."""
#     try:
#         metadata, holders = await asyncio.gather(
#             get_moralis_metadata(token.mint_address),
#             get_moralis_holder_stats(token.mint_address)
#         )
#         # Capture the returned data point objects
#         metadata_point = await save_data_point(token, metadata)
#         holders_point = await save_data_point(token, holders)

#         if 'error' in metadata or 'error' in holders:
#             print(f"  -> Skipping state update for {token.symbol} due to API error.")
#             # Still return the points so they can be logged in the email
#             return metadata_point, holders_point

#         current_mc_str = metadata.get('data', {}).get('fullyDilutedValue')
#         current_holders_str = holders.get('data', {}).get('totalHolders')

#         if current_mc_str and current_holders_str is not None:
#             current_mc = float(current_mc_str)
#             current_holders = int(current_holders_str)

#             @sync_to_async
#             def update_db():
#                 t = Token.objects.select_for_update().get(pk=token.pk)
#                 t.current_market_cap = current_mc
#                 t.current_holder_count = current_holders
#                 if not t.initial_market_cap:
#                     t.initial_market_cap = current_mc
#                 if not t.highest_market_cap or current_mc > t.highest_market_cap:
#                     t.highest_market_cap = current_mc
#                 if not t.peak_holder_count or current_holders > t.peak_holder_count:
#                     t.peak_holder_count = current_holders
#                 t.save()
            
#             await update_db()
#             print(f"  -> Refreshed data for {token.symbol}: MC=${current_mc}, Holders={current_holders}")
        
#         # Return the created database objects
#         return metadata_point, holders_point
#     except Exception as e:
#         print(f"  -> Could not parse API data during refresh for {token.symbol}: {e}")
#         return None, None

# pumplistener/listener.py

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

async def collect_data_for_watchlist_coin(token: Token):
    """
    REBUILT: Creates a combined log of data points and decisions for each time check.
    """
    print(f"📊 Starting 45-SECOND TEST monitoring for {token.symbol}...")
    
    # This will be our new, structured log
    combined_log = []
    holder_history = collections.deque(maxlen=4)

    for i in range(40):
    # 0000000000000000000000000000000000000000000000000000000000000000000000000
    # for i in range(3):
    # 0000000000000000000000000000000000000000000000000000000000000000000000000
        await asyncio.sleep(15)
        check_time = (i + 1) * 15
        print(f"  -> [{token.symbol}] Running T+{check_time}s check...")
        
        # Capture the data points created during the refresh
        metadata_point, holders_point = await refresh_token_state(token)
        refreshed_token = await Token.objects.aget(pk=token.pk)
        
        if refreshed_token.current_holder_count is not None:
            holder_history.append(refreshed_token.current_holder_count)

        current_reason = None
        # --- Sell condition logic (remains the same) ---
        if (i == 1 and refreshed_token.current_holder_count is not None and refreshed_token.current_market_cap is not None
                and refreshed_token.current_holder_count < 12 and refreshed_token.current_market_cap < 12000):
            current_reason = f"Failed 30-Second Viability Gate. Holders: {refreshed_token.current_holder_count}, MC: ${refreshed_token.current_market_cap:,.2f}"
        elif refreshed_token.current_market_cap is not None and refreshed_token.current_market_cap < 12000:
            current_reason = f"Absolute Market Cap Stop-Loss (< $12k). Holders: {refreshed_token.current_holder_count}, MC: ${refreshed_token.current_market_cap:,.2f}"
        # ... (other elif conditions remain the same) ...
        elif (refreshed_token.highest_market_cap is not None and refreshed_token.current_market_cap is not None
              and refreshed_token.current_market_cap < (refreshed_token.highest_market_cap * 0.55)):
            current_reason = f"Trailing MC Stop-Loss (>45% drop from peak of ${refreshed_token.highest_market_cap:,.2f}). Holders: {refreshed_token.current_holder_count}"
        elif (refreshed_token.peak_holder_count is not None and refreshed_token.current_holder_count is not None
              and refreshed_token.current_holder_count < (refreshed_token.peak_holder_count * 0.60)):
            current_reason = f"Peak Holder Stop-Loss (>40% drop from peak of {refreshed_token.peak_holder_count}). Holders: {refreshed_token.current_holder_count}"
        elif len(holder_history) >= 4:
            lowest_in_last_3 = min(list(holder_history)[:3])
            if refreshed_token.current_holder_count < (lowest_in_last_3 * 0.75):
                current_reason = f"Rapid Holder Decline (>25% drop from recent low of {lowest_in_last_3}). Holders: {refreshed_token.current_holder_count}"

        # --- Create the decision dictionary ---
        if current_reason:
            print(f"  -> 🚨 SIMULATION: SELL {refreshed_token.symbol} | Reason: {current_reason}")
            decision = {"action": "SELL", "reason": current_reason}
        else:
            print(f"  -> ✅ SIMULATION: HOLD {refreshed_token.symbol}")
            mc_display = f"${refreshed_token.current_market_cap:,.2f}" if refreshed_token.current_market_cap is not None else "N/A"
            holders_display = refreshed_token.current_holder_count if refreshed_token.current_holder_count is not None else "N/A"
            reason_text = f"All checks passed. MC: {mc_display}, Holders: {holders_display}"
            decision = {"action": "HOLD", "reason": reason_text}
        
        # --- Append the combined data for this check to our new log ---
        if metadata_point: # Ensure data points were created
            combined_log.append({
                "timestamp": metadata_point.timestamp,
                "metadata_point": metadata_point,
                "holders_point": holders_point,
                "decision": decision
            })
            
    print(f"✅ Finished 45-second test monitoring for {token.symbol}")
    return combined_log

async def run_trade_cycle(public_key, private_key, mint_address, rpc_url):
    """A dedicated async function just for the buy/sell logic."""
    # buy_sig = await asyncio.to_thread(trade3.buy, public_key, private_key, mint_address, rpc_url)
    # The new trade.buy is async, so we call it directly with await!
    buy_sig = await trade4.buy(public_key, private_key, mint_address, rpc_url)
    buy_time = timezone.now() + timedelta(hours=5, minutes=30)
    print(f"\n--- Waiting 1.5 seconds before selling ---\n")
    await asyncio.sleep(1.5)
    # sell_sig = await asyncio.to_thread(trade.sell, public_key, private_key, mint_address, rpc_url)
    sell_sig = await asyncio.to_thread(trade4.sell, public_key, private_key, mint_address, rpc_url)
    return buy_sig, sell_sig, buy_time

async def monitor_and_report(token_object, buy_signature, sell_signature):
    print(f"✅ Trade complete for {token_object.symbol}. Starting post-trade actions in the background...")
    # The variable name is updated to reflect the new structure
    combined_log = await collect_data_for_watchlist_coin(token_object)
    await send_trade_notification_email(token_object, buy_signature, sell_signature, combined_log)

async def execute_trade_strategy(token_websocket_data, public_key, private_key, rpc_url):
    """Handles the entire lifecycle for a watchlist token."""
    mint_address = token_websocket_data.get('mint')
    if not mint_address:
        return
    
    trade_task = asyncio.create_task(run_trade_cycle(public_key, private_key, mint_address, rpc_url))
    print(f"📈 Watchlist hit for {token_websocket_data.get('symbol')}. Firing trade task immediately...")

    # --- TRADING DISABLED FOR TEST ---
    # buy_signature, sell_signature, buy_timestamp = await run_trade_cycle(public_key, private_key, mint_address, rpc_url)
    # 2. Await the trade task to complete. This gives you the signatures and timestamp.
    buy_signature, sell_signature, buy_timestamp = await trade_task
    
    
    token_db_data = {
        'timestamp': timezone.now() + timedelta(hours=5, minutes=30), # Correct UTC timestamp
        'name': token_websocket_data.get('name', 'N/A'), 
        'symbol': token_websocket_data.get('symbol', 'N/A'),
        'mint_address': mint_address,
        'sol_amount': token_websocket_data.get('solAmount') or 0,
        'creator_address': token_websocket_data.get('traderPublicKey', 'N/A'),
        'pump_fun_link': f"https://pump.fun/{mint_address}",
        'is_from_watchlist': True,
        'buy_timestamp': buy_timestamp
    }

    # 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000    
    # --- Execute Trade and DB Save in Parallel ---
    db_save_task = asyncio.create_task(save_token_to_db(token_db_data))
    trade_signatures = await trade_task
    token_object = await db_save_task
    
    # This will now work correctly without a ValueError
    buy_signature, sell_signature, buy_timestamp = trade_signatures

    if token_object:
        if buy_signature:
            token_object.buy_timestamp = buy_timestamp
            await token_object.asave()

        # --- Fire and forget the long-running monitoring and reporting task ---
        # This function now exits immediately, keeping the main listener free.
        asyncio.create_task(
            monitor_and_report(token_object, buy_signature, sell_signature)
        )
    else:
        print(f"🚨 Could not start post-trade actions for {mint_address} because token object was not saved.")
        # Update token with the buy timestamp
    # if buy_signature:
    #     token_object.buy_timestamp = buy_timestamp
    #     await token_object.asave()

    # # --- Fire and forget the long-running monitoring and reporting task ---
    # asyncio.create_task(
    #     monitor_and_report(token_object, buy_signature, sell_signature)
    # )
    # ---------------------------------------------------------------------------------------------------------------------

    # token_object = await save_token_to_db(token_db_data)

    # if token_object:
    #     asyncio.create_task(monitor_and_report(token_object, buy_signature, sell_signature))
    # 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

# --- MAIN LISTENER LOOP ---
async def pump_fun_listener():
    print("🎧 Starting Pump.fun WebSocket listener...")
    async for websocket in websockets.connect(PUMPORTAL_WSS):
        try:
            await websocket.send(json.dumps({"method": "subscribeNewToken"}))
            print("✅ WebSocket Connected and Subscribed.")
            # --- TEMPORARY TEST FLAG ---
            # 0000000000000000000000000000000000000000
            # has_triggered_test = False
            # 00000000000000000000000000000000000000000
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                if data and data.get('txType') == 'create':
                    creator_address = data.get('traderPublicKey', 'N/A')
                    
                    if creator_address in WATCHLIST_CREATORS:
                    # 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    # if not has_triggered_test:
                    #     has_triggered_test = True # Set flag so it only runs once
                    # 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                        ############################################################################################
                        # If it's a watchlist token, start the entire non-blocking strategy.
                        asyncio.create_task(
                            execute_trade_strategy(data, PUBLIC_KEY, PRIVATE_KEY, RPC_URL)
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
        except websockets.ConnectionClosed:
            print("⚠️ WebSocket connection closed. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"💥 Main listener error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

def run_listener_in_new_loop():
    """Wrapper to run the async listener in a new asyncio event loop."""
    asyncio.run(pump_fun_listener())