import os
import sys
import asyncio
import random
import string
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector

# Khởi tạo colorama
init(autoreset=True)

# Constants
NETWORK_URL = "https://testnet.dplabs-internal.com"
CHAIN_ID = 688688
EXPLORER_URL = "https://testnet.pharosscan.xyz/tx/0x"
ROUTER = "0xd17512b7ec12880bd94eca9d774089ff89805f02"
IP_CHECK_URL = "https://api.ipify.org?format=json"
SYMBOL = "PHRS"
BORDER_WIDTH = 80
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, application/json",
    "Accept-Language": "en-US,en;q=0.1",
}
CONFIG = {
    "PAUSE_BETWEEN": [10, 20],
    "MAX_CONCURRENT": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.001
}

# Contract ABI
CONTRACT_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "uint32", "name": "tokenType", "type": "uint32"},
                    {"internalType": "address", "name": "tokenAddress", "type": "address"}
                ],
                "internalType": "struct TipToken",
                "name": "token",
                "type": "tuple"
            },
            {
                "components": [
                    {"internalType": "string", "name": "idSource", "type": "string"},
                    {"internalType": "string", "name": "id", "type": "string"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"internalType": "uint256[]", "name": "nftIds", "type": "uint256[]"}
                ],
                "internalType": "struct TipRecipientInfo",
                "name": "recipient",
                "type": "tuple"
            }
        ],
        "name": "tip",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

