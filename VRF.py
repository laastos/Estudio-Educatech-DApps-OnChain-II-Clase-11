import os
import json
import time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

with open("contracts/VRFv2Consumer_abi.json") as f:
    info_json = json.load(f)
ABI = info_json["output"]["abi"]

# la direccion del contrato debe ser una variable de entorno
CONTRACT_VRF = "0xC72c60f234bCDFA898faC832833462CCb77C6b75"
WALLET = os.environ["WALLET"]
PRIV_KEY = os.environ["PRIV_KEY"]

sepolia_rpc_url = 'https://endpoints.omniatech.io/v1/arbitrum/sepolia/public'


def oracle_random_number():
    """
    this function call a random number from chainlink
    :return:
    """
    w3 = Web3(Web3.HTTPProvider(sepolia_rpc_url))

    if w3.is_connected():
        print("-" * 50)
        print("Connection Successful")
        print("-" * 50)
    else:
        print("Connection Failed")

    contract_address = CONTRACT_VRF
    contract_abi = ABI
    queries = 4

    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    account_address = WALLET
    private_key = PRIV_KEY

    function_data = contract.functions.requestRandomWords().build_transaction({
        'from': account_address,
        'gas': 5000000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account_address),
        'chainId': 421614,
    })

    signed_transaction = w3.eth.account.sign_transaction(function_data, private_key)
    transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    print("Hash send transaction: ", transaction_hash.hex())

    time.sleep(10)

    result = contract.functions.lastRequestId().call()
    print("lastRequestId:", result)
    r_number = None

    for i in range(queries):
        request_status = contract.functions.s_requests(result).call()
        if request_status[0]:
            raw_number = contract.functions.getRequestStatus(result)
            r_number = raw_number.arguments[0]
            print("Request OK")
            break

        else:
            print("Processing request")
            r_number = 24839797740798566204421960018987282271019208905979606455200616560608859319253
            time.sleep(10)

    print("VRF random number: ")
    print(r_number)

    return r_number
