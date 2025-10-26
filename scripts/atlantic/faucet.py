import os
import sys
import asyncio
import random
import time
from typing import List, Tuple
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import aiohttp
from aiohttp_socks import ProxyConnector
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Border width
BORDER_WIDTH = 80

# Constants
NETWORK_URL = "https://atlantic.dplabs-internal.com"
CHAIN_ID = 688689
FAUCET_URL = "https://api.pharosnetwork.xyz"
CLAIM_URL = f"{FAUCET_URL}/faucet/daily"
STATUS_URL = f"{FAUCET_URL}/faucet/status"
RECAPTCHA_SITE_KEY = "6Lfx1iwrAAAAAJp_suDVjStYCUs0keW8tQ722uZR"
API_BASE_URL = "https://api.2captcha.com"
IP_CHECK_URL = "https://api.ipify.org?format=json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "Origin": "https://testnet.pharosnetwork.xyz",
    "Referer": "https://testnet.pharosnetwork.xyz/",
    "Sec-Ch-Ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}

# Configuration
CONFIG = {
    "DELAY_BETWEEN_ACCOUNTS": 10,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 5,
    "THREADS": 1,
    "BYPASS_SSL": True,
    "TIMEOUT": 30,
    "MINIMUM_BALANCE": 0,  # PHRS
}

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'FAUCET PHAROS - NHẬN TOKEN TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ: {balance:.6f} {symbol} (cần ít nhất {required:.6f})',
        'logging_in': 'Đang đăng nhập...',
        'login_success': '✅ Đăng nhập thành công, nhận được JWT',
        'login_failure': '❌ Đăng nhập thất bại: {error}',
        'claiming_tokens': 'Đang nhận token...',
        'success': '✅ Nhận token thành công cho ví {address}',
        'failure': '❌ Nhận token thất bại: {error}',
        'address': 'Địa chỉ ví',
        'balance': 'Số dư',
        'balance_info': 'Số dư ví',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✅ HOÀN THÀNH: {successful}/{total} NHẬN TOKEN THÀNH CÔNG',
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
        'enter_api_key': 'Vui lòng nhập 2captcha API Key: ',
        'api_key_saved': '✅ API Key đã được lưu vào 2captchakey.txt',
        'invalid_api_key': '❌ API Key không hợp lệ hoặc trống',
        'confirm_start': 'Tìm thấy {count} ví, bạn có muốn bắt đầu nhận token không? (y/n): ',
        'user_cancelled': 'ℹ Người dùng đã hủy thao tác',
        'recaptcha_submitting': 'Đang gửi yêu cầu giải reCAPTCHA...',
        'recaptcha_success': '✅ Giải reCAPTCHA thành công',
        'recaptcha_waiting': 'Đang chờ giải reCAPTCHA... (lần thử {attempt}/{max_attempts})',
        'recaptcha_failed': '❌ Giải reCAPTCHA thất bại: {error}',
        'recaptcha_timeout': '❌ Giải reCAPTCHA hết thời gian',
        'faucet_status': 'Trạng thái faucet: Có thể nhận token: {status}, Thời gian khả dụng tiếp theo: {timestamp}',
        'rate_limit': '⚠ Đạt giới hạn yêu cầu (HTTP 429). Đang thử lại sau {delay} giây...',
        'found_wallets': 'Thông tin: Tìm thấy {count} ví',
        'faucet_status': 'Trạng thái faucet...',
        'address': 'Địa chỉ ví',
        'claiming_tokens': 'Nhận token:',
        'faucet_already_claimed': '❌ Ví này đã thực hiện faucet rồi! Vui lòng thực hiện lại sau...',
        'can_claim': 'Có thể nhận',
        'cannot_claim': 'Không thể nhận',
    },
    'en': {
        'title': 'PHAROS FAUCET - CLAIM TESTNET TOKENS',
        'info': 'Information',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance: {balance:.6f} {symbol} (need at least {required:.6f})',
        'logging_in': 'Logging in...',
        'login_success': '✅ Login successful, obtained JWT',
        'login_failure': '❌ Login failed: {error}',
        'claiming_tokens': 'Claiming tokens...',
        'success': '✅ Token claim successful for wallet {address}',
        'failure': '❌ Token claim failed: {error}',
        'address': 'Wallet address',
        'balance': 'Balance',
        'balance_info': 'Wallet Balances',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✅ COMPLETED: {successful}/{total} TOKEN CLAIMS SUCCESSFUL',
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
        'no_proxy': 'No proxy',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'enter_api_key': 'Please enter 2captcha API Key: ',
        'api_key_saved': '✅ API Key saved to 2captchakey.txt',
        'invalid_api_key': '❌ API Key is invalid or empty',
        'confirm_start': 'Found {count} wallets, would you like to start claiming tokens? (y/n): ',
        'user_cancelled': 'ℹ User cancelled operation',
        'recaptcha_submitting': 'Submitting reCAPTCHA solve request...',
        'recaptcha_success': '✅ reCAPTCHA solved successfully',
        'recaptcha_waiting': 'Waiting for reCAPTCHA solution... (attempt {attempt}/{max_attempts})',
        'recaptcha_failed': '❌ reCAPTCHA solving failed: {error}',
        'recaptcha_timeout': '❌ reCAPTCHA solving timed out',
        'faucet_status': 'Faucet status: Can claim: {status}, Next available time: {timestamp}',
        'rate_limit': '⚠ Rate limit reached (HTTP 429). Retrying after {delay} seconds...',
        'found_wallets': 'Info: Found {count} wallets',
        'faucet_status': 'Faucet status...',
        'address': 'Wallet address',
        'claiming_tokens': 'Claim tokens:',
        'faucet_already_claimed': '❌ This wallet has already claimed tokens! Please try again later...',
        'can_claim': 'Can claim',
        'cannot_claim': 'Cannot claim',
    }
}

