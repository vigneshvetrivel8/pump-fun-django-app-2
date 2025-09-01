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

import asyncio
import websockets
import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from asgiref.sync import sync_to_async # <--- ADD THIS
from .models import Token # <--- ADD THIS
from datetime import datetime, timedelta

# --- CONFIGURATION ---
PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"
LOG_FILE = 'token_log.txt' # <--- CHANGED: Define the log file name

# --- ADD THIS HELPER FUNCTION ---
@sync_to_async
def save_token_to_db(token_data):
    """Safely saves a token to the database from an async context."""
    # Check if a token with this mint address already exists
    if not Token.objects.filter(mint_address=token_data['mint_address']).exists():
        token = Token.objects.create(**token_data)
        print(f"✅ Saved to DB: {token.name} ({token.symbol})")
    else:
        print(f"⚪️ Duplicate, not saved: {token_data['name']}")

async def pump_fun_listener():
    print("🚀 Starting Pump.fun listener (in-thread)...")
    try:
        async with websockets.connect(PUMPORTAL_WSS) as websocket:
            print("✅ WebSocket Connected (in-thread).")
            subscribe_message = {"method": "subscribeNewToken"}
            await websocket.send(json.dumps(subscribe_message))
            print("✅ Subscribed to new tokens (in-thread).")
            while True:
                try:
                    ########################################################################################################
#                     message = await websocket.recv()
#                     data = json.loads(message)
#                     if data and data.get('txType') == 'create':
#                         # --- THIS IS THE NEW LOGIC TO WRITE TO THE .TXT FILE ---

#                         # 1. Get the current time
#                         timestamp_ist = datetime.now(ZoneInfo("Asia/Kolkata"))

#                         # 2. Create a formatted, multi-line string with all the details
#                         log_entry = f"""
# =============================================
# 🔥 New Token Detected at {timestamp_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}
#    -> Name: {data.get('name', 'N/A')} (${data.get('symbol', 'N/A')})
#    -> Mint Address: {data.get('mint', 'N/A')}
#    -> Creator Invested: {data.get('solAmount', 0):.2f} SOL
#    -> Creator: {data.get('traderPublicKey', 'N/A')}
#    -> Link: https://pump.fun/{data.get('mint', '')}
# =============================================
# """
#                         # 3. Append this string to the log file
#                         with open(LOG_FILE, 'a', encoding='utf-8') as f:
#                             f.write(log_entry)

#                         # 4. (Optional) Print a confirmation to the console
#                         print(f"✅ Logged new token to {LOG_FILE}: {data.get('name', 'N/A')}")
#                         # --- END OF NEW LOGIC ---
                    # *************************************************************************************************************

                    message = await websocket.recv()
                    data = json.loads(message)
                    if data and data.get('txType') == 'create':
                        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
                        # --- THIS IS THE NEW LOGIC TO SAVE TO THE DATABASE ---
                        token_data = {
                            # 'timestamp': datetime.now(ZoneInfo("Asia/Kolkata")),
                            # 'timestamp': datetime.now(),
                            'timestamp': ist_time,
                            'name': data.get('name', 'N/A'),
                            'symbol': data.get('symbol', 'N/A'),
                            'mint_address': data.get('mint', 'N/A'),
                            'sol_amount': data.get('solAmount', 0),
                            'creator_address': data.get('traderPublicKey', 'N/A'),
                            'pump_fun_link': f"https://pump.fun/{data.get('mint', 'N/A')}"
                        }
                        await save_token_to_db(token_data)
                        # --- END OF NEW LOGIC ---

                        ####################################################################################################################

                except websockets.ConnectionClosed:
                    print("⚠️ WebSocket connection closed. Reconnecting...")
                    break
    except Exception as e:
        print(f"💥 Listener thread error: {e}")

# The run_listener_in_new_loop() function remains the same
def run_listener_in_new_loop():
    while True:
        try:
            asyncio.run(pump_fun_listener())
        except Exception as e:
            print(f"💥 Main listener loop crashed: {e}")
        print("Reconnecting in 10 seconds...")
        time.sleep(10)