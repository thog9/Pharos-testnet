import os
import sys
import asyncio
import random
import time
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector
from typing import List

# Initialize colorama
init(autoreset=True)

# Border width
BORDER_WIDTH = 80

# Network and contract constants
NETWORK_URL = "https://testnet.dplabs-internal.com"
CHAIN_ID = 688688
EXPLORER_URL = "https://testnet.pharosscan.xyz/tx/0x"
SWAP_ROUTER = Web3.to_checksum_address("0x1a4de519154ae51200b0ad7c90f7fac75547888a")

# Token definitions
TOKENS = {
    "PHRS": {"address": Web3.to_checksum_address("0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364"), "decimals": 18},
    "USDC": {"address": Web3.to_checksum_address("0x72df0bcd7276f2dfbac900d1ce63c272c4bccced"), "decimals": 6},
    "USDT": {"address": Web3.to_checksum_address("0xd4071393f8716661958f766df660033b3d35fd29"), "decimals": 6},
}

# Fee tiers
FEE_TIERS = {
    "LOW": 500,    # 0.05%
    "MEDIUM": 3000, # 0.3%
    "HIGH": 10000   # 1%
}

# Configuration
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [10, 30],
    "PAUSE_BETWEEN_SWAPS": [5, 15],
    "MAX_CONCURRENCY": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.001,  # Native token
    "DEFAULT_GAS": 300000,     # Default gas limit for ERC20 swaps
    "APPROVAL_GAS": 100000,    # Default gas limit for approvals
    "RETRY_DELAY": [5, 15],    # Delay between retries
}

# ABI definitions
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "success", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "remaining", "type": "uint256"}],
        "type": "function"
    }
]

# Swap Router ABI (simplified for exactInputSingle and multicall)
SWAP_ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
            {"internalType": "bytes[]", "name": "data", "type": "bytes[]"}
        ],
        "name": "multicall",
        "outputs": [{"internalType": "bytes[]", "name": "results", "type": "bytes[]"}],
        "stateMutability": "payable",
        "type": "function"
    }
]

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'TOKEN SWAP - PHAROS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallets': 'ℹ Thông tin: Đang xử lý {count} ví',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ: {balance:.6f} {symbol} (cần ít nhất {required:.6f})',
        'preparing_swap': 'Đang chuẩn bị swap...',
        'sending_swap': 'Đang gửi hoán đổi...',
        'success': '✅ Swap thành công: {from_token} -> {to_token}',
        'failure': '❌ Swap thất bại',
        'address': 'Địa chỉ',
        'amount': 'Số lượng',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư',
        'balance_info': 'Số dư',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✔ HOÀN THÀNH: {successful}/{total} SWAP THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': '✅ Thành công: Đã kết nối với mạng Pharos Testnet',
        'connect_error': '❌ Không thể kết nối với RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ Không tìm thấy tệp pv BO không tìm thấy',
        'pvkey_empty': '❌ Không tìm thấy khóa riêng hợp lệ',
        'pvkey_error': '❌ Không thể đọc pvkey.txt',
        'invalid_key': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'swap_type': 'Loại hoán đổi',
        'gas_estimation_failed': 'Không thể ước tính gas',
        'default_gas_used': 'Sử dụng gas mặc định: {gas}',
        'tx_rejected': '⚠ Giao dịch bị từ chối bởi hợp đồng hoặc mạng',
        'select_swap': 'Chọn loại swap',
        'invalid_choice': 'Lựa chọn không hợp lệ, vui lòng chọn số hợp lệ',
        'amount_prompt': 'Nhập số lượng token để swap',
        'invalid_amount': 'Số lượng không hợp lệ, vui lòng nhập số lớn hơn 0',
        'times_prompt': 'Nhập số lần hoán đổi',
        'invalid_times': 'Số không hợp lệ, vui lòng nhập số nguyên dương',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'approving_token': 'Đang phê duyệt {token} cho swap...',
        'approval_success': '✅ Phê duyệt thành công: {token}',
        'approval_failed': '❌ Phê duyệt thất bại: {token}',
    },
    'en': {
        'title': 'TOKEN SWAP - PHAROS TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallets': 'ℹ Info: Processing {count} wallets',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance: {balance:.6f} {symbol} (need at least {required:.6f})',
        'preparing_swap': 'Preparing swap...',
        'sending_swap': 'Sending swap...',
        'success': '✅ Swap successful: {from_token} -> {to_token}',
        'failure': '❌ Swap failed',
        'address': 'Address',
        'amount': 'Amount',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance',
        'balance_info': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✔ COMPLETED: {successful}/{total} SWAPS SUCCESSFUL',
        'error': 'Error',
        'connect_success': '✅ Success: Connected to Pharos Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'swap_type': 'Swap type',
        'gas_estimation_failed': 'Failed to estimate gas',
        'default_gas_used': 'Using default gas: {gas}',
        'tx_rejected': '⚠ Transaction rejected by contract or network',
        'select_swap': 'Select swap type',
        'invalid_choice': 'Invalid choice, please select a valid number',
        'amount_prompt': 'Enter token amount to swap',
        'invalid_amount': 'Invalid amount, please enter a number greater than 0',
        'times_prompt': 'Enter number of swaps',
        'invalid_times': 'Invalid number, please enter a positive integer',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'approving_token': 'Approving {token} for swap...',
        'approval_success': '✅ Approval successful: {token}',
        'approval_failed': '❌ Approval failed: {token}',
    }
}

