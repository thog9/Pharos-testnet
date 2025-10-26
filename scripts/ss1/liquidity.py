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
from typing import List, Tuple

# Initialize colorama
init(autoreset=True)

# Border width
BORDER_WIDTH = 80

# Constants
NETWORK_URL = "https://testnet.dplabs-internal.com"
CHAIN_ID = 688688
EXPLORER_URL = "https://testnet.pharosscan.xyz/tx/0x"
IP_CHECK_URL = "https://api.ipify.org?format=json"
MAX_WAIT_TIME = 180  # Timeout 3 minutes
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [10, 30],
    "PAUSE_BETWEEN_ACTIONS": [5, 15],
    "MAX_CONCURRENCY": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.00009,  # PHRS
    "DEFAULT_GAS": 600000,
    "APPROVE_GAS": 100000,
}

# Token definitions with checksummed addresses
TOKEN_ADDRESSES = {
    "PHRS": {"address": Web3.to_checksum_address("0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364"), "decimals": 18},
    "USDC": {"address": Web3.to_checksum_address("0xad902cf99c2de2f1ba5ec4d642fd7e49cae9ee37"), "decimals": 18},
    "USDT": {"address": Web3.to_checksum_address("0xEd59De2D7ad9C043442e381231eE3646FC3C2939"), "decimals": 18},
}

# Contract addresses
CONTRACT_ADDRESSES = {
    "positionManager": Web3.to_checksum_address("0xF8a1D4FF0f9b9Af7CE58E1fc1833688F3BFd6115"),
}

# Fee tiers
FEE_TIERS = {
    "LOW": 500,    # 0.05%
    "MEDIUM": 3000, # 0.3%
    "HIGH": 10000   # 1%
}

