# trade.py

import requests
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
import time

# Note: The dotenv loading and variable definitions are removed from this file.

def buy(public_key, private_key, mint_address, rpc_url):
    """
    Executes a buy transaction.
    Accepts configuration as arguments.
    """
    print("🔹 Executing BUY...")
    try:
        response = requests.post(url="https://pumpportal.fun/api/trade-local", data={
            "publicKey": public_key,
            "action": "buy",
            "mint": mint_address,
            "amount": 0.009,
            "denominatedInSol": "true",
            "slippage": 25,
            # "priorityFee": 0.0001,
            # "priorityFee": 0.00025,
            "priorityFee": 0.00001,
            "pool": "auto"
        })
        response.raise_for_status() # Raise an exception for bad status codes

        keypair = Keypair.from_base58_string(private_key)
        tx = VersionedTransaction(VersionedTransaction.from_bytes(response.content).message, [keypair])

        # config = RpcSendTransactionConfig(preflight_commitment=CommitmentLevel.Confirmed)
        # This saves one full network request, which is a huge speed boost
        config = RpcSendTransactionConfig(skip_preflight=True)
        
        rpc_response = requests.post(
            url=rpc_url,
            headers={"Content-Type": "application/json"},
            data=SendVersionedTransaction(tx, config).to_json()
        )
        rpc_response.raise_for_status()
        
        data = rpc_response.json()
        print("#" * 150)
        print(data)
        print("#" * 150)
        
        if 'result' in data:
            txSignature = data['result']
            print(f'✅ BUY successful! Transaction: https://solscan.io/tx/{txSignature}')
        else:
            print(f"❌ BUY failed. Response: {data}")

    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred during the API request: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred in buy(): {e}")


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
        "priorityFee": 0.00001,
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
    txSignature = response.json()['result']
    print(f'Transaction: https://solscan.io/tx/{txSignature}')

    # except Exception as e:
    #     print(f"❌ An unexpected error occurred in sell(): {e}")