# Display functions
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def print_message(message: str, color=Fore.YELLOW):
    print(f"{color}{message}{Style.RESET_ALL}")

def print_wallets_summary(count: int, language: str = 'en'):
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['processing_wallets'].format(count=count)}{Style.RESET_ALL}")
    print()

def display_all_wallets_balances(w3: Web3, private_keys: List[tuple], language: str = 'en'):
    print_border(LANG[language]['balance_info'], Fore.CYAN)
    print(f"{Fore.CYAN}  Wallet | {'PHRS':<10} | {'USDC':<10} | {'USDT':<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * 6} | {'-' * 10} | {'-' * 10} | {'-' * 10}{Style.RESET_ALL}")
    
    for i, (profile_num, key) in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        phrs_balance = check_balance(w3, address, "native", 18, language)
        usdc_balance = check_balance(w3, address, TOKENS["USDC"]["address"], TOKENS["USDC"]["decimals"], language)
        usdt_balance = check_balance(w3, address, TOKENS["USDT"]["address"], TOKENS["USDT"]["decimals"], language)
        print(f"{Fore.YELLOW}  {i:<6} | {phrs_balance:>10.6f} | {usdc_balance:>10.6f} | {usdt_balance:>10.6f}{Style.RESET_ALL}")
    print()

# Utility functions
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add private keys here, one per line\n# Example: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
            sys.exit(1)
        
        valid_keys = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                key = line.strip()
                if key and not key.startswith('#'):
                    if is_valid_private_key(key):
                        if not key.startswith('0x'):
                            key = '0x' + key
                        valid_keys.append((i, key))
                    else:
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key}{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add proxies here, one per line\n# Example: socks5://user:pass@host:port or http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not line.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

async def get_proxy_ip(proxy: str = None, language: str = 'en') -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
        }
        if proxy:
            if proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')):
                connector = ProxyConnector.from_url(proxy)
            else:
                parts = proxy.split(':')
                if len(parts) == 4:  # host:port:user:pass
                    proxy_url = f"socks5://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
                    connector = ProxyConnector.from_url(proxy_url)
                elif len(parts) == 3 and '@' in proxy:  # user:pass@host:port
                    connector = ProxyConnector.from_url(f"socks5://{proxy}")
                else:
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['invalid_proxy'].format(proxy=proxy)}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get("https://api.ipify.org?format=json", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
        else:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get("https://api.ipify.org?format=json", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}{Style.RESET_ALL}")
        return LANG[language]['unknown']

def connect_web3(language: str = 'en'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if not w3.is_connected():
            print(f"{Fore.RED}  ✖ {LANG[language]['connect_error']}{Style.RESET_ALL}")
            sys.exit(1)
        print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} │ Chain ID: {w3.eth.chain_id}{Style.RESET_ALL}")
        return w3
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def check_balance(w3: Web3, address: str, token_address: str, decimals: int, language: str = 'en') -> float:
    if token_address == "native":
        try:
            balance = w3.eth.get_balance(address)
            return float(w3.from_wei(balance, 'ether'))
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
            return -1
    else:
        token_abi = ERC20_ABI
        checksum_address = Web3.to_checksum_address(token_address)
        contract = w3.eth.contract(address=checksum_address, abi=token_abi)
        try:
            balance = contract.functions.balanceOf(address).call()
            return balance / (10 ** decimals)
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
            return -1

async def get_fee_data(w3: Web3, language: str = 'en'):
    try:
        gas_price = w3.eth.gas_price
        max_fee_per_gas = int(gas_price * 1.2)  # 20% buffer
        max_priority_fee_per_gas = int(gas_price * 1.2)  # 20% buffer
        return {"maxFeePerGas": max_fee_per_gas, "maxPriorityFeePerGas": max_priority_fee_per_gas}
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['error']}: {str(e)}. Using default values.{Style.RESET_ALL}")
        return {
            "maxFeePerGas": w3.to_wei('1.2', 'gwei'),
            "maxPriorityFeePerGas": w3.to_wei('1.2', 'gwei')
        }

