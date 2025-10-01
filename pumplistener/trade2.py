# pumplistener/trade.py

import os
import requests # Used for the initial synchronous call to PumpPortal
import asyncio
import aiohttp
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.pubkey import Pubkey
from solders.message import Message
from solders.system_program import TransferParams, transfer
import base58
import random
from dotenv import load_dotenv
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig


# Load environment variables from your .env file
load_dotenv()

# --- Configuration (Loaded from .env) ---
# It's better to manage these lists in your .env file
jito_endpoints_str = os.getenv('JITO_ENDPOINTS', '')
JITO_ENDPOINTS = [endpoint.strip() for endpoint in jito_endpoints_str.split(',') if endpoint.strip()]

jito_tips_str = os.getenv('JITO_TIP_ACCOUNTS', '')
JITO_TIP_ACCOUNTS = [acc.strip() for acc in jito_tips_str.split(',') if acc.strip()]

if not JITO_ENDPOINTS or not JITO_TIP_ACCOUNTS:
    print("⚠️ JITO_ENDPOINTS or JITO_TIP_ACCOUNTS are not set in the .env file.")

# --- Core Asynchronous Jito Functions ---

async def send_bundle_to_endpoint(session, endpoint, payload):
    """Sends a single bundle to a single Jito endpoint asynchronously."""
    try:
        async with session.post(f"{endpoint}/api/v1/bundles", json=payload, timeout=5) as response:
            result = await response.json()
            if response.status == 200 and 'result' in result:
                # Shorten the endpoint URL for cleaner logging
                endpoint_name = endpoint.split('.')[0].replace('https://', '')
                print(f"  ✅ Success from {endpoint_name}: Bundle ID {result['result']}")
                return result['result']
            else:
                return None
    except Exception:
        # Or other connection errors
        return None

async def send_jito_bundle_parallel(trade_tx, private_key, tip_lamports=100000):
    """Creates a bundle and sends it to ALL Jito endpoints simultaneously."""
    print(f"  -> Creating Jito bundle with {tip_lamports} lamports tip...")
    keypair = Keypair.from_base58_string(private_key)
    
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

    print("  -> Sending bundle to all Jito endpoints in parallel...")
    async with aiohttp.ClientSession() as session:
        tasks = [send_bundle_to_endpoint(session, endpoint, bundle_payload) for endpoint in JITO_ENDPOINTS]
        results = await asyncio.gather(*tasks)

    successful_bundle_id = next((res for res in results if res is not None), None)

    if successful_bundle_id:
        print(f"\n✅ Bundle sent successfully! First successful ID: {successful_bundle_id}")
        return successful_bundle_id
    else:
        print("\n❌ Bundle failed on all Jito endpoints.")
        return None

# --- Main Buy/Sell Functions ---

async def buy(public_key, private_key, mint_address, rpc_url):
    """
    Executes a buy transaction using a parallel Jito bundle.
    This function is now ASYNCHRONOUS.
    """
    print("🔹 Executing PARALLEL JITO BUY...")
    try:
        # 1. Get transaction from PumpPortal (this remains synchronous)
        print("  -> Requesting transaction from PumpPortal...")
        response = requests.post(
            url="https://pumpportal.fun/api/trade-local",
            json={
                "publicKey": public_key, "action": "buy", "mint": mint_address,
                "amount": 0.01, "denominatedInSol": "true", "slippage": 25, # Higher slippage for sniping
                "priorityFee": 0.0001, "pool": "pump"
            },
            timeout=10
        )
        if response.status_code != 200:
            print(f"  ❌ Error getting tx from PumpPortal: {response.status_code} - {response.text}")
            return None
        print("  -> ✓ Transaction received from PumpPortal")

        # 2. Sign the transaction
        keypair = Keypair.from_base58_string(private_key)
        unsigned_tx = VersionedTransaction.from_bytes(response.content)
        trade_tx = VersionedTransaction(unsigned_tx.message, [keypair])
        print("  -> ✓ Transaction signed")

        # 3. Send via the parallel Jito function
        jito_tip = int(os.getenv('JITO_TIP_LAMPORTS', 100000))
        bundle_id = await send_jito_bundle_parallel(trade_tx, private_key, tip_lamports=jito_tip)
        
        # The listener expects a signature, the bundle ID is the best equivalent
        return bundle_id

    except Exception as e:
        print(f"❌ An unexpected error occurred in buy(): {e}")
        return None

# def sell(public_key, private_key, mint_address, rpc_url):
#     """
#     TRADING IS DISABLED FOR TESTING. This function will not execute a sell.
#     You should implement a parallel Jito sell function similar to the buy function for production.
#     """
#     print("🔹 NOTICE: SELL operation skipped because trading is temporarily disabled.")
#     # Return a dummy signature for testing the email flow
#     return "DUMMY_SELL_SIGNATURE_FOR_TEST"

def sell(public_key, private_key, mint_address, rpc_url):
    """
    Executes a sell transaction for 100% of the token.
    Accepts configuration as arguments.
    """
    print("🔹 Executing SELL (100%)...")
    # try:
    response = requests.post(url="https://pumpportal.fun/api/trade-local", data={
        "publicKey": public_key,
        "action": "sell",
        "mint": mint_address,
        "amount": "100%",
        "denominatedInSol": "false",
        "slippage": 99,
        # "priorityFee": 0.00001,
        "priorityFee": 0.00005,
        # "priorityFee": 0.00025,
        "pool": "auto"
    })
    # response.raise_for_status()

    keypair = Keypair.from_base58_string(private_key)
    tx = VersionedTransaction(VersionedTransaction.from_bytes(response.content).message, [keypair])

    commitment = CommitmentLevel.Confirmed
    config = RpcSendTransactionConfig(preflight_commitment=commitment)
    # Remove the old commitment and config lines and replace them with this:
    # config = RpcSendTransactionConfig(skip_preflight=True)
    txPayload = SendVersionedTransaction(tx, config)

    response = requests.post(
        # url="Your RPC Endpoint here - Eg: https://api.mainnet-beta.solana.com/",
        # url="http://fra-sender.helius-rpc.com/fast",
        # url="https://mainnet.helius-rpc.com/?api-key=5d0a2bb2-0bd2-4f5a-b581-d1785d59e26b",
        url=rpc_url,
        headers={"Content-Type": "application/json"},
        data=SendVersionedTransaction(tx, config).to_json()
    )
    print("#" * 150)
    print(response.json())
    print("#" * 150)
    if 'result' in response.json():
        txSignature = response.json()['result']
        print(f'✅ SELL successful! Transaction: https://solscan.io/tx/{txSignature}')
        return txSignature # <-- RETURN THE SIGNATURE
    else:
        print(f"❌ SELL failed. Response: {response.json()}")
        return None # <-- RETURN NONE ON FAILURE
    # txSignature = response.json()['result']
    # print(f'Transaction: https://solscan.io/tx/{txSignature}')

    # except Exception as e:
    #     print(f"❌ An unexpected error occurred in sell(): {e}")