# Từ ngôn ngữ
LNG = {
    'vi': {
        'title': '✨ GỬI TIP - PHAROS TESTNET ✨',
        'info': 'ℹ Thông tin!',
        'found': 'Tìm thấy',
        'wallets': 'ví dụ',
        'processing': '⚠️ ĐANG XỬ LÝ {KEYS} VÍ',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt.txt!',
        'enter_tip_count': '✦ SỐ LẦN TIP',
        'tip_count': 'Nhập số lần TIP (mặc định 1): ',
        'selected': '✔ Đã chọn',
        'choice': ' TIP',
        'enter_amount': '✦ SỔ TIỀN PHAROS',
        'tip_amount': 'Số lượng PHRS (0.000001): ',
        'amount_unit': 'PHRS',
        'select_platform': '✦ CHỌN NỀN TẢNG GỬI TIP',
        'x_option': '1. X',
        'tiktok_option': '2. TikTok',
        'google_option': '3. Google Account',
        'select_tip_type': '✦ CHỌN LOẠI TIP',
        'random_option': '1. Gửi TIP ngẫu nhiên',
        'file_option': '2. Gửi TIP đến danh sách (username.txt)',
        'choice_prompt': 'Nhập lựa chọn (1/2): ',
        'start_random': '✨ BẮT ĐẦU GỬI {tip_count} TIP NGẪU NHIÊN',
        'start_file': '✨ GỬI TIP ĐẾN {user_count} TÀI KHOẢN Ở FILE',
        'processing_wallet': '⚠️ Đang xử lý ví',
        'balance_check': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ (cần {required:.6f} PHRS)',
        'tip': '💸 TIP',
        'to_user': 'Người nhận',
        'amount': 'Số lượng',
        'sending': 'Đang gửi TIP...',
        'success': '✅ TIP! Thành công!',
        'failure': '❌️ TIP thất bại!',
        'timeout': '�️ TIP không xác nhận sau {timeout} giây, kiểm tra trên explorer',
        'sender': 'Người gửi',
        'recipient': 'Người nhận',
        'amount': 'Số lượng',
        'gas': 'Gas',
        'block': 'Khối',
        'amount_txs': 'giao dịch',
        'balance': 'Số dư',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✔ HOÀN THÀNH! {txs_txs}/{tx_total} TIP thành công',
        'error': '✘ Lỗi',
        'invalid_number': 'Vui lòng nhập số hợp lệ!',
        'tip_count_error': 'Số TIP phải lớn hơn 0!',
        'amount_error': 'Số lượng phải lớn hơn 0.000001!',
        'invalid_choice': 'Lựa chọn không hợp lệ!',
        'connect_success': '✔ Thành công: Kết nối mạng Pharos Testnet',
        'connect_error': '✘ Không thể kết nối RPC',
        'web3_error': '✘ Kết nối Web3 thất bại',
        'pvkey_not_found': '✘ File pvkey.txt không tồn tại',
        'pvkey_empty': '✘ Không tìm thấy private key hợp lệ',
        'pvkey_error': '✘ Đọc pvkey.txt thất bại',
        'username_not_found': '✘ File username.txt không tồn tại',
        'username_empty': '✘ Không tìm thấy tài khoản hợp lệ trong username.txt',
        'username_error': '✘ Đọc username.txt thất bại',
        'invalid_username': 'không phải tài khoản hợp lệ, bỏ qua',
        'warning_line': '⚠️ Cảnh báo: Dòng',
        'using_proxy': '🔄 Dùng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không proxy',
        'unknown': 'Không rõ',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
    },
    'en': {
        'title': '✨ SEND TIP - PHAROS TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing': '⚠️ PROCESSING {KEYS} WALLETS',
        'found_proxies': 'Found {count} proxies in proxies.txt!',
        'enter_tip_count': '✦ NUMBER OF TIPS',
        'tip_count': 'Number of TIPs (default 1): ',
        'selected': '✔ Selected',
        'choice': ' TIPs',
        'enter_amount': '✦ AMOUNT OF PHRS',
        'tip_amount': 'Amount of PHRS (min 0.000001): ',
        'amount_unit': 'PHRS',
        'select_platform': '✦ SELECT TIP PLATFORM',
        'x_option': '1. X',
        'tiktok_option': '2. TikTok',
        'google_option': '3. Google Account',
        'select_tip_type': '✦ SELECT TIP TYPE',
        'random_option': '1. Send random TIPs',
        'file_option': '2. Send TIPs to list (username.txt)',
        'choice_prompt': 'Enter choice (1/2): ',
        'start_random': '✨ STARTING {tip_count} RANDOM TIPs',
        'start_file': '✨ SENDING TIPs TO {user_count} ACCOUNTS FROM FILE',
        'processing_wallet': '⚠️ Processing wallet',
        'balance_check': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance (need at least {required:.6f} PHRS)',
        'tip': '💸 TIP',
        'to_user': 'Recipient',
        'amount': 'Amount',
        'sending': 'Sending TIP...',
        'success': '✅ TIP Successful!',
        'failure': '❌ TIP Failed!',
        'timeout': '⏰ TIP not confirmed after {timeout} seconds, check on explorer',
        'sender': 'Sender',
        'recipient': 'Recipient',
        'amount': 'Amount',
        'gas': 'Gas',
        'block': 'Block',
        'amount_txs': 'transactions',
        'balance': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✔ COMPLETED: {txs_txs}/{tx_total} TIPs SUCCESSFUL',
        'error': '✘ Error',
        'invalid_number': 'Please enter a valid number!',
        'tip_count_error': 'Number of TIPs must be greater than 0!',
        'amount_error': 'Amount must be greater than 0.000001!',
        'invalid_choice': 'Invalid choice!',
        'connect_success': '✔ Success: Connected to Pharos Testnet',
        'connect_error': '✘ Failed to connect to RPC',
        'web3_error': '✘ Web3 connection failed',
        'pvkey_not_found': '✘ pvkey.txt file not found',
        'pvkey_empty': '✘ No valid private keys found',
        'pvkey_error': '✘ Failed to read pvkey.txt',
        'username_not_found': '✘ username.txt file not found',
        'username_empty': '✘ No valid accounts found in username.txt',
        'username_error': '✘ Failed to read username.txt',
        'invalid_username': 'is not a valid account, skipped',
        'warning_line': '⚠️ Warning: Line',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'No proxy',
        'unknown': 'Unknown',
        'no_proxies': 'No proxies found in proxies.txt',
    }
}

# Hàm hiển thị
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

def print_wallets_summary(count: int, language: str = 'vi'):
    print_border(
        LNG[language]['processing'].format(KEYS=count),
        Fore.MAGENTA
    )
    print()