# Position Manager ABI
POSITION_MANAGER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "token0", "type": "address"},
                    {"internalType": "address", "name": "token1", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "int24", "name": "tickLower", "type": "int24"},
                    {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                    {"internalType": "uint256", "name": "amount0Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount0Min", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Min", "type": "uint256"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                ],
                "internalType": "tuple",
                "name": "",
                "type": "tuple",
            }
        ],
        "name": "mint",
        "outputs": [
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
            {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"internalType": "uint256", "name": "amount1", "type": "uint256"},
        ],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount0Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount0Min", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Min", "type": "uint256"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                ],
                "internalType": "tuple",
                "name": "",
                "type": "tuple",
            }
        ],
        "name": "increaseLiquidity",
        "outputs": [
            {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"internalType": "uint256", "name": "amount1", "type": "uint256"},
        ],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "uint256", "name": "index", "type": "uint256"},
        ],
        "name": "tokenOfOwnerByIndex",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "positions",
        "outputs": [
            {"internalType": "uint96", "name": "nonce", "type": "uint96"},
            {"internalType": "address", "name": "operator", "type": "address"},
            {"internalType": "address", "name": "token0", "type": "address"},
            {"internalType": "address", "name": "token1", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"},
            {"internalType": "int24", "name": "tickLower", "type": "int24"},
            {"internalType": "int24", "name": "tickUpper", "type": "int24"},
            {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"internalType": "uint256", "name": "feeGrowthInside0LastX128", "type": "uint256"},
            {"internalType": "uint256", "name": "feeGrowthInside1LastX128", "type": "uint256"},
            {"internalType": "uint128", "name": "tokensOwed0", "type": "uint128"},
            {"internalType": "uint128", "name": "tokensOwed1", "type": "uint128"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

# ERC20 ABI
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "success", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
]

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'THÊM THANH KHOẢN - PHAROS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ: {balance:.6f} {symbol} (cần ít nhất {required:.6f})',
        'preparing_liquidity': 'Đang chuẩn bị thêm thanh khoản...',
        'sending_liquidity': 'Đang gửi giao dịch thêm thanh khoản...',
        'success': '✅ Thêm thanh khoản thành công: {token0} | {token1}',
        'failure': '❌ Thêm thanh khoản thất bại',
        'address': 'Địa chỉ ví',
        'contract_address': 'Địa chỉ hợp đồng',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư',
        'balance_info': 'Số dư ví',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': '✅ Thành công: Đã kết nối với mạng Pharos Testnet',
        'connect_error': '❌ Không thể kết nối với RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ Không tìm thấy tệp pvkey.txt',
        'pvkey_empty': '❌ Không tìm thấy khóa riêng hợp lệ',
        'pvkey_error': '❌ Không thể đọc pvkey.txt',
        'invalid_key': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'gas_estimation_failed': 'Không thể ước tính gas',
        'default_gas_used': 'Sử dụng gas mặc định: {gas}',
        'tx_rejected': '⚠ Giao dịch bị từ chối bởi hợp đồng hoặc mạng',
        'select_pair': 'Chọn cặp token để thêm thanh khoản',
        'invalid_choice': 'Lựa chọn không hợp lệ, vui lòng chọn từ danh sách',
        'amount_prompt': 'Nhập số lượng {token} để thêm thanh khoản',
        'invalid_amount': 'Số lượng không hợp lệ, vui lòng nhập số lớn hơn 0',
        'times_prompt': 'Nhập số lần thêm thanh khoản',
        'invalid_times': 'Số không hợp lệ, vui lòng nhập số nguyên dương',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'approve_success': '✅ Đã phê duyệt {token} cho Position Manager',
        'approve_failed': '❌ Phê duyệt {token} thất bại',
        'existing_position': 'Sử dụng vị trí thanh khoản hiện có #{tokenId}',
        'new_position': 'Tạo vị trí thanh khoản mới cho {token0} | {token1}',
    },
    'en': {
        'title': 'ADD LIQUIDITY - PHAROS TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance: {balance:.6f} {symbol} (need at least {required:.6f})',
        'preparing_liquidity': 'Preparing liquidity addition...',
        'sending_liquidity': 'Sending liquidity transaction...',
        'success': '✅ Liquidity added successfully: {token0} | {token1}',
        'failure': '❌ Liquidity addition failed',
        'address': 'Wallet address',
        'contract_address': 'Contract address',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance',
        'balance_info': 'Wallet Balances',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'connect_success': '✅ Success: Connected to Pharos Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'gas_estimation_failed': 'Failed to estimate gas',
        'default_gas_used': 'Using default gas: {gas}',
        'tx_rejected': '⚠ Transaction rejected by contract or network',
        'select_pair': 'Select token pair to add liquidity',
        'invalid_choice': 'Invalid choice, please select from the list',
        'amount_prompt': 'Enter amount of {token} to add liquidity',
        'invalid_amount': 'Invalid amount, please enter a number greater than 0',
        'times_prompt': 'Enter number of liquidity additions',
        'invalid_times': 'Invalid number, please enter a positive integer',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'approve_success': '✅ Approved {token} for Position Manager',
        'approve_failed': '❌ Failed to approve {token}',
        'existing_position': 'Using existing liquidity position #{tokenId}',
        'new_position': 'Creating new liquidity position for {token0} | {token1}',
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
    print_border(
        LANG[language]['processing_wallets'].format(count=count),
        Fore.MAGENTA
    )
    print()

def display_all_wallets_balances(w3: Web3, private_keys: List[Tuple[int, str]], language: str = 'en'):
    print_border(LANG[language]['balance_info'], Fore.CYAN)
    print(f"{Fore.CYAN}  Wallet | {'PHRS':<10} | {'USDC':<10} | {'USDT':<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * 6} | {'-' * 10} | {'-' * 10} | {'-' * 10}{Style.RESET_ALL}")

    for i, (profile_num, key) in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        phrs_balance = check_balance(w3, address, "native", 18, language)
        usdc_balance = check_balance(w3, address, TOKEN_ADDRESSES["USDC"]["address"], TOKEN_ADDRESSES["USDC"]["decimals"], language)
        usdt_balance = check_balance(w3, address, TOKEN_ADDRESSES["USDT"]["address"], TOKEN_ADDRESSES["USDT"]["decimals"], language)
        print(f"{Fore.YELLOW}  {i:<6} | {phrs_balance:>10.6f} | {usdc_balance:>10.3f} | {usdt_balance:>10.3f}{Style.RESET_ALL}")
    
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

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> List[Tuple[int, str]]:
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

def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> List[str]:
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
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
        else:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
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
        token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
        try:
            balance = token_contract.functions.balanceOf(address).call()
            return balance / (10 ** decimals)
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
            return -1

async def approve_token(w3: Web3, private_key: str, token_address: str, spender: str, amount: int, language: str = 'en', nonce: int = None, proxy: str = None):
    account = Account.from_key(private_key)
    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
    if nonce is None:
        nonce = w3.eth.get_transaction_count(account.address, 'pending')
    gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))
    
    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")
            
            tx = token_contract.functions.approve(Web3.to_checksum_address(spender), amount).build_transaction({
                'nonce': nonce,
                'from': account.address,
                'chainId': CHAIN_ID,
                'gas': CONFIG['APPROVE_GAS'],
                'gasPrice': gas_price
            })
            
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=MAX_WAIT_TIME))
            if receipt.status == 1:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['approve_success'].format(token=token_address)}{Style.RESET_ALL}")
                return True
            print(f"{Fore.RED}  ✖ {LANG[language]['approve_failed'].format(token=token_address)} │ Tx: {EXPLORER_URL}{tx_hash.hex()}{Style.RESET_ALL}")
            return False
        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print(f"{Fore.RED}  ✖ {LANG[language]['approve_failed'].format(token=token_address)}: {str(e)} │ Tx: {EXPLORER_URL}{tx_hash.hex() if 'tx_hash' in locals() else 'Not sent'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['approve_failed'].format(token=token_address)}: {str(e)} │ Tx: {EXPLORER_URL}{tx_hash.hex() if 'tx_hash' in locals() else 'Not sent'}{Style.RESET_ALL}")
            return False

