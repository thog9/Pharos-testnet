import os
import sys
import asyncio
import random
import time
import ssl
from typing import List, Tuple
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector

# Initialize colorama
init(autoreset=True)

# Border width
BORDER_WIDTH = 80

# Constants
NETWORK_URL = "https://atlantic.dplabs-internal.com"
CHAIN_ID = 688689
EXPLORER_URL = "https://atlantic.pharosscan.xyz/tx/0x"
API_BASE_URL = "https://api.pharosnetwork.xyz"
IP_CHECK_URL = "https://api.ipify.org?format=json"
MAX_WAIT_TIME = 180  # Timeout 3 minutes
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Origin": "https://testnet.pharosnetwork.xyz",
    "Referer": "https://testnet.pharosnetwork.xyz/",
}

# Configuration
CONFIG = {
    "DELAY_BETWEEN_ACCOUNTS": 5,  # Seconds
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 3,  # Seconds
    "THREADS": 2,
    "MINIMUM_BALANCE": 0.0001,  # PHRS
    "BYPASS_SSL": True,  # Temporary workaround for SSL issues
}

# Token definitions with checksummed addresses
TOKEN_ADDRESSES = {
    "PHRS": {"address": "native", "decimals": 18},
    "CASH+": {"address": Web3.to_checksum_address("0x56f4add11d723412d27a9e9433315401b351d6e3"), "decimals": 18},
    "USDT": {"address": Web3.to_checksum_address("0xe7e84b8b4f39c507499c40b4ac199b050e2882d5"), "decimals": 6},
}

# ERC20 ABI
ERC20_ABI = [
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
        'title': 'CHECK-IN HÀNG NGÀY - PHAROS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ: {balance:.6f} {symbol} (cần ít nhất {required:.6f})',
        'logging_in': 'Đang đăng nhập...',
        'login_success': '✅ Đăng nhập thành công, nhận được JWT',
        'login_failure': '❌ Đăng nhập thất bại: {error}',
        'performing_checkin': 'Đang thực hiện check-in...',
        'success': '✅ Check-in thành công cho ví {address}',
        'failure': '❌ Check-in thất bại: {error}',
        'address': 'Địa chỉ ví',
        'balance': 'Số dư',
        'balance_info': 'Số dư ví',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} CHECK-IN THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': '✅ Thành công: Đã kết nối với mạng Pharos Testnet',
        'connect_error': '❌ Không thể kết nối với RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ Không tìm thấy tệp pvkey.txt',
        'pvkey_empty': '❌ Không tìm thấy khóa riêng hợp lệ',
        'pvkey_error': '❌ Không thể đọc pvkey.txt',
        'invalid_key': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
    },
    'en': {
        'title': 'DAILY CHECK-IN - PHAROS TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance: {balance:.6f} {symbol} (need at least {required:.6f})',
        'logging_in': 'Logging in...',
        'login_success': '✅ Login successful, obtained JWT',
        'login_failure': '❌ Login failed: {error}',
        'performing_checkin': 'Performing check-in...',
        'success': '✅ Check-in successful for wallet {address}',
        'failure': '❌ Check-in failed: {error}',
        'address': 'Wallet address',
        'balance': 'Balance',
        'balance_info': 'Wallet Balances',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} CHECK-INS SUCCESSFUL',
        'error': 'Error',
        'connect_success': '✅ Success: Connected to Pharos Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
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
    print(f"{Fore.CYAN}  Wallet | {'PHRS':<10} | {'CASH+':<10} | {'USDT':<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * 6} | {'-' * 10} | {'-' * 10} | {'-' * 10}{Style.RESET_ALL}")

    for i, (profile_num, key) in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        phrs_balance = check_balance(w3, address, "native", 18, language)
        usdc_balance = check_balance(w3, address, TOKEN_ADDRESSES["USDC"]["address"], TOKEN_ADDRESSES["USDC"]["decimals"], language)
        usdt_balance = check_balance(w3, address, TOKEN_ADDRESSES["USDT"]["address"], TOKEN_ADDRESSES["USDT"]["decimals"], language)
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