def display_all_wallets_balances(w3: Web3, private_keys: list, language: str = 'vi'):
    print_border(LNG[language]['balance'], Fore.CYAN)
    print(f"{Fore.CYAN}  Wallet | {LNG[language]['amount_unit']:<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * 6} | {'-' * 10}{Style.RESET_ALL}")
    
    for i, key in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        balance = check_balance(w3, address, language)
        print(f"{Fore.YELLOW}  {i:<6} | {balance:>10.6f}{Style.RESET_ALL}")
    print()

# Hàm tiện ích
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'vi') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  {LNG[language]['pvkey_not_found']}{Style.RESET_ALL}")
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
                        valid_keys.append(key)
                    else:
                        print(f"{Fore.YELLOW}  {LNG[language]['warning_line']} {i}: {LNG[language]['invalid_username']} - {key}{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  {LNG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  {LNG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def load_usernames(file_path: str = "username.txt", language: str = 'vi') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  {LNG[language]['username_not_found']}. Creating new file.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add usernames or emails here, one per line\n# Example: @username or user@gmail.com\n")
            return None
        
        usernames = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                user = line.strip()
                if user and not user.startswith('#'):
                    usernames.append(user)
                else:
                    print(f"{Fore.YELLOW}  {LNG[language]['warning_line']} {i}: {LNG[language]['invalid_username']} - {user}{Style.RESET_ALL}")
        
        if not usernames:
            print(f"{Fore.RED}  {LNG[language]['username_empty']}{Style.RESET_ALL}")
            return None
        
        return usernames
    except Exception as e:
        print(f"{Fore.RED}  {LNG[language]['username_error']}: {str(e)}{Style.RESET_ALL}")
        return None

def load_proxies(file_path: str = "proxies.txt", language: str = 'vi') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  {LNG[language]['no_proxies']}. Running without proxy.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add proxies here, one per line\n# Example: socks5://user:pass@host:port or http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not proxy.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW}  {LNG[language]['no_proxies']}. Running without proxy.{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.YELLOW}  {LNG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED}  {LNG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

async def get_proxy_ip(proxy: str = None, language: str = 'vi') -> str:
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
                    return LNG[language]['unknown']
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LNG[language]['unknown'])
                    return LNG[language]['unknown']
        else:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LNG[language]['unknown'])
                    return LNG[language]['unknown']
    except Exception as e:
        return LNG[language]['unknown']