# Display functions
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH, language: str = 'en'):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA, language: str = 'en'):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def print_message(message: str, color=Fore.YELLOW, language: str = 'en'):
    print(f"{color}  {message}{Style.RESET_ALL}")

def print_wallets_summary(count: int, language: str = 'en'):
    print_border(
        LANG[language]['processing_wallets'].format(count=count),
        Fore.MAGENTA, language=language
    )
    print()

def display_all_wallets_balances(w3: Web3, private_keys: List[Tuple[int, str]], language: str = 'en'):
    print_border(LANG[language]['balance_info'], Fore.CYAN, language=language)
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
    return -1

def load_api_key(language: str = 'en') -> str:
    try:
        if os.path.exists('2captchakey.txt'):
            with open('2captchakey.txt', 'r', encoding='utf-8') as f:
                api_key = f.read().strip()
                if api_key:
                    return api_key
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
    return ""

async def login(w3: Web3, private_key: str, wallet_index: int, language: str = 'en', proxy: str = None) -> str:
    print(f"{Fore.CYAN}  > {LANG[language]['logging_in']}{Style.RESET_ALL}")
    address = Account.from_key(private_key).address
    message = "pharos"
    invite_code = "yiOCVzHm9Zx4Ff3C"

    message_hash = encode_defunct(text=message)
    signed_message = w3.eth.account.sign_message(message_hash, private_key=private_key)
    signature = signed_message.signature.hex()

    login_urls = [
        f"{FAUCET_URL}/user/login",  
        f"{FAUCET_URL}/auth/login",  
        f"{FAUCET_URL}/login"
    ]
    payload = {
        "address": address,
        "signature": signature,
        "invite_code": invite_code
    }
    login_headers = {**HEADERS}

    for login_url in login_urls:
        for attempt in range(CONFIG['RETRY_ATTEMPTS']):
            try:
                connector = ProxyConnector.from_url(proxy) if proxy and proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')) else None
                async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                    async with session.post(login_url, headers=login_headers, json=payload, ssl=not CONFIG['BYPASS_SSL']) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("code") == 0:
                                jwt = data["data"]["jwt"]
                                profile_url = f"{FAUCET_URL}/user/profile?address={address}"
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
                            print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error=f'HTTP {response.status} at {login_url}')}{Style.RESET_ALL}")
            except Exception as e:
                if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                    delay = CONFIG['RETRY_DELAY']
                    print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error=str(e))}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
                    continue
                print(f"{Fore.RED}  ✖ {LANG[language]['login_failure'].format(error=f'{str(e)} at {login_url}')}{Style.RESET_ALL}")
    return ""