async def find_existing_position(w3: Web3, address: str, token0: str, token1: str, fee: int, language: str = 'en') -> dict:
    position_manager = w3.eth.contract(address=CONTRACT_ADDRESSES["positionManager"], abi=POSITION_MANAGER_ABI)
    try:
        balance = position_manager.functions.balanceOf(address).call()
        if balance == 0:
            return None
        
        token0_lower = token0.lower()
        token1_lower = token1.lower()
        
        for i in range(balance):
            try:
                token_id = position_manager.functions.tokenOfOwnerByIndex(address, i).call()
                position = position_manager.functions.positions(token_id).call()
                
                pos_token0 = position[2].lower()
                pos_token1 = position[3].lower()
                pos_fee = position[4]
                
                if (
                    ((pos_token0 == token0_lower and pos_token1 == token1_lower) or
                     (pos_token0 == token1_lower and pos_token1 == token0_lower)) and
                    pos_fee == fee
                ):
                    print(f"{Fore.YELLOW}  ℹ {LANG[language]['existing_position'].format(tokenId=token_id)}{Style.RESET_ALL}")
                    return {
                        "tokenId": token_id,
                        "token0": position[2],
                        "token1": position[3],
                        "tickLower": position[5],
                        "tickUpper": position[6],
                    }
            except Exception as e:
                print(f"{Fore.YELLOW}  ⚠ Error checking position {i}: {str(e)}{Style.RESET_ALL}")
                continue
        return None
    except Exception as e:
        print(f"{Fore.RED}  ✖ Error finding existing positions: {str(e)}{Style.RESET_ALL}")
        return None

