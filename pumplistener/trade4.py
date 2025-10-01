import os
import requests # Still used for the initial synchronous call to PumpPortal
import asyncio
import aiohttp
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.system_program import TransferParams, transfer
from solders.pubkey import Pubkey
from solders.message import Message
import base58
import time
import random
from dotenv import load_dotenv
load_dotenv()
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig

# --- Configuration ---
PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY')
HELIUS_API_URL = os.getenv('RPC_URL')
keypair = Keypair.from_base58_string(PRIVATE_KEY)

jito_endpoints_str = os.getenv('JITO_ENDPOINTS', '')
JITO_ENDPOINTS = [endpoint.strip() for endpoint in jito_endpoints_str.split(',') if endpoint.strip()]

jito_tips_str = os.getenv('JITO_TIP_ACCOUNTS', '')
JITO_TIP_ACCOUNTS = [acc.strip() for acc in jito_tips_str.split(',') if acc.strip()]

if not JITO_ENDPOINTS or not JITO_TIP_ACCOUNTS:
    print("⚠️ JITO_ENDPOINTS or JITO_TIP_ACCOUNTS are not set in the .env file.")

# --- Configuration (Unchanged) ---
# PRIVATE_KEY = "66iEHNPJgy1wnefNHNFpUmvaLuwhgdseTqVhgkMmY6YeTSjc2cf2sQ7V3yMD6eqp64pjcFVSBrcHsJRAXYfkiF9Z"
# HELIUS_API_URL = "https://mainnet.helius-rpc.com/?api-key=5d0a2bb2-0bd2-4f5a-b581-d1785d59e26b"

# keypair = Keypair.from_base58_string(PRIVATE_KEY)
# PUBLIC_KEY = str(keypair.pubkey())

# MINT_ADDRESS = "GutMnkY4y6kzWJu1P3PfCnxyEkt9veeaLj63DGM5Rh6g"

# JITO_ENDPOINTS = [
#     "https://mainnet.block-engine.jito.wtf",
#     "https://amsterdam.mainnet.block-engine.jito.wtf",
#     "https://frankfurt.mainnet.block-engine.jito.wtf",
#     "https://ny.mainnet.block-engine.jito.wtf",
#     "https://tokyo.mainnet.block-engine.jito.wtf",
#     "https://dublin.mainnet.block-engine.jito.wtf",
#     "https://london.mainnet.block-engine.jito.wtf",
#     "https://slc.mainnet.block-engine.jito.wtf",
#     "https://singapore.mainnet.block-engine.jito.wtf"
# ]
# JITO_TIP_ACCOUNTS = [
#     "96gYZGLnJYVFmbjzopPSU6QiEV5fGq5TALxWbiaGKUaE", "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
#     "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY", "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
#     "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh", "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
#     "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL", "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"
# ]

# --- NEW: Asynchronous Jito Bundle Sending ---

async def send_bundle_to_endpoint(session, endpoint, payload):
    """Sends a single bundle to a single Jito endpoint."""
    try:
        async with session.post(f"{endpoint}/api/v1/bundles", json=payload, timeout=5) as response:
            result = await response.json()
            if response.status == 200 and 'result' in result:
                print(f"  ✅ Success from {endpoint.split('.')[0].replace('https://', '')}: Bundle ID {result['result']}")
                return result['result'] # Return the bundle ID on success
            else:
                return None
    except Exception:
        # Errors (like timeouts) are expected, so we don't need to log them here
        return None


async def send_jito_bundle_parallel(trade_tx, tip_lamports=100000):
    """
    Creates a bundle and sends it to ALL Jito endpoints simultaneously.
    """
    print(f"\n3. Creating Jito bundle with {tip_lamports} lamports tip...")
    
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

    print("  Sending bundle to all Jito endpoints in parallel...")
    async with aiohttp.ClientSession() as session:
        tasks = [send_bundle_to_endpoint(session, endpoint, bundle_payload) for endpoint in JITO_ENDPOINTS]
        results = await asyncio.gather(*tasks)

    # Find the first successful result (a bundle ID string)
    successful_bundle_id = next((res for res in results if res is not None), None)

    if successful_bundle_id:
        print(f"\n✅ Bundle sent successfully!")
        print(f"  First successful Bundle ID: {successful_bundle_id}")
        # You can add a status check loop here if needed
        return successful_bundle_id
    else:
        print("\n❌ Bundle failed on all Jito endpoints.")
        return None

def send_with_standard_rpc(trade_tx):
    """Fallback: Send via standard RPC (no Jito). This remains synchronous."""
    print("\n3. Sending transaction via Standard RPC...")
    try:
        # Using the synchronous requests library for simplicity here
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
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

# --- MODIFIED: Main execution function is now async ---

async def buy(PUBLIC_KEY, PRIVATE_KEY, MINT_ADDRESS, RPC_URL):
# async def execute_trade(use_jito=True, jito_tip_lamports=100000):
    """Execute Pump.fun trade, now async."""
    use_jito=True, 
    jito_tip_lamports=100000
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    print("="*80)
    print("PUMP.FUN PARALLEL JITO BUNDLE TRADER")
    print(f"Wallet: {PUBLIC_KEY}, Token: {MINT_ADDRESS}")
    print("="*80)
    
    # 1. Get transaction from PumpPortal (this part remains synchronous)
    print("\n1. Requesting transaction from PumpPortal...")
    try:
        response = requests.post(
            url="https://pumpportal.fun/api/trade-local",
            json={
                "publicKey": PUBLIC_KEY, "action": "buy", "mint": MINT_ADDRESS,
                "amount": 0.01, "denominatedInSol": "true", "slippage": 50,
                "priorityFee": 0.0001, "pool": "pump"
            },
            timeout=10
        )
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return
        print("  ✓ Transaction received")
    except Exception as e:
        print(f"❌ Error getting tx from PumpPortal: {e}")
        return

    # 2. Sign transaction (synchronous)
    print("\n2. Signing transaction...")
    unsigned_tx = VersionedTransaction.from_bytes(response.content)
    trade_tx = VersionedTransaction(unsigned_tx.message, [keypair])
    print("  ✓ Transaction signed")

    # 3. Send transaction (calls the appropriate async or sync function)
    if use_jito:
        result = await send_jito_bundle_parallel(trade_tx, jito_tip_lamports)
    # else:
        # Run the synchronous RPC call in a separate thread to not block asyncio
        # result = await asyncio.to_thread(send_with_standard_rpc, trade_tx)
    
    return result

# # --- MODIFIED: Entry point now uses asyncio.run() ---
# if __name__ == "__main__":
#     print("\n⚠️  IMPORTANT: Make sure to set your PRIVATE_KEY!\n")
    
#     # Use asyncio.run() to start the top-level async function
#     result = asyncio.run(execute_trade(use_jito=True, jito_tip_lamports=100000))
    
#     if not result:
#         print("\n🔄 Jito bundle failed. A standard RPC fallback could be implemented here if desired.")

#     print("\n" + "="*80)
#     print("TROUBLESHOOTING:")
#     print("  • If all endpoints fail, check the blockhash is recent.")
#     print("  • Ensure your server has low latency to the Jito endpoints.")
#     print("="*80)


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