async def estimate_gas(w3: Web3, tx_params: dict, language: str = 'en'):
    try:
        gas_estimate = w3.eth.estimate_gas(tx_params)
        return int(gas_estimate * 1.3)  # 30% buffer
    except Exception as e:
        #print(f"{Fore.YELLOW}  ⚠ {LANG[language]['gas_estimation_failed']}: {str(e)}. Using default values.{Style.RESET_ALL}")
        return CONFIG['DEFAULT_GAS'] if tx_params.get('value', 0) == 0 else 200000

async def approve_token(w3: Web3, private_key: str, token_address: str, spender: str, amount: int, language: str = 'en', nonce: int = None, proxy: str = None):
    account = Account.from_key(private_key)
    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
    if nonce is None:
        nonce = w3.eth.get_transaction_count(account.address, 'pending')
    
    current_allowance = token_contract.functions.allowance(account.address, Web3.to_checksum_address(spender)).call()
    if current_allowance >= amount:
        return True
    
    print(f"{Fore.CYAN}  > {LANG[language]['approving_token'].format(token=token_address)}{Style.RESET_ALL}")
    
    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")
            
            fee_data = await get_fee_data(w3, language)
            tx = token_contract.functions.approve(Web3.to_checksum_address(spender), 2**256 - 1).build_transaction({
                'nonce': nonce,
                'from': account.address,
                'chainId': CHAIN_ID,
                'maxFeePerGas': fee_data['maxFeePerGas'],
                'maxPriorityFeePerGas': fee_data['maxPriorityFeePerGas']
            })
            try:
                tx['gas'] = await estimate_gas(w3, tx, language)
                print(f"{Fore.YELLOW}    Gas estimated: {tx['gas']}{Style.RESET_ALL}")
            except Exception as e:
                tx['gas'] = CONFIG['APPROVAL_GAS']
                print(f"{Fore.YELLOW}    {LANG[language]['gas_estimation_failed']}: {str(e)}. {LANG[language]['default_gas_used'].format(gas=CONFIG['APPROVAL_GAS'])}{Style.RESET_ALL}")
            
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
            if receipt.status == 1:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['approval_success'].format(token=token_address)} │ Tx: {EXPLORER_URL}{tx_hash.hex()}{Style.RESET_ALL}")
                return True
            print(f"{Fore.RED}  ✖ {LANG[language]['approval_failed'].format(token=token_address)} │ Tx: {EXPLORER_URL}{tx_hash.hex()}{Style.RESET_ALL}")
            return False
        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(CONFIG['RETRY_DELAY'][0], CONFIG['RETRY_DELAY'][1])
                print(f"{Fore.RED}  ✖ {LANG[language]['approval_failed'].format(token=token_address)}: {str(e)} │ Tx: {EXPLORER_URL}{tx_hash.hex() if 'tx_hash' in locals() else 'Not sent'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['approval_failed'].format(token=token_address)}: {str(e)} │ Tx: {EXPLORER_URL}{tx_hash.hex() if 'tx_hash' in locals() else 'Not sent'}{Style.RESET_ALL}")
            return False