async def add_liquidity(w3: Web3, private_key: str, wallet_index: int, token0_name: str, token1_name: str, amount0: float, amount1: float, times: int, language: str = 'en', proxy: str = None):
    account = Account.from_key(private_key)
    address = account.address
    position_manager = w3.eth.contract(address=CONTRACT_ADDRESSES["positionManager"], abi=POSITION_MANAGER_ABI)
    successful_actions = 0
    nonce = w3.eth.get_transaction_count(address, 'pending')
    
    token0_addr = TOKEN_ADDRESSES[token0_name]["address"]
    token1_addr = TOKEN_ADDRESSES[token1_name]["address"]
    decimals0 = TOKEN_ADDRESSES[token0_name]["decimals"]
    decimals1 = TOKEN_ADDRESSES[token1_name]["decimals"]
    
    # Ensure token0 < token1
    swapped = False
    if token0_addr.lower() > token1_addr.lower():
        token0_addr, token1_addr = token1_addr, token0_addr
        amount0, amount1 = amount1, amount0
        token0_name, token1_name = token1_name, token0_name
        decimals0, decimals1 = decimals1, decimals0
        swapped = True
    
    amount0_desired = int(amount0 * 10 ** decimals0)
    amount1_desired = int(amount1 * 10 ** decimals1)
    
    for i in range(times):
        print_border(f"Liquidity Addition {i+1}/{times}: {token0_name} | {token1_name}", Fore.YELLOW)
        print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
        
        public_ip = await get_proxy_ip(proxy, language)
        proxy_display = proxy if proxy else LANG[language]['no_proxy']
        print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")
        
        phrs_balance = float(w3.from_wei(w3.eth.get_balance(address), 'ether'))
        if phrs_balance < CONFIG['MINIMUM_BALANCE']:
            print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=phrs_balance, symbol='PHRS', required=CONFIG['MINIMUM_BALANCE'])}{Style.RESET_ALL}")
            break
        
        token0_balance = check_balance(w3, address, token0_addr, decimals0, language)
        token1_balance = check_balance(w3, address, token1_addr, decimals1, language)
        if token0_balance < amount0:
            print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=token0_balance, symbol=token0_name, required=amount0)}{Style.RESET_ALL}")
            break
        if token1_balance < amount1:
            print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=token1_balance, symbol=token1_name, required=amount1)}{Style.RESET_ALL}")
            break
        
        print(f"{Fore.CYAN}  > {LANG[language]['preparing_liquidity']}{Style.RESET_ALL}")
        deadline = int(time.time()) + 20 * 60
        gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))
        
        # Approve tokens
        token0_contract = w3.eth.contract(address=token0_addr, abi=ERC20_ABI)
        token1_contract = w3.eth.contract(address=token1_addr, abi=ERC20_ABI)
        
        allowance0 = token0_contract.functions.allowance(address, CONTRACT_ADDRESSES["positionManager"]).call()
        if allowance0 < amount0_desired:
            if not await approve_token(w3, private_key, token0_addr, CONTRACT_ADDRESSES["positionManager"], amount0_desired, language, nonce, proxy):
                break
            nonce += 1
        
        allowance1 = token1_contract.functions.allowance(address, CONTRACT_ADDRESSES["positionManager"]).call()
        if allowance1 < amount1_desired:
            if not await approve_token(w3, private_key, token1_addr, CONTRACT_ADDRESSES["positionManager"], amount1_desired, language, nonce, proxy):
                break
            nonce += 1
        
        for attempt in range(CONFIG['MAX_RETRIES']):
            try:
                existing_position = await find_existing_position(w3, address, token0_addr, token1_addr, FEE_TIERS["LOW"], language)
                
                if existing_position:
                    print(f"{Fore.YELLOW}  ℹ {LANG[language]['existing_position'].format(tokenId=existing_position['tokenId'])}{Style.RESET_ALL}")
                    params = {
                        "tokenId": existing_position["tokenId"],
                        "amount0Desired": amount0_desired,
                        "amount1Desired": amount1_desired,
                        "amount0Min": 0,
                        "amount1Min": 0,
                        "deadline": deadline,
                    }
                    tx_func = position_manager.functions.increaseLiquidity(params)
                    gas_limit = 400000
                else:
                    print(f"{Fore.YELLOW}  ℹ {LANG[language]['new_position'].format(token0=token0_name, token1=token1_name)}{Style.RESET_ALL}")
                    params = {
                        "token0": token0_addr,
                        "token1": token1_addr,
                        "fee": FEE_TIERS["LOW"],
                        "tickLower": -887270,
                        "tickUpper": 887270,
                        "amount0Desired": amount0_desired,
                        "amount1Desired": amount1_desired,
                        "amount0Min": 0,
                        "amount1Min": 0,
                        "recipient": address,
                        "deadline": deadline,
                    }
                    tx_func = position_manager.functions.mint(params)
                    gas_limit = CONFIG['DEFAULT_GAS']
                
                tx_params = tx_func.build_transaction({
                    'nonce': nonce,
                    'from': address,
                    'chainId': CHAIN_ID,
                    'gasPrice': gas_price,
                    'gas': gas_limit,
                })
                
                try:
                    estimated_gas = w3.eth.estimate_gas(tx_params)
                    tx_params['gas'] = int(estimated_gas * 1.2)
                    print(f"{Fore.YELLOW}    Gas estimated: {tx_params['gas']}{Style.RESET_ALL}")
                except Exception as e:
                    tx_params['gas'] = gas_limit
                    print(f"{Fore.YELLOW}    {LANG[language]['gas_estimation_failed']}: {str(e)}. {LANG[language]['default_gas_used'].format(gas=gas_limit)}{Style.RESET_ALL}")
                
                print(f"{Fore.CYAN}  > {LANG[language]['sending_liquidity']}{Style.RESET_ALL}")
                signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
                
                receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=MAX_WAIT_TIME))
                
                if receipt.status == 1:
                    successful_actions += 1
                    phrs_balance_after = float(w3.from_wei(w3.eth.get_balance(address), 'ether'))
                    token0_balance_after = check_balance(w3, address, token0_addr, decimals0, language)
                    token1_balance_after = check_balance(w3, address, token1_addr, decimals1, language)
                    print(f"{Fore.GREEN}  ✔ {LANG[language]['success'].format(token0=token0_name, token1=token1_name)} │ Tx: {tx_link}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['address']:<12}: {address}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['block']:<12}: {receipt['blockNumber']}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['gas']:<12}: {receipt['gasUsed']}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['balance']:<12}: {phrs_balance_after:.6f} PHRS | {token0_name:<8}: {token0_balance_after:.6f} | {token1_name:<8}: {token1_balance_after:.6f}{Style.RESET_ALL}")
                    nonce += 1
                    break
                else:
                    print(f"{Fore.RED}  ✖ {LANG[language]['failure']} │ Tx: {tx_link}{Style.RESET_ALL}")
                    print(f"{Fore.RED}    {LANG[language]['tx_rejected']}{Style.RESET_ALL}")
                    break
                
            except Exception as e:
                if attempt < CONFIG['MAX_RETRIES'] - 1:
                    delay = random.uniform(5, 15)
                    print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
                    continue
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}{Style.RESET_ALL}")
                break
        
        if i < times - 1:
            delay = random.uniform(CONFIG['PAUSE_BETWEEN_ACTIONS'][0], CONFIG['PAUSE_BETWEEN_ACTIONS'][1])
            print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
    
    return successful_actions