class TwoCaptchaSolver:
    def __init__(self, api_key: str, language: str = 'en'):
        self.api_key = api_key
        self.language = language

    async def solve_recaptcha(self, site_key: str, url: str, proxy: str = None) -> str:
        print_message(LANG[self.language]['recaptcha_submitting'], Fore.CYAN, self.language)
        
        task_data = {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": url,
            "websiteKey": site_key
        }
        
        if proxy:
            task_data["type"] = "RecaptchaV2Task"
            if proxy.startswith(('http://', 'https://', 'socks5://', 'socks4://')):
                proxy_parts = proxy.replace('http://', '').replace('https://', '').replace('socks5://', '').replace('socks4://', '')
                if '@' in proxy_parts:
                    auth_part, server_part = proxy_parts.split('@')
                    if ':' in auth_part:
                        proxy_login, proxy_password = auth_part.split(':', 1)
                    else:
                        proxy_login, proxy_password = None, None
                    if ':' in server_part:
                        proxy_address, proxy_port = server_part.split(':', 1)
                    else:
                        proxy_address, proxy_port = server_part, "8080"
                else:
                    proxy_login, proxy_password = None, None
                    if ':' in proxy_parts:
                        proxy_address, proxy_port = proxy_parts.split(':', 1)
                    else:
                        proxy_address, proxy_port = proxy_parts, "8080"
                
                task_data["proxyType"] = "http" if proxy.startswith(('http://', 'https://')) else "socks5"
                task_data["proxyAddress"] = proxy_address
                task_data["proxyPort"] = int(proxy_port)
                if proxy_login and proxy_password:
                    task_data["proxyLogin"] = proxy_login
                    task_data["proxyPassword"] = proxy_password
        
        post_url = f"{API_BASE_URL}/createTask"
        payload = {
            "clientKey": self.api_key,
            "task": task_data
        }
        
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                async with session.post(post_url, json=payload, ssl=not CONFIG['BYPASS_SSL']) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('errorId') == 0:
                            task_id = result.get('taskId')
                            if not task_id:
                                print(f"{Fore.RED}  ✖ {LANG[self.language]['recaptcha_failed'].format(error='No taskId received')}{Style.RESET_ALL}")
                                return ""
                        else:
                            error_desc = result.get('errorDescription', result.get('errorCode', 'Unknown error'))
                            print(f"{Fore.RED}  ✖ {LANG[self.language]['recaptcha_failed'].format(error=error_desc)}{Style.RESET_ALL}")
                            return ""
                    else:
                        response_text = await response.text()
                        print(f"{Fore.RED}  ✖ {LANG[self.language]['recaptcha_failed'].format(error=f'HTTP {response.status}: {response_text}')}{Style.RESET_ALL}")
                        return ""
        except Exception as e:
            print(f"{Fore.RED}  ✖ {LANG[self.language]['recaptcha_failed'].format(error=str(e))}{Style.RESET_ALL}")
            return ""

        get_url = f"{API_BASE_URL}/getTaskResult"
        for attempt in range(30):
            await asyncio.sleep(5)  
            
            params = {
                'clientKey': self.api_key,
                'taskId': task_id
            }
            
            try:
                connector = ProxyConnector.from_url(proxy) if proxy else None
                async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                    async with session.post(get_url, json=params, ssl=not CONFIG['BYPASS_SSL']) as response:
                        if response.status == 200:
                            result = await response.json()
                            status = result.get('status')
                            
                            if status == "ready":
                                solution = result.get('solution', {}).get('gRecaptchaResponse', "")
                                if solution:
                                    print_message(LANG[self.language]['recaptcha_success'], Fore.GREEN, self.language)
                                    return solution
                                else:
                                    print(f"{Fore.RED}  ✖ {LANG[self.language]['recaptcha_failed'].format(error='Empty solution')}{Style.RESET_ALL}")
                                    return ""
                            elif status == "processing":
                                print_message(LANG[self.language]['recaptcha_waiting'].format(attempt=attempt + 1, max_attempts=30), Fore.YELLOW, self.language)
                            else:
                                error_desc = result.get('errorDescription', result.get('errorCode', 'Unknown status'))
                                print(f"{Fore.RED}  ✖ {LANG[self.language]['recaptcha_failed'].format(error=error_desc)}{Style.RESET_ALL}")
                                return ""
                        else:
                            print(f"{Fore.RED}  ✖ {LANG[self.language]['recaptcha_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                            return ""
            except Exception as e:
                print(f"{Fore.RED}  ✖ {LANG[self.language]['recaptcha_failed'].format(error=str(e))}{Style.RESET_ALL}")
                if attempt < 29:
                    continue
                return ""

        print(f"{Fore.RED}  ✖ {LANG[self.language]['recaptcha_timeout']}{Style.RESET_ALL}")
        return ""

async def check_faucet_status(address: str, jwt: str, proxy: str = None, language: str = 'en') -> bool:
    status_url = f"{STATUS_URL}?address={address}"
    headers = {**HEADERS, "Authorization": f"Bearer {jwt}"}
    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                async with session.get(status_url, headers=headers, ssl=not CONFIG['BYPASS_SSL']) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 0:
                            status = data["data"].get("is_able_to_faucet", False)
                            status_text = LANG[language]['can_claim'] if status else LANG[language]['cannot_claim']
                            print(f"{Fore.CYAN}  > {LANG[language]['faucet_status']}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}     - {LANG[language]['address']}: {address}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}     - {LANG[language]['claiming_tokens']} {status_text}{Style.RESET_ALL}")
                            if not status:
                                print(f"{Fore.RED}  ✖ {LANG[language]['faucet_already_claimed']}{Style.RESET_ALL}")
                            return status
                        else:
                            print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=data.get('msg', 'Unknown error'))}{Style.RESET_ALL}")
                            return False
                    elif response.status == 429:
                        delay = CONFIG['RETRY_DELAY'] * (attempt + 1) * 2
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['rate_limit'].format(delay=delay)}{Style.RESET_ALL}")
                        await asyncio.sleep(delay)
                        continue
                    print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return False
        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                delay = CONFIG['RETRY_DELAY']
                print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
            return False
    return False

