import os
import sys
import asyncio
import random
import string
from datetime import datetime
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from hexbytes import HexBytes
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector

# Khởi tạo colorama
init(autoreset=True)

# Constants
NETWORK_URL = "https://testnet.dplabs-internal.com"
CHAIN_ID = 688688
EXPLORER_URL = "https://testnet.pharosscan.xyz/tx/0x"
CONTROLLER_ADDRESS = "0x51be1ef20a1fd5179419738fc71d95a8b6f8a175"
RESOLVER = "0x9a43dcA1C3BB268546b98eb2AB1401bFc5b58505"
DURATION = 31536000
REVERSE_RECORD = True
OWNER_CONTROLLED_FUSES = 0
DATA = []
BORDER_WIDTH = 80
IP_CHECK_URL = "https://api.ipify.org?format=json"
SYMBOL = "PHRS"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}
CONFIG = {
    "PAUSE_BETWEEN": [10, 20],
    "MAX_CONCURRENT": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": Decimal("0.0000001")
}

# Contract ABI
CONTROLLER_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "name", "type": "string"},
            {"name": "owner", "type": "address"},
            {"name": "duration", "type": "uint256"},
            {"name": "secret", "type": "bytes32"},
            {"name": "resolver", "type": "address"},
            {"name": "data", "type": "bytes[]"},
            {"name": "reverseRecord", "type": "bool"},
            {"name": "ownerControlledFuses", "type": "uint16"}
        ],
        "name": "makeCommitment",
        "outputs": [{"name": "", "type": "bytes32"}],
        "stateMutability": "pure",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "commitment", "type": "bytes32"}],
        "name": "commit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "name", "type": "string"},
            {"name": "duration", "type": "uint256"}
        ],
        "name": "rentPrice",
        "outputs": [
            {
                "components": [
                    {"name": "base", "type": "uint256"},
                    {"name": "premium", "type": "uint256"}
                ],
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "name", "type": "string"},
            {"name": "owner", "type": "address"},
            {"name": "duration", "type": "uint256"},
            {"name": "secret", "type": "bytes32"},
            {"name": "resolver", "type": "address"},
            {"name": "data", "type": "bytes[]"},
            {"name": "reverseRecord", "type": "bool"},
            {"name": "ownerControlledFuses", "type": "uint16"}
        ],
        "name": "register",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