def connect_web3(language: str = 'vi'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if w3.is_connected():
            print(f"{Fore.GREEN}  {LNG[language]['connect_success']} | Chain ID: {w3.eth.chain_id} | RPC: {NETWORK_URL}{Style.RESET_ALL}")
            return w3
        else:
            print(f"{Fore.RED}  {LNG[language]['connect_error']} at {NETWORK_URL}{Style.RESET_ALL}")
            sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}  {LNG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

async def wait_for_receipt(w3: Web3, tx_hash: str, max_wait_time: int = 300, language: str = 'vi'):
    start_time = asyncio.get_event_loop().time()
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt
        except Exception:
            pass
        
        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time > max_wait_time:
            return None
        
        await asyncio.sleep(5)

def check_balance(w3: Web3, address: str, language: str = 'vi') -> float:
    try:
        balance = w3.eth.get_balance(address)
        return float(w3.from_wei(balance, 'ether'))
    except Exception as e:
        print(f"{Fore.YELLOW}  {LNG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return -1

def generate_random_username(platform: str) -> str:
    prefix = '@' if platform in ['x', 'tiktok'] else ''
    length = random.randint(5, 12)
    chars = string.ascii_lowercase + string.digits + '_'
    return prefix + ''.join(random.choice(chars) for _ in range(length))

async def send_tip(w3: Web3, private_key: str, platform: str, username: str, amount: float, proxy: str, language: str) -> bool:
    account = Account.from_key(private_key)
    sender_address = account.address
    contract = w3.eth.contract(address=Web3.to_checksum_address(ROUTER), abi=CONTRACT_ABI)
    
    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LNG[language]['no_proxy']
            print_message(f"  🔄 {LNG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}", Fore.CYAN)

            print_message(f"  > {LNG[language]['balance_check']}", Fore.CYAN)
            balance = check_balance(w3, sender_address, language)
            if balance < CONFIG['MINIMUM_BALANCE'] + amount:
                print_message(f"  {LNG[language]['insufficient_balance'].format(required=CONFIG['MINIMUM_BALANCE'] + amount)}: {balance:.6f} {SYMBOL}", Fore.RED)
                return False

            print_message(f"  > {LNG[language]['sending']}", Fore.CYAN)
            nonce = w3.eth.get_transaction_count(sender_address)
            amount_wei = w3.to_wei(amount, 'ether')
            tip_token = {
                "tokenType": 1,
                "tokenAddress": "0x0000000000000000000000000000000000000000"
            }
            tip_recipient = {
                "idSource": platform,
                "id": username,
                "amount": amount_wei,
                "nftIds": []
            }
            tx = contract.functions.tip(tip_token, tip_recipient).build_transaction({
                'from': sender_address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': w3.to_wei('50', 'gwei'),
                'value': amount_wei,
                'chainId': CHAIN_ID
            })

            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=300, language=language)
            if receipt is None:
                print_message(f"  {LNG[language]['timeout'].format(timeout=300)} - Tx: {tx_link}", Fore.YELLOW)
                return False
            elif receipt.status == 1:
                total_cost = w3.from_wei(receipt['gasUsed'] * tx['gasPrice'], 'ether')
                print_message(f"  {LNG[language]['success']} │ Tx: {tx_link}", Fore.GREEN)
                print_message(f"    - {LNG[language]['sender']}: {sender_address}", Fore.YELLOW)
                print_message(f"    - {LNG[language]['recipient']}: {username}", Fore.YELLOW)
                print_message(f"    - {LNG[language]['amount']}: {amount:.6f} {SYMBOL}", Fore.YELLOW)
                print_message(f"    - {LNG[language]['gas']}: {receipt['gasUsed']}", Fore.YELLOW)
                print_message(f"    - {LNG[language]['block']}: {receipt['blockNumber']}", Fore.YELLOW)
                print_message(f"    - {LNG[language]['balance']}: {check_balance(w3, sender_address, language):.6f} {SYMBOL}", Fore.YELLOW)
                return True
            else:
                print_message(f"  {LNG[language]['failure']} │ Tx: {tx_link}", Fore.RED)
                return False
        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print_message(f"  {LNG[language]['failure']}: {str(e)} - Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}", Fore.RED)
                print_message(f"  {LNG[language]['pausing']} {delay:.2f} {LNG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
                continue
            print_message(f"  {LNG[language]['failure']}: {str(e)} - Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}", Fore.RED)
            return False
    return False

async def process_wallet(index: int, private_key: str, proxy: str, w3: Web3, platform: str, tip_count: int, amount: float, usernames: list, language: str) -> int:
    wallet_index = index + 1
    successful_tips = 0
    
    try:
        for tip_iter in range(tip_count):
            print_message(f"  > {LNG[language]['tip']} {tip_iter + 1}/{tip_count}", Fore.CYAN)
            account = Account.from_key(private_key)
            username = random.choice(usernames) if usernames else generate_random_username(platform)
            if await send_tip(w3, private_key, platform, username, amount, proxy, language):
                successful_tips += 1
            if tip_iter < tip_count - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN'][0], CONFIG['PAUSE_BETWEEN'][1])
                print_message(f"  {LNG[language]['pausing']} {delay:.2f} {LNG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
            print_separator()
        return successful_tips
    except Exception as e:
        print_message(f"  {LNG[language]['error']}: Wallet {wallet_index} failed: {str(e)}", Fore.RED)
        print_separator(Fore.RED)
        return 0

async def run_primussend(language: str = 'vi'):
    print()
    print_border(LNG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    proxies = load_proxies('proxies.txt', language)
    random.shuffle(private_keys)
    print(f"{Fore.YELLOW}  {LNG[language]['info']}: {LNG[language]['found']} {len(private_keys)} {LNG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    display_all_wallets_balances(w3, private_keys, language)
    print_separator()

    while True:
        print_border(LNG[language]['enter_tip_count'], Fore.YELLOW)
        try:
            tip_count_input = input(f"{Fore.YELLOW}  > {LNG[language]['tip_count']}{Style.RESET_ALL}")
            tip_count = int(tip_count_input) if tip_count_input.strip() else 1
            if tip_count <= 0:
                print(f"{Fore.RED}  {LNG[language]['error']}: {LNG[language]['tip_count_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  {LNG[language]['selected']}: {tip_count} {LNG[language]['choice']}{Style.RESET_ALL}")
                break
        except ValueError:
            print(f"{Fore.RED}  {LNG[language]['error']}: {LNG[language]['invalid_number']}{Style.RESET_ALL}")

    while True:
        print_border(LNG[language]['enter_amount'], Fore.YELLOW)
        try:
            amount_input = input(f"{Fore.YELLOW}  > {LNG[language]['tip_amount']}{Style.RESET_ALL}")
            amount = float(amount_input) if amount_input.strip() else 0.001
            if amount < 0.000001:
                print(f"{Fore.RED}  {LNG[language]['error']}: {LNG[language]['amount_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  {LNG[language]['selected']}: {amount} {LNG[language]['amount_unit']}{Style.RESET_ALL}")
                break
        except ValueError:
            print(f"{Fore.RED}  {LNG[language]['error']}: {LNG[language]['invalid_number']}{Style.RESET_ALL}")

    while True:
        print_border(LNG[language]['select_platform'], Fore.YELLOW)
        print(f"{Fore.GREEN}    ├─ {LNG[language]['x_option']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    ├─ {LNG[language]['tiktok_option']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    └─ {LNG[language]['google_option']}{Style.RESET_ALL}")
        platform_choice = input(f"{Fore.YELLOW}  > Enter choice (1-3): {Style.RESET_ALL}").strip()
        if platform_choice == '1':
            platform = 'x'
            break
        elif platform_choice == '2':
            platform = 'tiktok'
            break
        elif platform_choice == '3':
            platform = 'google'
            break
        print(f"{Fore.RED}  {LNG[language]['invalid_choice']}{Style.RESET_ALL}")

    while True:
        print_border(LNG[language]['select_tip_type'], Fore.YELLOW)
        print(f"{Fore.GREEN}    ├─ {LNG[language]['random_option']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    └─ {LNG[language]['file_option']}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}  > {LNG[language]['choice_prompt']}{Style.RESET_ALL}").strip()
        if choice in ['1', '2']:
            break
        print(f"{Fore.RED}  {LNG[language]['invalid_choice']}{Style.RESET_ALL}")

    usernames = None
    if choice == '2':
        usernames = load_usernames('username.txt', language)
        if not usernames:
            return
        print_border(LNG[language]['start_file'].format(user_count=len(usernames)), Fore.CYAN)
    else:
        print_border(LNG[language]['start_random'].format(tip_count=tip_count), Fore.CYAN)

    successful_tips = 0
    total_tips = (tip_count if choice == '1' else len(usernames or [0])) * len(private_keys)
    print_wallets_summary(len(private_keys), language)

    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENT'])
    async def limited_task(index, private_key, proxy):
        nonlocal successful_tips
        async with semaphore:
            result = await process_wallet(index, private_key, proxy, w3, platform, tip_count, amount, usernames, language)
            successful_tips += result
            if index < len(private_keys) - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN'][0], CONFIG['PAUSE_BETWEEN'][1])
                print_message(f"  {LNG[language]['pausing']} {delay:.2f} {LNG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)

    tasks = []
    for i, private_key in enumerate(private_keys):
        proxy = proxies[i % len(proxies)] if proxies else None
        tasks.append(limited_task(i, private_key, proxy))

    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(
        f"{LNG[language]['completed'].format(txs_txs=successful_tips, tx_total=total_tips)}",
        Fore.GREEN
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_primussend('vi'))
