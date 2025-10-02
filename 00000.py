import os
import requests
import asyncio
import aiohttp
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.system_program import TransferParams, transfer
from solders.pubkey import Pubkey
from solders.message import Message
import base58
import time # Used for performance timing

import random
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY')

# --- Configuration (Unchanged) ---
# PRIVATE_KEY = "66iEHNPJgy1wnefNHNFpUmvaLuwhgdseTqVhgkMmY6YeTSjc2cf2sQ7V3yMD6eqp64pjcFVSBrcHsJRAXYfkiF9Z"
HELIUS_API_URL = "https://mainnet.helius-rpc.com/?api-key=5d0a2bb2-0bd2-4f5a-b581-d1785d59e26b"

keypair = Keypair.from_base58_string(PRIVATE_KEY)
PUBLIC_KEY = str(keypair.pubkey())

MINT_ADDRESS = "GutMnkY4y6kzWJu1P3PfCnxyEkt9veeaLj63DGM5Rh6g"

jito_endpoints_str = os.getenv('JITO_ENDPOINTS', '')
JITO_ENDPOINTS = [endpoint.strip() for endpoint in jito_endpoints_str.split(',') if endpoint.strip()]

jito_tips_str = os.getenv('JITO_TIP_ACCOUNTS', '')
JITO_TIP_ACCOUNTS = [acc.strip() for acc in jito_tips_str.split(',') if acc.strip()]

JITO_ENDPOINTS = [
    "https://mainnet.block-engine.jito.wtf",
    "https://amsterdam.mainnet.block-engine.jito.wtf",
    "https://frankfurt.mainnet.block-engine.jito.wtf",
    "https://ny.mainnet.block-engine.jito.wtf",
    "https://tokyo.mainnet.block-engine.jito.wtf",
    "https://dublin.mainnet.block-engine.jito.wtf",
    "https://london.mainnet.block-engine.jito.wtf",
    "https://slc.mainnet.block-engine.jito.wtf",
    "https://singapore.mainnet.block-engine.jito.wtf"
]
JITO_TIP_ACCOUNTS = [
    "96gYZGLnJYVFmbjzopPSU6QiEV5fGq5TALxWbiaGKUaE", "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
    "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY", "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
    "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh", "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
    "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL", "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"
]

if not JITO_ENDPOINTS or not JITO_TIP_ACCOUNTS:
    print("⚠️ JITO_ENDPOINTS or JITO_TIP_ACCOUNTS are not set in the .env file.")

# --- Asynchronous Jito Bundle Sending (Unchanged) ---

async def send_bundle_to_endpoint(session, endpoint, payload):
    """Sends a single bundle to a single Jito endpoint."""
    try:
        async with session.post(f"{endpoint}/api/v1/bundles", json=payload, timeout=5) as response:
            result = await response.json()
            if response.status == 200 and 'result' in result:
                # Minimalist success print to avoid clutter
                # print(f"  ✅ Success from {endpoint.split('.')[0].replace('https://', '')}")
                return result['result']
            else:
                return None
    except Exception:
        return None

# async def send_jito_bundle_parallel(trade_tx, tip_lamports=100000):
#     """
#     Creates a bundle and sends it to ALL Jito endpoints simultaneously.
#     """
#     print(f"\n3. Creating Jito bundle with {tip_lamports} lamports tip...")
    
#     # --- TIMING: Bundle Creation ---
#     start_bundle_creation_time = time.perf_counter()

#     trade_blockhash = trade_tx.message.recent_blockhash
#     tip_account = random.choice(JITO_TIP_ACCOUNTS)
    
#     tip_instruction = transfer(TransferParams(from_pubkey=keypair.pubkey(), to_pubkey=Pubkey.from_string(tip_account), lamports=tip_lamports))
#     tip_message = Message.new_with_blockhash(instructions=[tip_instruction], payer=keypair.pubkey(), blockhash=trade_blockhash)
#     tip_tx = VersionedTransaction(tip_message, [keypair])

