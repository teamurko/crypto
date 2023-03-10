import argparse
from typing import Any, ItemsView

from eth_typing import HexStr
from web3 import Web3
from web3.types import BlockData


def main(provider_url: str, action: str, **kwargs) -> None:
    w3 = _create_client(provider_url)
    if action not in ACTIONS:
        raise Exception(f'Unknown action {action}, must be one of {ACTIONS.keys()}')
    ACTIONS[action](w3=w3, **kwargs)


def _print_balance(w3: Web3, account: HexStr, *args, **kwargs) -> None:
    wei = w3.eth.get_balance(account)
    ether = w3.fromWei(wei, 'ether')
    print(f'Balance: {ether} ether')


def _get_block_data(w3: Web3, block_number: int) -> BlockData:
    return w3.eth.get_block(block_number)


def _pprint_data(items: ItemsView[str, Any]) -> None:
    for field, value in items:
        if isinstance(value, list):
            print(f'  {field}:')
            for e in value:
                print(f'    {e!r}')
        else:
            print(f'  {field}: {value!r}')


def _print_block_data(w3: Web3, block_number: int, *args, **kwargs) -> None:
    block_info: BlockData = _get_block_data(w3, block_number or w3.eth.block_number)
    print(f'Block #{w3.eth.block_number}:')
    _pprint_data(block_info.items())


def _print_transaction_data(w3: Web3, transaction_id: HexStr, *args, **kwargs) -> None:
    transaction = w3.eth.get_transaction(transaction_id)
    print(f'Transaction {transaction_id}:')
    _pprint_data(transaction.items())


def _send_transaction(w3: Web3, account: HexStr, private_key: HexStr, to_account: HexStr, *args, **kwargs) -> None:
    nonce = w3.eth.get_transaction_count(account)
    tx = {
        'nonce': nonce,
        'to': to_account,
        'value': w3.toWei(1, 'micro'),
        'gas': 2_000_000,
        'gasPrice': w3.toWei('50', 'gwei')
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f'Executed send transaction {tx}, hash {w3.toHex(tx_hash)}')


def _create_client(provider_url: str) -> Web3:
    if provider_url.startswith('https'):
        return Web3(Web3.HTTPProvider(provider_url))
    elif provider_url.startswith('wss'):
        return Web3(Web3.WebsocketProvider(provider_url))
    else:
        raise Exception(f'Only https/wss protocols are supported, but provided {provider_url}')


ACTIONS = {
    'get_balance': _print_balance,
    'get_block_data': _print_block_data,
    'get_transaction_data': _print_transaction_data,
    'send_transaction': _send_transaction,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ethereum wallet cli app')
    parser.add_argument('-p', '--provider', type=str, help='Node provider url, [https|wss]://<url>')
    parser.add_argument('-a', '--account', type=HexStr, nargs='?', help='Account address')
    parser.add_argument('-k', '--private_key', type=HexStr, nargs='?', help='Account private key to sign txs with')
    parser.add_argument('-m', '--action_type', type=str, help=f'Action type: {ACTIONS}')
    parser.add_argument('-b', '--block_number', type=int, nargs='?', help='Block number')
    parser.add_argument('-t', '--transaction_id', type=HexStr, nargs='?', help='Transaction id')
    parser.add_argument('-d', '--to_account', type=HexStr, nargs='?', help='Account address to send to')
    args: argparse.Namespace = parser.parse_args()
    main(
        provider_url=args.provider,
        action=args.action_type,
        account=args.account,
        private_key=args.private_key,
        block_number=args.block_number,
        transaction_id=args.transaction_id,
        to_account=args.to_account,
    )