async def swap(w3: Web3, private_key: str, wallet_index: int, from_token: str, to_token: str, amount_in: int, swap_times: int, language: str = 'en', proxy: str = None):
    account = Account.from_key(private_key)
    sender_address = account.address
    contract = w3.eth.contract(address=SWAP_ROUTER, abi=SWAP_ROUTER_ABI)
    successful_swaps = 0
    
    token_in = TOKENS[from_token]["address"]
    token_out = TOKENS[to_token]["address"]
    is_native_swap = from_token == "PHRS"
    
    nonce = w3.eth.get_transaction_count(sender_address, 'pending')
    
    for i in range(swap_times):
        print_border(f"Swap {i+1}/{swap_times}: {from_token} -> {to_token}", Fore.YELLOW)
        print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
        
        public_ip = await get_proxy_ip(proxy, language)
        proxy_display = proxy if proxy else LANG[language]['no_proxy']
        print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")
        
        phrs_balance = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
        if phrs_balance < CONFIG['MINIMUM_BALANCE']:
            print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=phrs_balance, symbol='PHRS', required=CONFIG['MINIMUM_BALANCE'])}{Style.RESET_ALL}")
            break
        
        if is_native_swap:
            if amount_in > w3.eth.get_balance(sender_address):
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=phrs_balance, symbol='PHRS', required=w3.from_wei(amount_in, 'ether'))}{Style.RESET_ALL}")
                break
        else:
            token_balance = check_balance(w3, sender_address, token_in, TOKENS[from_token]["decimals"], language)
            if amount_in > token_balance * (10 ** TOKENS[from_token]["decimals"]):
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=token_balance, symbol=from_token, required=amount_in / (10 ** TOKENS[from_token]['decimals']))}{Style.RESET_ALL}")
                break
        
        print(f"{Fore.CYAN}  > {LANG[language]['preparing_swap']}{Style.RESET_ALL}")
        deadline = int(time.time()) + 20 * 60
        
        for attempt in range(CONFIG['MAX_RETRIES']):
            try:
                fee_data = await get_fee_data(w3, language)
                
                # Use functions interface instead of encodeABI
                exact_input_params = (
                    token_in,
                    token_out,
                    FEE_TIERS["LOW"],
                    sender_address,
                    amount_in,
                    0,  # No minimum output
                    0   # No price limit
                )
                
                # Create the function selector for exactInputSingle
                exact_input_single_data = contract.functions.exactInputSingle(exact_input_params).build_transaction({
                    'chainId': CHAIN_ID,
                    'gas': 0,
                    'maxFeePerGas': 0,
                    'maxPriorityFeePerGas': 0,
                    'nonce': 0
                })['data']
                
                # Create the function call for multicall
                multicall_tx = contract.functions.multicall(
                    deadline, 
                    [exact_input_single_data]
                ).build_transaction({
                    'nonce': nonce,
                    'from': sender_address,
                    'chainId': CHAIN_ID,
                    'maxFeePerGas': fee_data['maxFeePerGas'],
                    'maxPriorityFeePerGas': fee_data['maxPriorityFeePerGas']
                })
                
                if is_native_swap:
                    multicall_tx['value'] = amount_in
                else:
                    multicall_tx['value'] = 0
                    if not await approve_token(w3, private_key, token_in, SWAP_ROUTER, amount_in, language, nonce, proxy):
                        break
                    nonce += 1
                
                try:
                    multicall_tx['gas'] = await estimate_gas(w3, multicall_tx, language)
                    print(f"{Fore.YELLOW}    Gas estimated: {multicall_tx['gas']}{Style.RESET_ALL}")
                except Exception as e:
                    multicall_tx['gas'] = CONFIG['DEFAULT_GAS'] if not is_native_swap else 200000
                    print(f"{Fore.YELLOW}    {LANG[language]['gas_estimation_failed']}: {str(e)}. {LANG[language]['default_gas_used'].format(gas=multicall_tx['gas'])}{Style.RESET_ALL}")
                
                print(f"{Fore.CYAN}  > {LANG[language]['sending_swap']}{Style.RESET_ALL}")
                signed_tx = w3.eth.account.sign_transaction(multicall_tx, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
                
                receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
                
                if receipt.status == 1:
                    successful_swaps += 1
                    phrs_balance_after = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
                    to_token_balance = check_balance(w3, sender_address, token_out, TOKENS[to_token]["decimals"], language)
                    print(f"{Fore.GREEN}  ✔ {LANG[language]['success'].format(from_token=from_token, to_token=to_token)} │ Tx: {tx_link}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['address']:<12}: {sender_address}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['block']:<12}: {receipt['blockNumber']}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['gas']:<12}: {receipt['gasUsed']}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['balance']:<12}: {phrs_balance_after:.6f} PHRS | {to_token:<8}: {to_token_balance:.6f}{Style.RESET_ALL}")
                    nonce += 1
                    break
                else:
                    print(f"{Fore.RED}  ✖ {LANG[language]['failure']} │ Tx: {tx_link}{Style.RESET_ALL}")
                    print(f"{Fore.RED}    {LANG[language]['tx_rejected']}{Style.RESET_ALL}")
                    break
                
            except Exception as e:
                if attempt < CONFIG['MAX_RETRIES'] - 1:
                    delay = random.uniform(CONFIG['RETRY_DELAY'][0], CONFIG['RETRY_DELAY'][1])
                    print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
                    continue
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}{Style.RESET_ALL}")
                break
        
        if i < swap_times - 1:
            delay = random.uniform(CONFIG['PAUSE_BETWEEN_SWAPS'][0], CONFIG['PAUSE_BETWEEN_SWAPS'][1])
            print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
    
    return successful_swaps