#     trade_tx_b58 = base58.b58encode(bytes(trade_tx)).decode('utf-8')
#     tip_tx_b58 = base58.b58encode(bytes(tip_tx)).decode('utf-8')

#     bundle_payload = {
#         "jsonrpc": "2.0", "id": 1,
#         "method": "sendBundle",
#         "params": [[trade_tx_b58, tip_tx_b58]]
#     }
    
#     end_bundle_creation_time = time.perf_counter()
#     print(f"  ⏱️ Bundle created in {end_bundle_creation_time - start_bundle_creation_time:.4f} seconds")

#     print("  Sending bundle to all Jito endpoints in parallel...")
    
#     # --- TIMING: Parallel HTTP Requests ---
#     start_parallel_send_time = time.perf_counter()
#     async with aiohttp.ClientSession() as session:
#         tasks = [send_bundle_to_endpoint(session, endpoint, bundle_payload) for endpoint in JITO_ENDPOINTS]
#         results = await asyncio.gather(*tasks)
#     end_parallel_send_time = time.perf_counter()
    
#     print(f"  ⏱️ All parallel requests completed in {end_parallel_send_time - start_parallel_send_time:.4f} seconds")

#     successful_bundle_id = next((res for res in results if res is not None), None)

#     if successful_bundle_id:
#         print(f"\n✅ Bundle sent successfully!")
#         print(f"  First successful Bundle ID: {successful_bundle_id}")
#         return successful_bundle_id
#     else:
#         print("\n❌ Bundle failed on all Jito endpoints.")
#         return None

async def send_jito_bundle_parallel(trade_tx, tip_lamports=100000):
    """
    Creates a bundle and sends it to ALL Jito endpoints simultaneously,
    but acts on the FIRST successful response.
    """
    print(f"\n3. Creating Jito bundle with {tip_lamports} lamports tip...")
    
    start_bundle_creation_time = time.perf_counter()
    trade_blockhash = trade_tx.message.recent_blockhash
    tip_account = random.choice(JITO_TIP_ACCOUNTS)
    tip_instruction = transfer(TransferParams(from_pubkey=keypair.pubkey(), to_pubkey=Pubkey.from_string(tip_account), lamports=tip_lamports))
    tip_message = Message.new_with_blockhash(instructions=[tip_instruction], payer=keypair.pubkey(), blockhash=trade_blockhash)
    tip_tx = VersionedTransaction(tip_message, [keypair])
    trade_tx_b58 = base58.b58encode(bytes(trade_tx)).decode('utf-8')
    tip_tx_b58 = base58.b58encode(bytes(tip_tx)).decode('utf-8')
    bundle_payload = {
        "jsonrpc": "2.0", "id": 1,
        "method": "sendBundle",
        "params": [[trade_tx_b58, tip_tx_b58]]
    }
    end_bundle_creation_time = time.perf_counter()
    print(f"  ⏱️ Bundle created in {end_bundle_creation_time - start_bundle_creation_time:.4f} seconds")

    print("  Sending bundle to all Jito endpoints in parallel...")
    
    start_parallel_send_time = time.perf_counter()
    successful_bundle_id = None
    
    async with aiohttp.ClientSession() as session:
        # Create a set of tasks to run in parallel
        tasks = {asyncio.create_task(send_bundle_to_endpoint(session, endpoint, bundle_payload)) for endpoint in JITO_ENDPOINTS}
        
        # Use asyncio.as_completed to process tasks as they finish
        for future in asyncio.as_completed(tasks):
            result = await future
            # If we get a successful result, store it and break the loop
            if result:
                successful_bundle_id = result
                # Now that we have what we need, cancel all other pending tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                break

    end_parallel_send_time = time.perf_counter()
    
    if successful_bundle_id:
        print(f"  ⏱️ First successful response received in {end_parallel_send_time - start_parallel_send_time:.4f} seconds")
        print(f"\n✅ Bundle sent successfully!")
        print(f"  First successful Bundle ID: {successful_bundle_id}")
        return successful_bundle_id
    else:
        print(f"  ⏱️ All parallel requests completed in {end_parallel_send_time - start_parallel_send_time:.4f} seconds")
        print("\n❌ Bundle failed on all Jito endpoints.")
        return None