async def login(w3: Web3, private_key: str, wallet_index: int, language: str = 'en', proxy: str = None) -> str:
    print(f"{Fore.CYAN}  > {LANG[language]['logging_in']}{Style.RESET_ALL}")
    address = Account.from_key(private_key).address
    message = "pharos"
    invite_code = "yiOCVzHm9Zx4Ff3C"  

    # Sign message
    message_hash = encode_defunct(text=message)
    signed_message = w3.eth.account.sign_message(message_hash, private_key=private_key)
    signature = signed_message.signature.hex()

    login_url = f"{API_BASE_URL}/user/login?address={address}&signature={signature}&invite_code={invite_code}"
    login_headers = {**HEADERS, "Authorization": "Bearer null"}

    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy and proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')) else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(login_url, headers=login_headers, json=None, ssl=not CONFIG['BYPASS_SSL']) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 0:
                            jwt = data["data"]["jwt"]
                            # Get user profile
                            profile_url = f"{API_BASE_URL}/user/profile?address={address}"
                            async with session.get(profile_url, headers={**HEADERS, "Authorization": f"Bearer {jwt}"}, ssl=not CONFIG['BYPASS_SSL']) as profile_response:
                                if profile_response.status == 200:
                                    print(f"{Fore.GREEN}  ✔ {LANG[language]['login_success']}{Style.RESET_ALL}")
                                    return jwt
                                else:
                                    error_msg = f"Profile fetch failed: HTTP {profile_response.status}"
                                    print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error=error_msg)}{Style.RESET_ALL}")
                                    return ""
                        else:
                            error_msg = data.get("msg", "Unknown error")
                            print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error=f'Code {data["code"]}: {error_msg}')}{Style.RESET_ALL}")
                            return ""
                    else:
                        print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
        except ssl.SSLCertVerificationError as e:
            if CONFIG['BYPASS_SSL']:
                print(f"{Fore.YELLOW}  ⚠ SSL verification bypassed due to configuration{Style.RESET_ALL}")
            else:
                if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                    delay = CONFIG['RETRY_DELAY']
                    print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error=str(e))}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
                    continue
                print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error=str(e))}{Style.RESET_ALL}")
                return ""
        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                delay = CONFIG['RETRY_DELAY']
                print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error=str(e))}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error=str(e))}{Style.RESET_ALL}")
            return ""
    
    return ""

async def daily_checkin(w3: Web3, address: str, jwt: str, wallet_index: int, language: str = 'en', proxy: str = None) -> bool:
    print_border(f"Check-in for Wallet {wallet_index}: {address[:6]}...{address[-4:]}", Fore.YELLOW)
    print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")

    phrs_balance = check_balance(w3, address, "native", 18, language)
    if phrs_balance < CONFIG['MINIMUM_BALANCE']:
        print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=phrs_balance, symbol='PHRS', required=CONFIG['MINIMUM_BALANCE'])}{Style.RESET_ALL}")
        return False

    public_ip = await get_proxy_ip(proxy, language)
    proxy_display = proxy if proxy else LANG[language]['no_proxy']
    print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

    if not jwt:
        print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error='No JWT obtained')}{Style.RESET_ALL}")
        return False

    print(f"{Fore.CYAN}  > {LANG[language]['performing_checkin']}{Style.RESET_ALL}")
    checkin_url = f"{API_BASE_URL}/sign/in?address={address}"

    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy and proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')) else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    checkin_url,
                    headers={**HEADERS, "Authorization": f"Bearer {jwt}"},
                    json=None,
                    ssl=not CONFIG['BYPASS_SSL']
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 0:
                            print(f"{Fore.GREEN}  ✔ {LANG[language]['success'].format(address=address)}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}    {LANG[language]['address']:<12}: {address}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}    {LANG[language]['balance']:<12}: {phrs_balance:.6f} PHRS{Style.RESET_ALL}")
                            return True
                        else:
                            error_msg = data.get("msg", "Unknown error")
                            print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=error_msg)}{Style.RESET_ALL}")
                            return False
                    else:
                        print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
        except ssl.SSLCertVerificationError as e:
            if CONFIG['BYPASS_SSL']:
                print(f"{Fore.YELLOW}  ⚠ SSL verification bypassed due to configuration{Style.RESET_ALL}")
            else:
                if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                    delay = CONFIG['RETRY_DELAY']
                    print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
                    continue
                print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
                return False
        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                delay = CONFIG['RETRY_DELAY']
                print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
            return False
    
    return False

async def run_checkin(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    proxies = load_proxies('proxies.txt', language)
    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)  # Initialize Web3 connection once
    print()

    display_all_wallets_balances(w3, private_keys, language)
    print_separator()

    total_checkins = 0
    successful_checkins = 0

    print_separator()
    random.shuffle(private_keys)
    print_wallets_summary(len(private_keys), language)

    async def process_wallet(index, profile_num, private_key):
        nonlocal successful_checkins, total_checkins
        proxy = proxies[index % len(proxies)] if proxies else None
        address = Account.from_key(private_key).address
        
        async with semaphore:
            # Perform login to get JWT
            jwt = await login(w3, private_key, profile_num, language, proxy)  # Pass w3
            if not jwt:
                print(f"{Fore.RED}  ✖ Skipping check-in for wallet {profile_num} due to login failure{Style.RESET_ALL}")
                total_checkins += 1
                return

            # Perform check-in
            success = await daily_checkin(w3, address, jwt, profile_num, language, proxy)  # Pass w3
            total_checkins += 1
            if success:
                successful_checkins += 1
            if index < len(private_keys) - 1:
                delay = CONFIG['DELAY_BETWEEN_ACCOUNTS']
                print_message(f"  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)

    semaphore = asyncio.Semaphore(CONFIG['THREADS'])
    tasks = [process_wallet(i, profile_num, key) for i, (profile_num, key) in enumerate(private_keys)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_checkins, total=total_checkins)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_checkin('en'))