async def run_swap(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    proxies = load_proxies('proxies.txt', language)
    
    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    display_all_wallets_balances(w3, private_keys, language)
    print_separator()

    total_swaps = 0
    successful_swaps = 0

    token_list = ["PHRS", "USDC", "USDT"]

    print(f"{Fore.CYAN}{LANG[language]['select_swap']}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  Available Tokens{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  ----------------{Style.RESET_ALL}")
    for idx, token in enumerate(token_list, 1):
        targets = " | ".join(t for t in token_list if t != token)
        print(f"{Fore.YELLOW}  {idx}. {token} ↔ {targets}{Style.RESET_ALL}")

    print()
    while True:
        print(f"{Fore.CYAN}Select token to swap from [1-3]:{Style.RESET_ALL}")
        try:
            token_choice = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if 1 <= token_choice <= 3:
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")

    from_token = token_list[token_choice - 1]

    print(f"\n{Fore.CYAN}{from_token} Swap Pairs{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  ------------{Style.RESET_ALL}")
    swap_pairs = [t for t in token_list if t != from_token]
    for idx, to_token in enumerate(swap_pairs, 1):
        print(f"{Fore.YELLOW}  {idx}. {from_token} → {to_token}{Style.RESET_ALL}")

    print()
    while True:
        print(f"{Fore.CYAN}Select swap pair [1-{len(swap_pairs)}]:{Style.RESET_ALL}")
        try:
            pair_choice = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if 1 <= pair_choice <= len(swap_pairs):
                break
            print(f"{Fore.RED}  ✖ Invalid choice, please select from 1-{len(swap_pairs)}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ Invalid choice, please select from 1-{len(swap_pairs)}{Style.RESET_ALL}")

    to_token = swap_pairs[pair_choice - 1]

    min_balance = float('inf')
    for _, key in private_keys:
        account = Account.from_key(key)
        balance = check_balance(w3, account.address, TOKENS[from_token]["address"] if from_token != "PHRS" else "native", TOKENS[from_token]["decimals"] if from_token != "PHRS" else 18, language)
        min_balance = min(min_balance, balance)

    print()
    while True:
        print(f"{Fore.CYAN}{LANG[language]['amount_prompt']} {Fore.YELLOW}(Max: {min_balance:.4f} {from_token}){Style.RESET_ALL}")
        try:
            amount_input = float(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if amount_input > 0 and amount_input <= min_balance:
                amount_in = int(amount_input * 10 ** TOKENS[from_token]["decimals"])
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_amount']} or exceeds balance{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_amount']}{Style.RESET_ALL}")

    print()
    while True:
        print(f"{Fore.CYAN}{LANG[language]['times_prompt']}:{Style.RESET_ALL}")
        try:
            swap_times = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if swap_times > 0:
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_times']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_times']}{Style.RESET_ALL}")

    print_separator()
    random.shuffle(private_keys)
    print_wallets_summary(len(private_keys), language)

    async def process_wallet(index, profile_num, private_key):
        nonlocal successful_swaps, total_swaps
        proxy = proxies[index % len(proxies)] if proxies else None
        
        async with semaphore:
            swaps = await swap(w3, private_key, profile_num, from_token, to_token, amount_in, swap_times, language, proxy)
            successful_swaps += swaps
            total_swaps += swap_times
            if index < len(private_keys) - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                print_message(f"  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)

    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    tasks = [process_wallet(i, profile_num, key) for i, (profile_num, key) in enumerate(private_keys)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_swaps, total=total_swaps)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_swap('en'))