# --- Standard RPC Fallback (Unchanged) ---
def send_with_standard_rpc(trade_tx):
    print("\n3. Sending transaction via Standard RPC...")
    try:
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "sendTransaction",
            "params": [
                base58.b58encode(bytes(trade_tx)).decode('utf-8'),
                {"skipPreflight": True, "preflightCommitment": "processed", "maxRetries": 2}
            ]
        }
        response = requests.post(HELIUS_API_URL, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        result = response.json()
        
        if 'result' in result:
            signature = result['result']
            print(f"✅ Transaction sent! Signature: {signature}")
            return signature
        else:
            print(f"❌ RPC send failed: {result.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Error sending via RPC: {e}")
        return None

# --- MODIFIED: Main execution function with timing ---

async def execute_trade(use_jito=True, jito_tip_lamports=100000):
    """Execute Pump.fun trade, now async and with performance timing."""
    # --- TIMING: Start total timer ---
    start_total_time = time.perf_counter()

    print("="*80)
    print("PUMP.FUN PARALLEL JITO BUNDLE TRADER")
    print(f"Wallet: {PUBLIC_KEY}, Token: {MINT_ADDRESS}")
    print("="*80)
    
    # 1. Get transaction from PumpPortal
    print("\n1. Requesting transaction from PumpPortal...")
    # --- TIMING: Fetch transaction ---
    start_fetch_time = time.perf_counter()
    try:
        response = requests.post(
            url="https://pumpportal.fun/api/trade-local",
            json={
                "publicKey": PUBLIC_KEY, "action": "buy", "mint": MINT_ADDRESS,
                "amount": 0.004, "denominatedInSol": "true", "slippage": 10,
                "priorityFee": 0.001, "pool": "pump"
            },
            timeout=10
        )
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return
        end_fetch_time = time.perf_counter()
        print(f"  ⏱️ Transaction received in {end_fetch_time - start_fetch_time:.4f} seconds")
    except Exception as e:
        print(f"❌ Error getting tx from PumpPortal: {e}")
        return

    # 2. Sign transaction
    print("\n2. Signing transaction...")
    # --- TIMING: Sign transaction ---
    start_sign_time = time.perf_counter()
    unsigned_tx = VersionedTransaction.from_bytes(response.content)
    trade_tx = VersionedTransaction(unsigned_tx.message, [keypair])
    end_sign_time = time.perf_counter()
    print(f"  ⏱️ Transaction signed in {end_sign_time - start_sign_time:.4f} seconds")

    # 3. Send transaction
    # --- TIMING: Send transaction (bundle or RPC) ---
    start_send_time = time.perf_counter()
    result = None
    if use_jito:
        result = await send_jito_bundle_parallel(trade_tx, jito_tip_lamports)
    else:
        result = await asyncio.to_thread(send_with_standard_rpc, trade_tx)
    end_send_time = time.perf_counter()
    print(f"  ⏱️ Sending process completed in {end_send_time - start_send_time:.4f} seconds")
    
    # --- TIMING: Calculate and print total time ---
    end_total_time = time.perf_counter()
    print(f"\n✨ Total execution time: {end_total_time - start_total_time:.4f} seconds")
    
    return result

# --- Entry point (Unchanged) ---
if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Make sure to set your PRIVATE_KEY!\n")
    
    result = asyncio.run(execute_trade(use_jito=True, jito_tip_lamports=100000))
    
    if not result:
        print("\n🔄 Jito bundle failed. A standard RPC fallback could be implemented here if desired.")

    print("\n" + "="*80)
    print("TROUBLESHOOTING:")
    print("  • If all endpoints fail, check the blockhash is recent.")
    print("  • Ensure your server has low latency to the Jito endpoints.")
    print("="*80)

###################################################################################################################

# import os
# import requests
# import time
# from solders.keypair import Keypair
# from solders.transaction import VersionedTransaction
# from solders.rpc.requests import SendVersionedTransaction
# from solders.rpc.config import RpcSendTransactionConfig
# from dotenv import load_dotenv

# # Load environment variables from your .env file
# load_dotenv()

# # --- CONFIGURATION ---
# PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
# RPC_URL = os.getenv("RPC_URL") # Ensure this is your Helius (or other) RPC URL
# MINT_ADDRESS = "GutMnkY4y6kzWJu1P3PfCnxyEkt9veeaLj63DGM5Rh6g" # Example token

# def buy_standard_with_timing(private_key, mint_address, rpc_url):
#     """
#     Executes a standard buy transaction via RPC and measures the time of each step.
#     """
#     if not private_key or not rpc_url:
#         print("❌ Error: WALLET_PRIVATE_KEY or RPC_URL not found in environment variables.")
#         return

#     keypair = Keypair.from_base58_string(private_key)
#     public_key = str(keypair.pubkey())

#     # --- TIMING: Start total timer ---
#     start_total_time = time.perf_counter()
    
#     print("="*80)
#     print("STANDARD PUMP.FUN RPC BUY TESTER")
#     print(f"Wallet: {public_key}, Token: {mint_address}")
#     print("="*80)

#     try:
#         # 1. Get transaction from PumpPortal
#         print("\n1. Requesting transaction from PumpPortal...")
#         start_fetch_time = time.perf_counter()
#         response = requests.post(url="https://pumpportal.fun/api/trade-local", data={
#             "publicKey": public_key, "action": "buy", "mint": mint_address,
#             "amount": 0.01, "denominatedInSol": "true", "slippage": 15,
#             "priorityFee": 0.0001, "pool": "auto"
#         })
#         response.raise_for_status()
#         end_fetch_time = time.perf_counter()
#         print(f"  ⏱️ Transaction received in {end_fetch_time - start_fetch_time:.4f} seconds")

#         # 2. Sign transaction
#         print("\n2. Signing transaction...")
#         start_sign_time = time.perf_counter()
#         tx = VersionedTransaction(VersionedTransaction.from_bytes(response.content).message, [keypair])
#         end_sign_time = time.perf_counter()
#         print(f"  ⏱️ Transaction signed in {end_sign_time - start_sign_time:.4f} seconds")

#         # 3. Send transaction to standard RPC
#         print("\n3. Sending transaction via Standard RPC...")
#         config = RpcSendTransactionConfig(skip_preflight=True)
#         start_rpc_time = time.perf_counter()
#         rpc_response = requests.post(
#             url=rpc_url,
#             headers={"Content-Type": "application/json"},
#             data=SendVersionedTransaction(tx, config).to_json()
#         )
#         rpc_response.raise_for_status()
#         end_rpc_time = time.perf_counter()
#         print(f"  ⏱️ RPC response received in {end_rpc_time - start_rpc_time:.4f} seconds")
        
#         data = rpc_response.json()
#         if 'result' in data:
#             txSignature = data['result']
#             print(f'\n✅ BUY successful! Signature: {txSignature}')
#             return txSignature
#         else:
#             print(f"\n❌ BUY failed. Response: {data}")
#             return None

#     except Exception as e:
#         print(f"❌ An unexpected error occurred: {e}")
#         return None
#     finally:
#         # --- TIMING: Calculate and print total time ---
#         end_total_time = time.perf_counter()
#         print(f"\n✨ Total execution time: {end_total_time - start_total_time:.4f} seconds")
#         print("="*80)


# if __name__ == "__main__":
#     buy_standard_with_timing(PRIVATE_KEY, MINT_ADDRESS, RPC_URL)