async def claim_tokens(w3: Web3, private_key: str, index: int, jwt: str, proxy: str = None, language: str = 'en', two_captcha: TwoCaptchaSolver = None) -> bool:
    address = Account.from_key(private_key).address
    print_border(f"Claim Tokens for Wallet {index}: {address[:6]}...{address[-4:]}", Fore.YELLOW, language=language)

    print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
    phrs_balance = check_balance(w3, address, "native", 18, language)
    if phrs_balance < CONFIG['MINIMUM_BALANCE']:
        print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=phrs_balance, symbol='PHRS', required=CONFIG['MINIMUM_BALANCE'])}{Style.RESET_ALL}")
        return False

    public_ip = await get_proxy_ip(proxy, language)
    proxy_display = proxy if proxy else LANG[language]['no_proxy']
    print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

    can_claim = await check_faucet_status(address, jwt, proxy, language)
    if not can_claim:
        return False

    recaptcha_response = await two_captcha.solve_recaptcha(RECAPTCHA_SITE_KEY, "https://testnet.pharosnetwork.xyz", proxy)
    if not recaptcha_response:
        print(f"{Fore.RED}  ✖ {LANG[language]['recaptcha_failed'].format(error='No response')}{Style.RESET_ALL}")
        return False

    print(f"{Fore.CYAN}  > {LANG[language]['claiming_tokens']}{Style.RESET_ALL}")
    payload = {"address": address, "captcha": recaptcha_response}
    headers = {**HEADERS, "Authorization": f"Bearer {jwt}"}

    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                async with session.post(CLAIM_URL, json=payload, headers=headers, ssl=not CONFIG['BYPASS_SSL']) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 0:
                            print(f"{Fore.GREEN}  ✔ {LANG[language]['success'].format(address=address)}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}    {LANG[language]['address']}: {address}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}    {LANG[language]['balance']}: {phrs_balance:.6f} PHRS{Style.RESET_ALL}")
                            return True
                        else:
                            print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=data.get('msg', 'Unknown error'))}{Style.RESET_ALL}")
                            return False
                    elif response.status == 429:
                        delay = CONFIG['RETRY_DELAY'] * (attempt + 1) * 2
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['rate_limit'].format(delay=delay)}{Style.RESET_ALL}")
                        await asyncio.sleep(delay)
                        continue
                    print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return False
        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                delay = CONFIG['RETRY_DELAY']
                print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
            return False
    return False