LNG = {
    'vi': {
        'title': '✨ PNS DOMAIN MINT - PHAROS TESTNET ✨',
        'info': 'ℹ Thông tin!',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing': '⚠️ ĐANG XỬ LÝ {KEYS} VÍ',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt!',
        'enter_domain_count': '✦ SỐ LẦN MINT DOMAIN',
        'domain_count': 'Nhập số lần mint domain (mặc định 1): ',
        'selected': '✔ Đã chọn',
        'choice': ' domain',
        'select_domain_type': '✦ CHỌN LOẠI MINT DOMAIN',
        'random_option': '1. Mint domain ngẫu nhiên',
        'manual_option': '2. Mint domain thủ công',
        'choice_prompt': 'Nhập lựa chọn (1/2): ',
        'enter_domain': 'Nhập tên domain (ví dụ: thog): ',
        'start_random': '✨ BẮT ĐẦU MINT {domain_count} DOMAIN NGẪU NHIÊN',
        'start_manual': '✨ MINT {domain_count} DOMAIN THỦ CÔNG',
        'processing_wallet': '⚠️ Đang xử lý ví',
        'balance_check': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ (cần {required:.6f} PHRS)',
        'preparing_commit': 'Đang chuẩn bị commitment...',
        'sending_commit': 'Đang gửi commitment...',
        'waiting_commit': 'Đang đợi 60 giây sau commitment...',
        'calculating_price': 'Đang tính phí thuê domain...',
        'domain_price': 'Phí đăng ký domain "{domain}": {price:.6f} PHRS',
        'sending_register': 'Đang gửi giao dịch đăng ký...',
        'success': '✅ Mint domain "{domain}" thành công!',
        'failure': '❌️ Mint domain thất bại!',
        'timeout': '⏰ Giao dịch không xác nhận sau {timeout} giây, kiểm tra trên explorer',
        'sender': 'Người gửi',
        'domain': 'Domain',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✔ HOÀN THÀNH! {txs_txs}/{tx_total} domain thành công',
        'error': '✘ Lỗi',
        'invalid_number': 'Vui lòng nhập số hợp lệ!',
        'domain_count_error': 'Số domain phải lớn hơn 0!',
        'invalid_choice': 'Lựa chọn không hợp lệ!',
        'invalid_domain': 'Tên domain không hợp lệ! Chỉ dùng chữ cái, số, và dấu gạch ngang.',
        'connect_success': '✔ Thành công: Kết nối mạng Pharos Testnet',
        'connect_error': '✘ Không thể kết nối RPC',
        'web3_error': '✘ Kết nối Web3 thất bại',
        'pvkey_not_found': '✘ File pvkey.txt không tồn tại',
        'pvkey_empty': '✘ Không tìm thấy private key hợp lệ',
        'pvkey_error': '✘ Đọc pvkey.txt thất bại',
        'using_proxy': '🔄 Dùng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không proxy',
        'unknown': 'Không rõ',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
    },
    'en': {
        'title': '✨ PNS DOMAIN MINT - PHAROS TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing': '⚠️ PROCESSING {KEYS} WALLETS',
        'found_proxies': 'Found {count} proxies in proxies.txt!',
        'enter_domain_count': '✦ NUMBER OF DOMAINS',
        'domain_count': 'Number of domains to mint (default 1): ',
        'selected': '✔ Selected',
        'choice': ' domains',
        'select_domain_type': '✦ SELECT DOMAIN MINT TYPE',
        'random_option': '1. Mint random domains',
        'manual_option': '2. Mint manual domains',
        'choice_prompt': 'Enter choice (1/2): ',
        'enter_domain': 'Enter domain name (e.g., thog): ',
        'start_random': '✨ STARTING {domain_count} RANDOM DOMAINS',
        'start_manual': '✨ MINTING {domain_count} MANUAL DOMAINS',
        'processing_wallet': '⚠️ Processing wallet',
        'balance_check': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance (need {required:.6f} PHRS)',
        'preparing_commit': 'Preparing commitment...',
        'sending_commit': 'Sending commitment...',
        'waiting_commit': 'Waiting 60 seconds after commitment...',
        'calculating_price': 'Calculating domain rent price...',
        'domain_price': 'Registration fee for domain "{domain}": {price:.6f} PHRS',
        'sending_register': 'Sending registration transaction...',
        'success': '✅ Successfully minted domain "{domain}"!',
        'failure': '❌ Failed to mint domain!',
        'timeout': '⏰ Transaction not confirmed after {timeout} seconds, check on explorer',
        'sender': 'Sender',
        'domain': 'Domain',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✔ COMPLETED! {txs_txs}/{tx_total} domains SUCCESSFUL',
        'error': '✘ Error',
        'invalid_number': 'Please enter a valid number!',
        'domain_count_error': 'Number of domains must be greater than 0!',
        'invalid_choice': 'Invalid choice!',
        'invalid_domain': 'Invalid domain name! Use only letters, numbers, and hyphens.',
        'connect_success': '✔ Success: Connected to Pharos Testnet',
        'connect_error': '✘ Failed to connect to RPC',
        'web3_error': '✘ Web3 connection failed',
        'pvkey_not_found': '✘ pvkey.txt file not found',
        'pvkey_empty': '✘ No valid private keys found',
        'pvkey_error': '✘ Failed to read pvkey.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'No proxy',
        'unknown': 'Unknown',
        'no_proxies': 'No proxies found in proxies.txt',
    }
}

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
    print(f"{Fore.CYAN}  Wallet | {LNG[language]['balance']:<10}{Style.RESET_ALL}")
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

