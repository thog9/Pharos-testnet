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
NETWORK_URL = "https://testnet.dplabs-internal.com"
CHAIN_ID = 688688
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

# Task names
TASK_NAMES = {
    201: "Follow on X",
    202: "Retweet on X",
    203: "Comment on X",
    204: "Join Discord",
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
        'title': 'NHIỆM VỤ XÃ HỘI - PHAROS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ: {balance:.6f} PHRS (cần ít nhất {required:.6f})',
        'logging_in': 'Đang đăng nhập...',
        'login_success': '✅ Đăng nhập thành công, nhận được JWT',
        'login_failure': '❌ Đăng nhập thất bại: {error}',
        'verifying_task': '⚙ Xác minh nhiệm vụ: {task_name} cho {count} ví',
        'task_success': '✅ Nhiệm vụ {task_name} xác minh thành công cho ví {address}',
        'task_failure': '❌ Xác minh nhiệm vụ {task_name} thất bại cho ví {address}: {error}',
        'fetching_tasks': 'Đang lấy danh sách nhiệm vụ...',
        'tasks_fetched': '✅ Lấy danh sách nhiệm vụ thành công: {count} nhiệm vụ',
        'tasks_fetch_failed': '❌ Lấy danh sách nhiệm vụ thất bại: {error}',
        'address': 'Địa chỉ ví',
        'balance': 'Số dư',
        'balance_info': 'Số dư ví',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} NHIỆM VỤ THÀNH CÔNG',
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
        'jwt_missing': '❌ Thiếu JWT token',
        'select_task': 'Chọn nhiệm vụ để xác minh',
        'invalid_choice': 'Lựa chọn không hợp lệ, vui lòng chọn từ danh sách',
    },
    'en': {
        'title': 'SOCIAL TASKS - PHAROS TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance: {balance:.6f} PHRS (need at least {required:.6f})',
        'logging_in': 'Logging in...',
        'login_success': '✅ Login successful, obtained JWT',
        'login_failure': '❌ Login failed: {error}',
        'verifying_task': '⚙ Verifying task: {task_name} for {count} wallets',
        'task_success': '✅ Task {task_name} verified successfully for wallet {address}',
        'task_failure': '❌ Task {task_name} verification failed for wallet {address}: {error}',
        'fetching_tasks': 'Fetching user tasks...',
        'tasks_fetched': '✅ Successfully fetched tasks: {count} tasks',
        'tasks_fetch_failed': '❌ Failed to fetch user tasks: {error}',
        'address': 'Wallet address',
        'balance': 'Balance',
        'balance_info': 'Wallet Balances',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} TASKS SUCCESSFUL',
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
        'jwt_missing': '❌ JWT token missing',
        'select_task': 'Select task to verify',
        'invalid_choice': 'Invalid choice, please select from the list',
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
    print(f"{Fore.CYAN}  Wallet | {'PHRS':<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * 6} | {'-' * 10}{Style.RESET_ALL}")

    for i, (profile_num, key) in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        phrs_balance = check_balance(w3, address, "native", 18, language)
        print(f"{Fore.YELLOW}  {i:<6} | {phrs_balance:>10.6f}{Style.RESET_ALL}")
    
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