async def run_liquidity(language: str = 'en'):
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

    total_actions = 0
    successful_actions = 0

    token_list = ["PHRS", "USDC", "USDT"]
    liquidity_pairs = [
        {"token0": "USDC", "token1": "USDT"},
        {"token0": "PHRS", "token1": "USDC"},
        {"token0": "PHRS", "token1": "USDT"},
    ]

    print(f"{Fore.CYAN}{LANG[language]['select_pair']}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  Available Pairs{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  --------------{Style.RESET_ALL}")
    for idx, pair in enumerate(liquidity_pairs, 1):
        print(f"{Fore.YELLOW}  {idx}. {pair['token0']} | {pair['token1']}{Style.RESET_ALL}")

    print()
    while True:
        print(f"{Fore.CYAN}Select liquidity pair [1-{len(liquidity_pairs)}]:{Style.RESET_ALL}")
        try:
            pair_choice = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if 1 <= pair_choice <= len(liquidity_pairs):
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")

    selected_pair = liquidity_pairs[pair_choice - 1]
    token0_name = selected_pair["token0"]
    token1_name = selected_pair["token1"]

    min_balance0 = float('inf')
    min_balance1 = float('inf')
    for _, key in private_keys:
        account = Account.from_key(key)
        balance0 = check_balance(w3, account.address, TOKEN_ADDRESSES[token0_name]["address"] if token0_name != "PHRS" else "native", TOKEN_ADDRESSES[token0_name]["decimals"] if token0_name != "PHRS" else 18, language)
        balance1 = check_balance(w3, account.address, TOKEN_ADDRESSES[token1_name]["address"] if token1_name != "PHRS" else "native", TOKEN_ADDRESSES[token1_name]["decimals"] if token1_name != "PHRS" else 18, language)
        min_balance0 = min(min_balance0, balance0)
        min_balance1 = min(min_balance1, balance1)

    print()
    while True:
        print(f"{Fore.CYAN}{LANG[language]['amount_prompt'].format(token=token0_name)} {Fore.YELLOW}(Max: {min_balance0:.4f} {token0_name}){Style.RESET_ALL}")
        try:
            amount0 = float(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if amount0 > 0 and amount0 <= min_balance0:
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_amount']} or exceeds balance{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_amount']}{Style.RESET_ALL}")

    print()
    while True:
        print(f"{Fore.CYAN}{LANG[language]['amount_prompt'].format(token=token1_name)} {Fore.YELLOW}(Max: {min_balance1:.4f} {token1_name}){Style.RESET_ALL}")
        try:
            amount1 = float(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if amount1 > 0 and amount1 <= min_balance1:
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_amount']} or exceeds balance{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_amount']}{Style.RESET_ALL}")

    print()
    while True:
        print(f"{Fore.CYAN}{LANG[language]['times_prompt']}:{Style.RESET_ALL}")
        try:
            times = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if times > 0:
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_times']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_times']}{Style.RESET_ALL}")

    print_separator()
    random.shuffle(private_keys)
    print_wallets_summary(len(private_keys), language)

    async def process_wallet(index, profile_num, private_key):
        nonlocal successful_actions, total_actions
        proxy = proxies[index % len(proxies)] if proxies else None
        
        async with semaphore:
            actions = await add_liquidity(w3, private_key, profile_num, token0_name, token1_name, amount0, amount1, times, language, proxy)
            successful_actions += actions
            total_actions += times
            if index < len(private_keys) - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                print_message(f"  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)

    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    tasks = [process_wallet(i, profile_num, key) for i, (profile_num, key) in enumerate(private_keys)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_actions, total=total_actions)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_liquidity('en'))
