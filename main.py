from web3 import Web3, exceptions
from erc20_abi import ABI
from flask import Flask, request
from settings import POLYGON_URL, ADDRESS

app = Flask(__name__)

web3 = Web3(Web3.HTTPProvider(POLYGON_URL))


checksum_token_address = web3.to_checksum_address(ADDRESS)

contract = web3.eth.contract(address=checksum_token_address, abi=ABI)


@app.route('/get_balance/<address>')
def get_balance(address: str):
    """
    Receiving balance for one address

    :param address: address for receiving balance
    """

    try:
        balance = contract.functions.balanceOf(address).call()

        return {'data': {'address': address, 'balance': balance}}, 200

    except exceptions.Web3ValidationError as error:
        return {'error': 'Web3ValidationError', 'message': f'{error}'}, 400

    except exceptions.InvalidAddress as error:
        return {'error': 'InvalidAddress', 'message': f'{error}'}, 400

    except Exception as error:
        return {'error': 'InternalError', 'message': error}, 500


@app.route('/get_balance_batch', methods=['POST'])
def get_balance_batch():
    """
    Receiving balances for multiple addresses
    """

    addresses = request.json.get('addresses')

    if not addresses:
        return {'error': 'BadRequest', 'message': 'Required parameter is missing: address'}, 400

    if not isinstance(addresses, list):
        return {'error': 'BadRequest', 'message': 'Parameter addresses must be list'}, 400

    try:
        balances = []
        for address in addresses:
            balances.append({'address': address, 'balance': contract.functions.balanceOf(address).call()})
        return {'data': balances}, 200

    except exceptions.Web3ValidationError as error:
        return {'error': 'Web3ValidationError', 'message': f'{error}'}, 400

    except exceptions.InvalidAddress as error:
        return {'error': 'InvalidAddress', 'message': f'{error}'}, 400

    except Exception as error:
        return {'error': 'InternalError', 'message': error}, 500


if __name__ == "__main__":
    app.run()