def is_valid_domain(domain: str) -> bool:
    if not domain:
        return False
    return all(c.isalnum() or c == '-' for c in domain) and not domain.startswith('-') and not domain.endswith('-')

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
                        print(f"{Fore.YELLOW}  {LNG[language]['error']}: Line {i} invalid private key{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  {LNG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  {LNG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

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
        print(f"{Fore.YELLOW}  {LNG[language]['error']}: Failed to check balance: {str(e)}{Style.RESET_ALL}")
        return -1

def random_name(length: int = 9) -> str:
    if length < 3:
        length = 3
    chars_letters = string.ascii_lowercase
    chars_letters_digits = string.ascii_lowercase + string.digits
    name_list = [random.choice(chars_letters)]
    for _ in range(length - 1):
        if name_list[-1] == '-':
            name_list.append(random.choice(chars_letters_digits))
        else:
            name_list.append(random.choice(chars_letters_digits + '-' * 1))
    if name_list[-1] == '-':
        name_list[-1] = random.choice(chars_letters_digits)
    cleaned_name = []
    for i, char in enumerate(name_list):
        if char == '-' and i > 0 and cleaned_name and cleaned_name[-1] == '-':
            cleaned_name.append(random.choice(chars_letters_digits))
        else:
            cleaned_name.append(char)
    while len(cleaned_name) < length:
        if cleaned_name and cleaned_name[-1] == '-':
            cleaned_name.append(random.choice(chars_letters_digits))
        else:
            cleaned_name.append(random.choice(chars_letters_digits + '-'))
    final_result = ''.join(cleaned_name[:length])
    if final_result.startswith('-'):
        final_result = random.choice(chars_letters_digits) + final_result[1:]
    if final_result.endswith('-'):
        final_result = final_result[:-1] + random.choice(chars_letters_digits)
    final_result = final_result.replace('--', random.choice(chars_letters_digits) + random.choice(chars_letters_digits))
    while len(final_result) < length:
        final_result += random.choice(chars_letters_digits)
    return final_result[:length]

async def register_domain(w3: Web3, private_key: str, index: int, domain: str, proxy: str, language: str) -> bool:
    account = Account.from_key(private_key)
    sender_address = account.address
    controller_address = Web3.to_checksum_address(CONTROLLER_ADDRESS)
    resolver_address = Web3.to_checksum_address(RESOLVER)
    
    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LNG[language]['no_proxy']
            print_message(f"  🔄 {LNG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}", Fore.CYAN)

            print_message(f"  > {LNG[language]['balance_check']}", Fore.CYAN)
            balance = Decimal(str(check_balance(w3, sender_address, language)))
            if balance < CONFIG['MINIMUM_BALANCE']:
                print_message(f"  {LNG[language]['insufficient_balance'].format(required=float(CONFIG['MINIMUM_BALANCE']))}: {float(balance):.6f} {SYMBOL}", Fore.RED)
                return False

            controller = w3.eth.contract(address=controller_address, abi=CONTROLLER_ABI)
            secret = HexBytes(os.urandom(32))

            print_message(f"  > {LNG[language]['preparing_commit']}", Fore.CYAN)
            commitment = controller.functions.makeCommitment(
                domain,
                sender_address,
                DURATION,
                secret,
                resolver_address,
                DATA,
                REVERSE_RECORD,
                OWNER_CONTROLLED_FUSES
            ).call()

            print_message(f"  > {LNG[language]['sending_commit']}", Fore.CYAN)
            nonce = w3.eth.get_transaction_count(sender_address)
            tx_commit = controller.functions.commit(commitment).build_transaction({
                'from': sender_address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': w3.eth.gas_price,
                'chainId': CHAIN_ID
            })

            signed_tx_commit = w3.eth.account.sign_transaction(tx_commit, private_key)
            try:
                tx_hash_commit = w3.eth.send_raw_transaction(signed_tx_commit.raw_transaction)
            except ValueError as e:
                if "nonce" in str(e).lower() or "transaction already in pool" in str(e).lower():
                    print_message(f"  {LNG[language]['error']}: Nonce error or transaction already in pool, retrying with new nonce", Fore.YELLOW)
                    nonce = w3.eth.get_transaction_count(sender_address)
                    tx_commit['nonce'] = nonce
                    signed_tx_commit = w3.eth.account.sign_transaction(tx_commit, private_key)
                    tx_hash_commit = w3.eth.send_raw_transaction(signed_tx_commit.raw_transaction)
                else:
                    raise

            receipt_commit = await wait_for_receipt(w3, tx_hash_commit, max_wait_time=300, language=language)
            if receipt_commit is None:
                print_message(f"  {LNG[language]['timeout'].format(timeout=300)} - Tx: {EXPLORER_URL}{tx_hash_commit.hex()}", Fore.YELLOW)
                return False
            elif receipt_commit.status != 1:
                print_message(f"  {LNG[language]['failure']} - Tx: {EXPLORER_URL}{tx_hash_commit.hex()}", Fore.RED)
                return False
            print_message(f"  {LNG[language]['success'].format(domain='Commitment')} - Tx: {EXPLORER_URL}{tx_hash_commit.hex()}", Fore.GREEN)

            print_message(f"  {LNG[language]['waiting_commit']}", Fore.CYAN)
            await asyncio.sleep(60)

            print_message(f"  > {LNG[language]['calculating_price']}", Fore.CYAN)
            price = controller.functions.rentPrice(domain, DURATION).call()
            value = int(price[0]) + int(price[1])  
            rent_price = w3.from_wei(value, 'ether')
            print_message(f"  {LNG[language]['domain_price'].format(domain=domain + '.phrs', price=float(rent_price))}", Fore.YELLOW)

            if balance < rent_price + CONFIG['MINIMUM_BALANCE']:
                required = float(rent_price + CONFIG['MINIMUM_BALANCE'])
                print_message(f"  {LNG[language]['insufficient_balance'].format(required=required)}", Fore.RED)
                return False

            print_message(f"  > {LNG[language]['sending_register']}", Fore.CYAN)
            tx_register = controller.functions.register(
                domain,
                sender_address,
                DURATION,
                secret,
                resolver_address,
                DATA,
                REVERSE_RECORD,
                OWNER_CONTROLLED_FUSES
            ).build_transaction({
                'from': sender_address,
                'nonce': w3.eth.get_transaction_count(sender_address),
                'gas': 300000,
                'gasPrice': w3.eth.gas_price,
                'value': value,
                'chainId': CHAIN_ID
            })

            signed_tx_register = w3.eth.account.sign_transaction(tx_register, private_key)
            try:
                tx_hash_register = w3.eth.send_raw_transaction(signed_tx_register.raw_transaction)
            except ValueError as e:
                if "nonce" in str(e).lower() or "transaction already in pool" in str(e).lower():
                    print_message(f"  {LNG[language]['error']}: Nonce error or transaction already in pool, retrying with new nonce", Fore.YELLOW)
                    tx_register['nonce'] = w3.eth.get_transaction_count(sender_address)
                    signed_tx_register = w3.eth.account.sign_transaction(tx_register, private_key)
                    tx_hash_register = w3.eth.send_raw_transaction(signed_tx_register.raw_transaction)
                else:
                    raise

            receipt_register = await wait_for_receipt(w3, tx_hash_register, max_wait_time=300, language=language)
            if receipt_register is None:
                print_message(f"  {LNG[language]['timeout'].format(timeout=300)} - Tx: {EXPLORER_URL}{tx_hash_register.hex()}", Fore.YELLOW)
                return False
            elif receipt_register.status != 1:
                print_message(f"  {LNG[language]['failure']} - Tx: {EXPLORER_URL}{tx_hash_register.hex()}", Fore.RED)
                return False

            print_message(f"  {LNG[language]['success'].format(domain=domain + '.phrs')} - Tx: {EXPLORER_URL}{tx_hash_register.hex()}", Fore.GREEN)
            print_message(f"    - {LNG[language]['sender']}: {sender_address}", Fore.YELLOW)
            print_message(f"    - {LNG[language]['domain']}: {domain}.phrs", Fore.YELLOW)
            print_message(f"    - {LNG[language]['gas']}: {receipt_register['gasUsed']}", Fore.YELLOW)
            print_message(f"    - {LNG[language]['block']}: {receipt_register['blockNumber']}", Fore.YELLOW)
            print_message(f"    - {LNG[language]['balance']}: {check_balance(w3, sender_address, language):.6f} {SYMBOL}", Fore.YELLOW)
            return True

        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print_message(f"  {LNG[language]['failure']}: {str(e)[:150]}... - Tx: {EXPLORER_URL}{tx_hash_commit.hex() if 'tx_hash_commit' in locals() else 'Not sent'}", Fore.RED)
                print_message(f"  {LNG[language]['pausing']} {delay:.2f} {LNG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
                continue
            print_message(f"  {LNG[language]['failure']}: {str(e)[:150]}... - Tx: {EXPLORER_URL}{tx_hash_commit.hex() if 'tx_hash_commit' in locals() else 'Not sent'}", Fore.RED)
            return False
    return False

async def process_wallet(index: int, private_key: str, proxy: str, w3: Web3, domain_count: int, domains: list, language: str) -> int:
    wallet_index = index + 1
    successful_txs = 0
    
    try:
        for domain_iter in range(domain_count):
            print_message(f"  > {LNG[language]['processing_wallet']} {wallet_index} - Domain {domain_iter + 1}/{domain_count}", Fore.CYAN)
            domain = domains[domain_iter % len(domains)] if domains else random_name()
            if await register_domain(w3, private_key, index, domain, proxy, language):
                successful_txs += 1
            if domain_iter < domain_count - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN'][0], CONFIG['PAUSE_BETWEEN'][1])
                print_message(f"  {LNG[language]['pausing']} {delay:.2f} {LNG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
            print_separator()
        return successful_txs
    except Exception as e:
        print_message(f"  {LNG[language]['error']}: Wallet {wallet_index} failed: {str(e)}", Fore.RED)
        print_separator(Fore.RED)
        return 0

async def run_pnsdomain(language: str = 'vi'):
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
        print_border(LNG[language]['enter_domain_count'], Fore.YELLOW)
        try:
            domain_count_input = input(f"{Fore.YELLOW}  > {LNG[language]['domain_count']}{Style.RESET_ALL}")
            domain_count = int(domain_count_input) if domain_count_input.strip() else 1
            if domain_count <= 0:
                print(f"{Fore.RED}  {LNG[language]['error']}: {LNG[language]['domain_count_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  {LNG[language]['selected']}: {domain_count} {LNG[language]['choice']}{Style.RESET_ALL}")
                break
        except ValueError:
            print(f"{Fore.RED}  {LNG[language]['error']}: {LNG[language]['invalid_number']}{Style.RESET_ALL}")

    while True:
        print_border(LNG[language]['select_domain_type'], Fore.YELLOW)
        print(f"{Fore.GREEN}    ├─ {LNG[language]['random_option']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    └─ {LNG[language]['manual_option']}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}  > {LNG[language]['choice_prompt']}{Style.RESET_ALL}").strip()
        if choice in ['1', '2']:
            break
        print(f"{Fore.RED}  {LNG[language]['invalid_choice']}{Style.RESET_ALL}")

    domains = None
    if choice == '2':
        domains = []
        print_border(LNG[language]['enter_domain'], Fore.YELLOW)
        for i in range(domain_count):
            while True:
                domain = input(f"{Fore.YELLOW}  > {LNG[language]['enter_domain']} {i+1}/{domain_count}: {Style.RESET_ALL}").strip()
                if is_valid_domain(domain):
                    domains.append(domain)
                    break
                print(f"{Fore.RED}  {LNG[language]['invalid_domain']}{Style.RESET_ALL}")
        print_border(LNG[language]['start_manual'].format(domain_count=domain_count), Fore.CYAN)
    else:
        print_border(LNG[language]['start_random'].format(domain_count=domain_count), Fore.CYAN)

    successful_txs = 0
    total_txs = domain_count * len(private_keys)
    print_wallets_summary(len(private_keys), language)

    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENT'])
    async def limited_task(index, private_key, proxy):
        nonlocal successful_txs
        async with semaphore:
            result = await process_wallet(index, private_key, proxy, w3, domain_count, domains, language)
            successful_txs += result
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
        f"{LNG[language]['completed'].format(txs_txs=successful_txs, tx_total=total_txs)}",
        Fore.GREEN
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_pnsdomain('vi'))