async def run_faucet(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN, language=language)
    print()

    proxies = load_proxies(language=language)
    print()

    private_keys = load_private_keys(language=language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_wallets'].format(count=len(private_keys))}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    display_all_wallets_balances(w3, private_keys, language)
    print_separator(language=language)

    api_key = load_api_key(language)
    if not api_key:
        print(f"{Fore.YELLOW}  > {LANG[language]['enter_api_key']}{Style.RESET_ALL}", end='')
        api_key = input().strip()
        if not api_key:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_api_key']}{Style.RESET_ALL}")
            return
        with open('2captchakey.txt', 'w', encoding='utf-8') as f:
            f.write(api_key)
        print(f"{Fore.GREEN}  ✔ {LANG[language]['api_key_saved']}{Style.RESET_ALL}")

    print(f"{Fore.YELLOW}  > {LANG[language]['confirm_start'].format(count=len(private_keys))}{Style.RESET_ALL}", end='')
    confirm = input().strip().lower()
    if confirm not in ['y', 'yes']:
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['user_cancelled']}{Style.RESET_ALL}")
        return

    print_separator(language=language)
    random.shuffle(private_keys)
    print_wallets_summary(len(private_keys), language)

    total_claims = 0
    successful_claims = 0
    two_captcha = TwoCaptchaSolver(api_key, language)

    async def process_wallet(index, profile_num, private_key):
        nonlocal successful_claims, total_claims
        proxy = proxies[index % len(proxies)] if proxies else None
        
        async with semaphore:
            jwt = await login(w3, private_key, profile_num, language, proxy)
            if not jwt:
                print(f"{Fore.RED}  ✖ Skipping faucet claim for wallet {profile_num} due to login failure{Style.RESET_ALL}")
                total_claims += 1
                return

            success = await claim_tokens(w3, private_key, profile_num, jwt, proxy, language, two_captcha)
            total_claims += 1
            if success:
                successful_claims += 1
            if index < len(private_keys) - 1:
                print_message(f"{LANG[language]['pausing']} {CONFIG['DELAY_BETWEEN_ACCOUNTS']:.2f} {LANG[language]['seconds']}", Fore.YELLOW, language)
                await asyncio.sleep(CONFIG['DELAY_BETWEEN_ACCOUNTS'])

    semaphore = asyncio.Semaphore(CONFIG['THREADS'])
    tasks = [process_wallet(i, profile_num, key) for i, (profile_num, key) in enumerate(private_keys)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(
        LANG[language]['completed'].format(successful=successful_claims, total=total_claims),
        Fore.GREEN, language=language
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_faucet('vi'))