class AuthService:
    def __init__(self, private_key: str, wallet_index: int, language: str = 'en'):
        self.account = Account.from_key(private_key)
        self.wallet_index = wallet_index
        self.language = language
        self.base_url = API_BASE_URL
        self.jwt = None

    async def login(self, w3: Web3, proxy: str = None) -> dict:
        print(f"{Fore.CYAN}  > {LANG[self.language]['logging_in']}{Style.RESET_ALL}")
        address = self.account.address
        message = "pharos"
        invite_code = "yiOCVzHm9Zx4Ff3C"

        # Sign message
        message_hash = encode_defunct(text=message)
        signed_message = w3.eth.account.sign_message(message_hash, private_key=self.account.key)
        signature = signed_message.signature.hex()

        login_url = f"{self.base_url}/user/login?address={address}&signature={signature}&invite_code={invite_code}"
        headers = {**HEADERS, "Authorization": "Bearer null"}

        for attempt in range(CONFIG['RETRY_ATTEMPTS']):
            try:
                connector = ProxyConnector.from_url(proxy) if proxy and proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')) else None
                async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=30)) as session:
                    async with session.post(login_url, headers=headers, json=None, ssl=not CONFIG['BYPASS_SSL']) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("code") == 0:
                                self.jwt = data["data"]["jwt"]
                                profile_url = f"{self.base_url}/user/profile?address={address}"
                                async with session.get(profile_url, headers={**HEADERS, "Authorization": f"Bearer {self.jwt}"}, ssl=not CONFIG['BYPASS_SSL']) as profile_response:
                                    if profile_response.status == 200:
                                        profile_data = await profile_response.json()
                                        user_info = profile_data.get("data", {}).get("user_info", {})
                                        print(f"{Fore.GREEN}  ✔ {LANG[self.language]['login_success']}{Style.RESET_ALL}")
                                        return {"jwt": self.jwt, "user_info": user_info}
                                    else:
                                        error_msg = f"Profile fetch failed: HTTP {profile_response.status}"
                                        print(f"{Fore.RED}  ✖ {LANG[self.language]['login_failure'].format(error=error_msg)}{Style.RESET_ALL}")
                                        return {}
                            else:
                                error_msg = data.get("msg", "Unknown error")
                                print(f"{Fore.RED}  ✖ {LANG[self.language]['login_failure'].format(error=f'Code {data["code"]}: {error_msg}')}{Style.RESET_ALL}")
                                return {}
                        else:
                            print(f"{Fore.RED}  ✖ {LANG[self.language]['login_failure'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
            except ssl.SSLCertVerificationError as e:
                if CONFIG['BYPASS_SSL']:
                    print(f"{Fore.YELLOW}  ⚠ SSL verification bypassed due to configuration{Style.RESET_ALL}")
                else:
                    if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                        delay = CONFIG['RETRY_DELAY']
                        print(f"{Fore.RED}  ✖ {LANG[self.language]['login_failure'].format(error=str(e))}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    {LANG[self.language]['pausing']} {delay:.2f} {LANG[self.language]['seconds']}{Style.RESET_ALL}")
                        await asyncio.sleep(delay)
                        continue
                    print(f"{Fore.RED}  ✖ {LANG[self.language]['login_failure'].format(error=str(e))}{Style.RESET_ALL}")
                    return {}
            except Exception as e:
                if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                    delay = CONFIG['RETRY_DELAY']
                    print(f"{Fore.RED}  ✖ {LANG[self.language]['login_failure'].format(error=str(e))}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[self.language]['pausing']} {delay:.2f} {LANG[self.language]['seconds']}{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
                    continue
                print(f"{Fore.RED}  ✖ {LANG[self.language]['login_failure'].format(error=str(e))}{Style.RESET_ALL}")
                return {}
        
        return {}

    def get_jwt(self) -> str:
        return self.jwt

class SocialService:
    def __init__(self, wallet_index: int, language: str = 'en'):
        self.wallet_index = wallet_index
        self.language = language
        self.base_url = API_BASE_URL
        self.jwt = None

    def set_jwt(self, jwt: str):
        self.jwt = jwt

    async def verify_task(self, address: str, task_id: int, proxy: str = None, wallet_count: int = 1) -> bool:
        task_name = TASK_NAMES.get(task_id, f"Task {task_id}")
        print_border(
            LANG[self.language]['verifying_task'].format(task_name=task_name, count=wallet_count),
            Fore.CYAN
        )
        public_ip = await get_proxy_ip(proxy, self.language)
        proxy_display = proxy if proxy else LANG[self.language]['no_proxy']
        print(f"{Fore.CYAN}  🔄 {LANG[self.language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

        if not self.jwt:
            print(f"{Fore.RED}  ✖ {LANG[self.language]['jwt_missing']}{Style.RESET_ALL}")
            return False

        verify_url = f"{self.base_url}/task/verify?address={address}&task_id={task_id}"
        headers = {**HEADERS, "Authorization": f"Bearer {self.jwt}"}

        for attempt in range(CONFIG['RETRY_ATTEMPTS']):
            try:
                connector = ProxyConnector.from_url(proxy) if proxy and proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')) else None
                async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=30)) as session:
                    async with session.post(verify_url, headers=headers, json=None, ssl=not CONFIG['BYPASS_SSL']) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("code") == 0 and data.get("data", {}).get("verified"):
                                print(f"{Fore.GREEN}  ✔ {LANG[self.language]['task_success'].format(task_name=task_name, address=address[:6] + '...' + address[-4:])}{Style.RESET_ALL}")
                                return True
                            else:
                                error_msg = data.get("msg", "Unknown error")
                                print(f"{Fore.RED}  ✖ {LANG[self.language]['task_failure'].format(task_name=task_name, address=address[:6] + '...' + address[-4:], error=error_msg)}{Style.RESET_ALL}")
                                return False
                        else:
                            print(f"{Fore.RED}  ✖ {LANG[self.language]['task_failure'].format(task_name=task_name, address=address[:6] + '...' + address[-4:], error=f'HTTP {response.status}')}{Style.RESET_ALL}")
            except ssl.SSLCertVerificationError as e:
                if CONFIG['BYPASS_SSL']:
                    print(f"{Fore.YELLOW}  ⚠ SSL verification bypassed due to configuration{Style.RESET_ALL}")
                else:
                    if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                        delay = CONFIG['RETRY_DELAY']
                        print(f"{Fore.RED}  ✖ {LANG[self.language]['task_failure'].format(task_name=task_name, address=address[:6] + '...' + address[-4:], error=str(e))}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    {LANG[self.language]['pausing']} {delay:.2f} {LANG[self.language]['seconds']}{Style.RESET_ALL}")
                        await asyncio.sleep(delay)
                        continue
                    print(f"{Fore.RED}  ✖ {LANG[self.language]['task_failure'].format(task_name=task_name, address=address[:6] + '...' + address[-4:], error=str(e))}{Style.RESET_ALL}")
                    return False
            except Exception as e:
                if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                    delay = CONFIG['RETRY_DELAY']
                    print(f"{Fore.RED}  ✖ {LANG[self.language]['task_failure'].format(task_name=task_name, address=address[:6] + '...' + address[-4:], error=str(e))}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[self.language]['pausing']} {delay:.2f} {LANG[self.language]['seconds']}{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
                    continue
                print(f"{Fore.RED}  ✖ {LANG[self.language]['task_failure'].format(task_name=task_name, address=address[:6] + '...' + address[-4:], error=str(e))}{Style.RESET_ALL}")
                return False
        
        return False

async def run_social(language: str = 'en'):
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

    total_tasks = 0
    successful_tasks = 0

    print(f"{Fore.CYAN}{LANG[language]['select_task']}{Style.RESET_ALL}")
    task_list = [
        (201, "Follow on X"),
        (202, "Retweet on X"),
        (203, "Comment on X"),
        (204, "Join Discord"),
        (0, "Verify All Social Tasks"),
    ]
    for idx, (task_id, task_name) in enumerate(task_list, 1):
        print(f"{Fore.YELLOW}  {idx}. {task_name} {'[ID: ' + str(task_id) + ']' if task_id != 0 else ''}{Style.RESET_ALL}")

    print()
    while True:
        print(f"{Fore.CYAN}Select task to verify [1-{len(task_list)}]:{Style.RESET_ALL}")
        try:
            task_choice = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if 1 <= task_choice <= len(task_list):
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")

    selected_task_id, selected_task_name = task_list[task_choice - 1]
    task_ids = [201, 202, 203, 204] if selected_task_id == 0 else [selected_task_id]

    random.shuffle(private_keys)
    print_wallets_summary(len(private_keys), language)

    async def process_wallet(index, profile_num, private_key):
        nonlocal successful_tasks, total_tasks
        proxy = proxies[index % len(proxies)] if proxies else None
        address = Account.from_key(private_key).address

        async with semaphore:
            # Initialize AuthService
            auth_service = AuthService(private_key, profile_num, language)
            login_result = await auth_service.login(w3, proxy)
            if not login_result.get("jwt"):
                print(f"{Fore.RED}  ✖ Skipping tasks for wallet {profile_num} due to login failure{Style.RESET_ALL}")
                total_tasks += len(task_ids)
                return

            # Initialize SocialService
            social_service = SocialService(profile_num, language)
            social_service.set_jwt(login_result["jwt"])

            # Check balance
            print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
            phrs_balance = check_balance(w3, address, "native", 18, language)
            if phrs_balance < CONFIG['MINIMUM_BALANCE']:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=phrs_balance, required=CONFIG['MINIMUM_BALANCE'])}{Style.RESET_ALL}")
                total_tasks += len(task_ids)
                return

            # Verify tasks
            for task_id in task_ids:
                success = await social_service.verify_task(address, task_id, proxy, len(private_keys))
                total_tasks += 1
                if success:
                    successful_tasks += 1

            if index < len(private_keys) - 1:
                delay = CONFIG['DELAY_BETWEEN_ACCOUNTS']
                print_message(f"  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)

    semaphore = asyncio.Semaphore(CONFIG['THREADS'])
    tasks = [process_wallet(i, profile_num, key) for i, (profile_num, key) in enumerate(private_keys)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_tasks, total=total_tasks)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_social('en'))
