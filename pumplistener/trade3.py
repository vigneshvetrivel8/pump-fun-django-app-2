import os
import requests
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.system_program import TransferParams, transfer
from solders.pubkey import Pubkey
from solders.message import Message
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
import base58
import time
import random
from dotenv import load_dotenv
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig

load_dotenv()

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


# Official Jito tip accounts (these are the correct ones)
# JITO_TIP_ACCOUNTS = [
#     "96gYZGLnJYVFmbjzopPSU6QiEV5fGq5TALxWbiaGKUaE",
#     "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
#     "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY",
#     "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
#     "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh",
#     "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
#     "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
#     "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"
# ]

JITO_BLOCK_ENGINE_URL = JITO_ENDPOINTS[0]


def send_jito_bundle_simple(trade_tx, tip_lamports=100000):
    """
    Simplified approach: Add tip instruction directly to the trade transaction
    This ensures proper write-locking
    """
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    print(f"\n3. Creating Jito bundle with {tip_lamports} lamports tip...")
    
    try:
        # Get the blockhash from trade transaction
        trade_blockhash = trade_tx.message.recent_blockhash
        print(f"   Using blockhash: {trade_blockhash}")
        
        # Pick random tip account for better parallelization
        tip_account = random.choice(JITO_TIP_ACCOUNTS)
        print(f"   Tip account: {tip_account}")
        
        # Create tip transaction with SAME blockhash
        tip_instruction = transfer(
            TransferParams(
                from_pubkey=keypair.pubkey(),
                to_pubkey=Pubkey.from_string(tip_account),
                lamports=tip_lamports
            )
        )
        
        tip_message = Message.new_with_blockhash(
            instructions=[tip_instruction],
            payer=keypair.pubkey(),
            blockhash=trade_blockhash  # MUST match trade tx
        )
        
        tip_tx = VersionedTransaction(tip_message, [keypair])
        print("   ✓ Tip transaction created")
        
        # Serialize both transactions
        trade_tx_b58 = base58.b58encode(bytes(trade_tx)).decode('utf-8')
        tip_tx_b58 = base58.b58encode(bytes(tip_tx)).decode('utf-8')
        
        # Send bundle - transactions execute in order
        print(f"   Sending bundle to Jito...")
        bundle_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendBundle",
            "params": [[trade_tx_b58, tip_tx_b58]]
        }
        
        response = requests.post(
            f"{JITO_BLOCK_ENGINE_URL}/api/v1/bundles",
            json=bundle_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        result = response.json()
        print(f"   Response: {result}")
        
        if response.status_code == 200 and 'result' in result:
            bundle_id = result['result']
            print(f"\n✅ Bundle sent!")
            print(f"   Bundle ID: {bundle_id}")
            
            # Monitor bundle status
            for i in range(5):
                time.sleep(2)
                status_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBundleStatuses",
                    "params": [[bundle_id]]
                }
                
                status_resp = requests.post(
                    f"{JITO_BLOCK_ENGINE_URL}/api/v1/bundles",
                    json=status_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if status_resp.status_code == 200:
                    status = status_resp.json()
                    print(f"   Status check {i+1}: {status}")
                    
                    # Check if bundle landed
                    if 'result' in status and status['result'].get('value'):
                        bundle_status = status['result']['value'][0]
                        if bundle_status.get('confirmation_status') == 'confirmed':
                            print(f"\n✅ Bundle confirmed!")
                            if 'transactions' in bundle_status:
                                for tx_sig in bundle_status['transactions']:
                                    print(f"   Transaction: https://solscan.io/tx/{tx_sig}")
                            break
            
            return bundle_id
        else:
            error = result.get('error', {})
            print(f"\n❌ Bundle failed: {error.get('message', 'Unknown error')}")
            
            # Common error solutions
            if 'write lock' in str(error).lower():
                print("\n💡 Tip: The bundle needs a transaction that write-locks a tip account")
                print("   This usually means the tip transaction format is incorrect")
            
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def send_with_standard_rpc(trade_tx):
    """Fallback: Send via standard RPC (no Jito)"""
    print("\n3. Sending transaction via Standard RPC...")
    
    try:
        client = Client(HELIUS_API_URL)
        signature = client.send_transaction(
            trade_tx,
            opts={"skip_preflight": True, "max_retries": 0}
        ).value
        
        print(f"✅ Transaction sent!")
        print(f"   Signature: {signature}")
        print(f"   Explorer: https://solscan.io/tx/{signature}")
        
        return signature
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def buy(PUBLIC_KEY, PRIVATE_KEY, MINT_ADDRESS, RPC_URL):
    """Execute Pump.fun trade"""
    use_jito=True, 
    jito_tip_lamports=100000
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    print("="*80)
    print("PUMP.FUN JITO BUNDLE TRADER")
    print("="*80)
    print(f"Wallet: {PUBLIC_KEY}")
    print(f"Token: {MINT_ADDRESS}")
    print(f"Method: {'Jito Bundle' if use_jito else 'Standard RPC'}")
    if use_jito:
        print(f"Jito Tip: {jito_tip_lamports} lamports ({jito_tip_lamports/1e9} SOL)")
    print("="*80)
    
    # Get transaction from PumpPortal
    print("\n1. Requesting transaction from PumpPortal...")
    try:
        response = requests.post(
            url="https://pumpportal.fun/api/trade-local",
            json={
                "publicKey": PUBLIC_KEY,
                "action": "buy",
                "mint": MINT_ADDRESS,
                "amount": 0.01,
                "denominatedInSol": "true",
                "slippage": 10,
                "priorityFee": 0.0005,
                "pool": "pump"
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
        
        print("   ✓ Transaction received")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    # Sign transaction
    print("\n2. Signing transaction...")
    try:
        unsigned_tx = VersionedTransaction.from_bytes(response.content)
        trade_tx = VersionedTransaction(unsigned_tx.message, [keypair])
        print("   ✓ Transaction signed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    # Send transaction
    if use_jito:
        result = send_jito_bundle_simple(trade_tx, jito_tip_lamports)
    # else:
        # result = send_with_standard_rpc(trade_tx)
    
    return result


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