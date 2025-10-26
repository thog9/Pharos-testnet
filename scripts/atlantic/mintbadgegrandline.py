import os
import sys
import asyncio
import random
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector
from typing import List

# Initialize colorama
init(autoreset=True)

# Constants
NETWORK_URL = "https://atlantic.dplabs-internal.com"
CHAIN_ID = 688689
EXPLORER_URL = "https://atlantic.pharosscan.xyz/tx/0x"
IP_CHECK_URL = "https://api.ipify.org?format=json"
BORDER_WIDTH = 80
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [10, 30],
    "PAUSE_BETWEEN_MINTS": [5, 15],
    "MAX_CONCURRENCY": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.001,
    "DEFAULT_GAS": 250000,
    "TIMEOUT": 300
}

# Contract details
CONTRACTS_TO_MINT = [
    {"address": "0x22614ca3393e83da6411a45f012239bafc258abd", "title": "Pharos Atlantic Testnet Badge", "price": 0.1},

]

# ABI
ABI = [
    {
        "inputs": [
            {"name": "_receiver", "type": "address"},
            {"name": "_quantity", "type": "uint256"},
            {"name": "_currency", "type": "address"},
            {"name": "_pricePerToken", "type": "uint256"},
            {
                "components": [
                    {"name": "proof", "type": "bytes32[]"},
                    {"name": "quantityLimitPerWallet", "type": "uint256"},
                    {"name": "pricePerToken", "type": "uint256"},
                    {"name": "currency", "type": "address"}
                ],
                "name": "_allowlistProof",
                "type": "tuple"
            },
            {"name": "_data", "type": "bytes"}
        ],
        "name": "claim",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': '✨ MINT NFT - PHAROS TESTNET ✨',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'connect_success': '✅ Thành công: Đã kết nối với Pharos Testnet │ Chain ID: {chain_id}',
        'connect_error': '❌ Không thể kết nối tới Pharos Testnet: {error}',
        'pvkey_not_found': '❌ Không tìm thấy tệp pvkey.txt',
        'pvkey_empty': '❌ Không tìm thấy khóa riêng hợp lệ',
        'pvkey_error': '❌ Không thể đọc pvkey.txt',
        'invalid_key': 'khóa riêng không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy} ({error})',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'checking_balance': 'Đang kiểm tra số dư...',
        'no_balance': '❌ Số dư không đủ: {balance:.6f} PHRS (cần {required:.6f} PHRS)',
        'contract_info': 'Contract: {title} | Địa chỉ: {address} | Giá: {price:.6f} PHRS',
        'nft_balance': 'Số dư NFT ({title}): {count}',
        'enter_nft_amount': 'Nhập số lượng NFT muốn mint (1-10): ',
        'invalid_nft_amount': 'Số lượng không hợp lệ, vui lòng nhập số từ 1 đến 10',
        'preparing_tx': 'Đang chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'waiting_tx': 'Đang đợi xác nhận giao dịch...',
        'success': '✔ ✅ Thành công: Mint NFT từ {title}! | TX: ',
        'failure': '❌ Thất bại: Mint NFT: {error}',
        'timeout': '⚠ Giao dịch chưa xác nhận sau {timeout} giây, kiểm tra explorer: {tx_link}',
        'already_minted': '⚠ Ví này đã mint NFT ({title}) rồi! Vui lòng không thực hiện lại.',
        'address': 'Địa chỉ',
        'gas': 'Gas',
        'gas_price': 'Gas Price',
        'total_cost': 'Tổng chi phí',
        'block': 'Khối',
        'balance': 'Số dư',
        'balance_info': 'Số dư ví',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✔ HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'gas_estimation_failed': '❌ Không thể ước lượng gas: {error}',
        'default_gas_used': 'Sử dụng gas mặc định: {gas}',
        'tx_rejected': '❌ Giao dịch bị từ chối: {error}',
        'select_contract': 'Chọn NFT để mint',
        'invalid_contract': '❌ Lựa chọn không hợp lệ, chọn số từ 1 đến {max}',
    },
    'en': {
        'title': '✨ MINT NFT - PHAROS TESTNET ✨',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'connect_success': '✅ Success: Connected to Pharos Testnet │ Chain ID: {chain_id}',
        'connect_error': '❌ Failed to connect to Pharos Testnet: {error}',
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
        'invalid_proxy': '⚠ Invalid or non-working proxy: {proxy} ({error})',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'checking_balance': 'Checking balance...',
        'no_balance': '❌ Insufficient balance: {balance:.6f} PHRS (need {required:.6f} PHRS)',
        'contract_info': 'Contract: {title} | Address: {address} | Price: {price:.6f} PHRS',
        'nft_balance': 'NFT Balance ({title}): {count}',
        'enter_nft_amount': 'Enter number of NFTs to mint (1-10): ',
        'invalid_nft_amount': 'Invalid amount, please enter a number from 1 to 10',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'waiting_tx': 'Waiting for transaction confirmation...',
        'success': '✔ ✅ Success: Minted NFT from {title}! | TX: ',
        'failure': '❌ Failed: Mint NFT: {error}',
        'timeout': '⚠ Transaction not confirmed after {timeout} seconds, check explorer: {tx_link}',
        'already_minted': '⚠ This wallet has already minted NFT ({title})! Please do not attempt again.',
        'address': 'Address',
        'gas': 'Gas',
        'gas_price': 'Gas Price',
        'total_cost': 'Total Cost',
        'block': 'Block',
        'balance': 'Balance',
        'balance_info': 'Wallet Balances',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✔ COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'gas_estimation_failed': '❌ Failed to estimate gas: {error}',
        'default_gas_used': 'Using default gas: {gas}',
        'tx_rejected': '❌ Transaction rejected: {error}',
        'select_contract': 'Select NFT to mint',
        'invalid_contract': '❌ Invalid choice, select a number from 1 to {max}',
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
    print(f"{color} {message}{Style.RESET_ALL}")

def print_wallets_summary(count: int, language: str = 'vi'):
    print_border(
        LANG[language]['processing_wallets'].format(count=count),
        Fore.MAGENTA
    )
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

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'vi') -> List[tuple]:
    try:
        if not os.path.exists(file_path):
            print_message(f"✖ {LANG[language]['pvkey_not_found']}", Fore.RED)
            with open(file_path, 'w') as f:
                f.write("# Thêm private keys vào đây, mỗi key trên một dòng\n# Ví dụ: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
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
                        print_message(f"⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key[:10]}...", Fore.YELLOW)
        
        if not valid_keys:
            print_message(f"✖ {LANG[language]['pvkey_empty']}", Fore.RED)
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print_message(f"✖ {LANG[language]['pvkey_error']}: {str(e)}", Fore.RED)
        sys.exit(1)

def load_proxies(file_path: str = "proxies.txt", language: str = 'vi') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print_message(f"⚠ {LANG[language]['no_proxies']}. Using no proxy.", Fore.YELLOW)
            with open(file_path, 'w') as f:
                f.write("# Thêm proxy vào đây, mỗi proxy trên một dòng\n# Ví dụ: socks5://user:pass@host:port hoặc http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not proxy.startswith('#'):
                    if not proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')):
                        parts = proxy.split(':')
                        if len(parts) == 4:
                            proxy = f"socks5://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
                        elif len(parts) >= 3 and '@' in proxy:
                            proxy = f"socks5://{proxy}"
                        else:
                            print_message(f"⚠ {LANG[language]['invalid_proxy'].format(proxy=proxy)}", Fore.YELLOW)
                            continue
                    proxies.append(proxy)
        
        if not proxies:
            print_message(f"⚠ {LANG[language]['no_proxies']}. Using no proxy.", Fore.YELLOW)
            return []
        
        print_message(f"ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}", Fore.YELLOW)
        return proxies
    except Exception as e:
        print_message(f"✖ {LANG[language]['error']}: {str(e)}", Fore.RED)
        return []

async def get_proxy_ip(proxy: str = None, language: str = 'vi') -> str:
    try:
        connector = ProxyConnector.from_url(proxy) if proxy else None
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('ip', LANG[language]['unknown'])
                print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}", Fore.YELLOW)
                return LANG[language]['unknown']
    except Exception as e:
        print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}", Fore.YELLOW)
        return LANG[language]['unknown']

def connect_web3(language: str = 'vi'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if not w3.is_connected():
            print_message(f"✖ {LANG[language]['connect_error'].format(error='Không thể kết nối')}", Fore.RED)
            sys.exit(1)
        chain_id = w3.eth.chain_id
        if chain_id != CHAIN_ID:
            print_message(f"✖ {LANG[language]['connect_error'].format(error=f'Chain ID không khớp: kỳ vọng {CHAIN_ID}, nhận được {chain_id}')}", Fore.RED)
            sys.exit(1)
        print_message(f"✔ {LANG[language]['connect_success'].format(chain_id=chain_id)}", Fore.GREEN)
        return w3
    except Exception as e:
        print_message(f"✖ {LANG[language]['connect_error'].format(error=str(e))}", Fore.RED)
        sys.exit(1)

def check_balance(w3: Web3, address: str, language: str = 'vi') -> float:
    try:
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        return float(balance_eth)
    except Exception as e:
        print_message(f"✖ {LANG[language]['error']}: {str(e)}", Fore.RED)
        return 0.0

async def check_nft_balance(w3: Web3, address: str, contract_address: str, title: str, language: str = 'vi') -> int:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://grandline-backend-scan-ku6qd.ondigitalocean.app/profile/{address}", headers=HEADERS) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        # Kiểm tra xem hợp đồng có trong danh sách NFT của ví không
                        for nft in data.get("data", []):
                            if nft["collectionAddress"].lower() == contract_address.lower():
                                print_message(f"ℹ {LANG[language]['nft_balance'].format(title=title, count=1)}", Fore.YELLOW)
                                return 1  # Ví đã có NFT từ hợp đồng này
                        print_message(f"ℹ {LANG[language]['nft_balance'].format(title=title, count=0)}", Fore.YELLOW)
                        return 0  # Ví chưa có NFT từ hợp đồng này
                    else:
                        print_message(f"✖ {LANG[language]['error']}: Không thể lấy dữ liệu từ API: {data.get('message', 'Unknown error')}", Fore.RED)
                        return 0
                else:
                    print_message(f"✖ {LANG[language]['error']}: API trả về mã lỗi {response.status}", Fore.RED)
                    return 0
    except Exception as e:
        print_message(f"✖ {LANG[language]['error']}: Không thể kiểm tra số dư NFT cho {title} ({contract_address}): {str(e)}", Fore.RED)
        return 0

async def wait_for_receipt(w3: Web3, tx_hash: str, timeout: int, language: str = 'vi'):
    start_time = asyncio.get_event_loop().time()
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt
        except Exception:
            pass
        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time > timeout:
            return None
        await asyncio.sleep(5)

async def mint_nft(w3: Web3, private_key: str, wallet_index: int, contract: dict, proxy: str, language: str = 'vi') -> bool:
    account = Account.from_key(private_key)
    sender_address = account.address
    contract_address = contract["address"]
    title = contract["title"]
    price = contract["price"]
    mint_count = 1

    print_message(f"ℹ Đang xử lý hợp đồng: {title} ({contract_address})", Fore.YELLOW)
    print_message(f"> {LANG[language]['checking_balance']}", Fore.CYAN)
    balance = check_balance(w3, sender_address, language)
    required_balance = price + CONFIG['MINIMUM_BALANCE']
    if balance < required_balance:
        print_message(f"✖ {LANG[language]['no_balance'].format(balance=balance, required=required_balance)}", Fore.RED)
        return False

    # Kiểm tra số dư NFT bằng API
    print_message(f"ℹ Đang kiểm tra số dư NFT cho hợp đồng {title} ({contract_address})", Fore.YELLOW)
    if await check_nft_balance(w3, sender_address, contract_address, title, language) > 0:
        print_message(f"✖ {LANG[language]['already_minted'].format(title=title)}", Fore.YELLOW)
        return False

    public_ip = await get_proxy_ip(proxy, language)
    proxy_display = proxy if proxy else LANG[language]['no_proxy']
    print_message(f"🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}", Fore.CYAN)

    contract_instance = w3.eth.contract(address=w3.to_checksum_address(contract_address), abi=ABI)

    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            print_message(f"> {LANG[language]['preparing_tx']}", Fore.CYAN)
            nonce = w3.eth.get_transaction_count(sender_address, 'pending')
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))

            allowlist_proof = ([], 0, 0, w3.to_checksum_address("0x0000000000000000000000000000000000000000"))
            data = b""
            claim_tx = contract_instance.functions.claim(
                sender_address,
                mint_count,
                w3.to_checksum_address("0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"),
                w3.to_wei(price, 'ether'),
                allowlist_proof,
                data
            ).build_transaction({
                'from': sender_address,
                'nonce': nonce,
                'gasPrice': gas_price,
                'value': w3.to_wei(price, 'ether') * mint_count
            })

            try:
                estimated_gas = w3.eth.estimate_gas(claim_tx)
                claim_tx['gas'] = int(estimated_gas * 1.2)
                print_message(f" - Gas ước lượng: {estimated_gas} | Gas limit: {claim_tx['gas']}", Fore.YELLOW)
            except Exception as e:
                claim_tx['gas'] = CONFIG['DEFAULT_GAS']
                print_message(f"⚠ {LANG[language]['gas_estimation_failed'].format(error=str(e))}. {LANG[language]['default_gas_used'].format(gas=CONFIG['DEFAULT_GAS'])}", Fore.YELLOW)

            print_message(f"> {LANG[language]['sending_tx']}", Fore.CYAN)
            signed_tx = w3.eth.account.sign_transaction(claim_tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            print_message(f"> {LANG[language]['waiting_tx']}", Fore.CYAN)
            receipt = await wait_for_receipt(w3, tx_hash, CONFIG['TIMEOUT'], language)

            if receipt is None:
                print_message(f"⚠ {LANG[language]['timeout'].format(timeout=CONFIG['TIMEOUT'], tx_link=tx_link)}", Fore.YELLOW)
                return False
            elif receipt.status == 1:
                total_cost = w3.from_wei(receipt['gasUsed'] * claim_tx['gasPrice'], 'ether')
                print_message(f"{LANG[language]['success'].format(title=title)} {tx_link}", Fore.GREEN)
                print_message(f"    - {LANG[language]['address']}: {sender_address}", Fore.YELLOW)
                print_message(f"    - {LANG[language]['block']}: {receipt['blockNumber']}", Fore.YELLOW)
                print_message(f"    - {LANG[language]['gas']}: {receipt['gasUsed']} | {LANG[language]['gas_price']}: {w3.from_wei(claim_tx['gasPrice'], 'gwei'):.6f} Gwei", Fore.YELLOW)
                print_message(f"    - {LANG[language]['total_cost']}: {total_cost:.12f} PHRS | {LANG[language]['balance']}: {check_balance(w3, sender_address, language):.6f} PHRS", Fore.YELLOW)
                return True
            else:
                print_message(f"✖ {LANG[language]['failure'].format(error='Transaction failed')}", Fore.RED)
                return False
        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                print_message(f"✖ {LANG[language]['failure'].format(error=str(e))}", Fore.RED)
                print_message(f"⚠ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
                continue
            print_message(f"✖ {LANG[language]['failure'].format(error=str(e))}", Fore.RED)
            return False
    return False

def display_all_wallets_balances(w3: Web3, private_keys: List[tuple], language: str = 'vi'):
    print_border(LANG[language]['balance_info'], Fore.CYAN)
    print(f"{Fore.CYAN} Wallet | {'Address':<46} | {'PHRS':<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN} {'-' * 6} | {'-' * 46} | {'-' * 10}{Style.RESET_ALL}")
    
    for i, (profile_num, key) in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        balance = check_balance(w3, address, language)
        print(f"{Fore.YELLOW} {i:<6} | {address:<46} | {balance:>10.6f}{Style.RESET_ALL}")

async def process_wallet(index: int, profile_num: int, private_key: str, proxy: str, w3: Web3, contract: dict, language: str) -> bool:
    sender_address = Account.from_key(private_key).address
    print_border(f"Ví {profile_num}: {sender_address[:6]}...{sender_address[-4:]}", Fore.YELLOW)
    try:
        # Truyền đúng hợp đồng vào mint_nft
        return await mint_nft(w3, private_key, profile_num, contract, proxy, language)
    except Exception as e:
        print_message(f"✖ Ví {profile_num} thất bại: {str(e)}", Fore.RED)
        return False

async def run_mintbadgegrandline(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    proxies = load_proxies('proxies.txt', language)
    private_keys = load_private_keys('pvkey.txt', language)
    print_message(f"ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}", Fore.YELLOW)
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    display_all_wallets_balances(w3, private_keys, language)
    print_separator()

    print_border(LANG[language]['select_contract'], Fore.CYAN)
    print()
    for idx, contract in enumerate(CONTRACTS_TO_MINT, 1):
        print_message(f"{idx}. {contract['title']}", Fore.YELLOW)
    print()
    while True:
        try:
            choice = int(input(f"{Fore.CYAN}> {Style.RESET_ALL}"))
            if 1 <= choice <= len(CONTRACTS_TO_MINT):
                break
            print_message(f"✖ {LANG[language]['invalid_contract'].format(max=len(CONTRACTS_TO_MINT))}", Fore.RED)
        except ValueError:
            print_message(f"✖ {LANG[language]['invalid_contract'].format(max=len(CONTRACTS_TO_MINT))}", Fore.RED)

    selected_contract = CONTRACTS_TO_MINT[choice - 1]
    print_message(f"ℹ {LANG[language]['contract_info'].format(title=selected_contract['title'], address=selected_contract['address'][:6] + '...' + selected_contract['address'][-4:], price=selected_contract['price'])}", Fore.YELLOW)
    print_separator()

    total_wallets = len(private_keys)
    successful_mints = 0
    CONFIG['TOTAL_WALLETS'] = total_wallets
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], total_wallets)

    print_wallets_summary(total_wallets, language)

    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    async def limited_task(index, profile_num, private_key, proxy):
        nonlocal successful_mints
        async with semaphore:
            # Truyền selected_contract thay vì contract cố định
            result = await process_wallet(index, profile_num, private_key, proxy, w3, selected_contract, language)
            if result:
                successful_mints += 1
            if index < total_wallets - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_MINTS'][0], CONFIG['PAUSE_BETWEEN_MINTS'][1])
                print_message(f"ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)

    tasks = []
    for i, (profile_num, private_key) in enumerate(private_keys):
        proxy = proxies[i % len(proxies)] if proxies else None
        tasks.append(limited_task(i, profile_num, private_key, proxy))

    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(
        f"{LANG[language]['completed'].format(successful=successful_mints, total=total_wallets)}",
        Fore.GREEN if successful_mints > 0 else Fore.RED
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_mintbadgegrandline('vi'))




