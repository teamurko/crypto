import argparse
from typing import Optional

from web3 import Web3
from web3.types import BlockData


def main(provider_url: str, action: str, **kwargs) -> None:
    w3 = _create_client(provider_url)
    if action not in ACTIONS:
        raise Exception(f'Unknown action {action}, must be one of {ACTIONS.keys()}')
    ACTIONS[action](w3=w3, **kwargs)


def _print_balance(w3: Web3, account: str, *args, **kwargs) -> None:
    print(f'Balance: {w3.eth.get_balance(account)}')


def _get_block_data(w3: Web3, block_number: int) -> BlockData:
    return w3.eth.get_block(block_number)


def _print_block_data(w3: Web3, block_number: int, *args, **kwargs) -> None:
    latest_block_info: BlockData = _get_block_data(w3, block_number or w3.eth.block_number)
    print(f'Block #{w3.eth.block_number}:')
    for field, value in latest_block_info.items():
        if isinstance(value, list):
            print(f'  {field}:')
            for e in value:
                print(f'    {e!r}')
        else:
            print(f'  {field}: {value!r}')


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
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ethereum wallet cli app')
    parser.add_argument('-p', '--provider', type=str, help='Node provider url, [https|wss]://<url>')
    parser.add_argument('-a', '--account', type=str, nargs='?', help='Account address')
    parser.add_argument('-t', '--action_type', type=str, help=f'Action type: {ACTIONS}')
    parser.add_argument('-b', '--block_number', type=int, nargs='?', help='Block number')
    args: argparse.Namespace = parser.parse_args()
    print(args)
    main(provider_url=args.provider, action=args.action_type, account=args.account, block_number=args.block_number)
