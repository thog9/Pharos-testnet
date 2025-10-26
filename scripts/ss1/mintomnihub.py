import os
import sys
import asyncio
import random
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector

# Khởi tạo colorama
init(autoreset=True)

# Độ rộng viền
BORDER_WIDTH = 80

# Constants
NETWORK_URL = "https://testnet.dplabs-internal.com"
CHAIN_ID = 688688
EXPLORER_URL = "https://testnet.pharosscan.xyz/tx/0x"
MINT_PRICE = 0.001001  
IP_CHECK_URL = "https://api.ipify.org?format=json"
TIMEOUT = 300  # Timeout 5 phút
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [10, 30],
    "MAX_CONCURRENCY": 2,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.001,  # PHRS
    "DEFAULT_GAS": 200000
}

# Danh sách contract cố định để mint
CONTRACTS_TO_MINT = [
    {"address": "0x51ba522B904C11D79bC0586A1F4cB385DFB43c6e", "title": "OmniHub x Pharos", "price": MINT_PRICE},
    {"address": "0xA4d6B5c2f3390385452d606EDA8B2418a00b7476", "title": "Pharos Testnet", "price": MINT_PRICE},
    {"address": "0x51ba522B904C11D79bC0586A1F4cB385DFB43c6e", "title": "PHRS Omni", "price": MINT_PRICE},

]

# ABI cho ERC721 contract
ERC721_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    }
]

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': '✨ MINT OMNIHUB NFT - PHAROS TESTNET ✨',
        'info': 'ℹ Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'no_balance': 'Số dư ví không đủ (cần ít nhất {required:.6f} PHRS cho giao dịch)',
        'select_contract': 'Chọn NFTs để mint:\n{options}\n  4. Mint NFTs OmniHub x Pharos | Pharos Testnet | PHRS Omni',
        'invalid_contract': 'Contract không hợp lệ, vui lòng chọn số từ 1 đến 4',
        'contract_info': 'Contract: {title} | Địa chỉ: {address} | Giá: {price:.6f} PHRS',
        'nft_balance': 'Số dư NFT (contract {title}): {count}',
        'has_nft': 'Ví này đã mint {count} NFT từ contract {title}.\n    Bạn có muốn mint thêm không? (y/n): ',
        'preparing_tx': 'Đang chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'waiting_tx': 'Đang đợi xác nhận giao dịch...',
        'success': '✅ Mint NFT từ {title} thành công!',
        'failure': '❌ Mint NFT thất bại',
        'timeout': '⚠ Giao dịch chưa nhận được receipt sau {timeout} giây, kiểm tra trên explorer...',
        'address': 'Địa chỉ ví',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư PHRS',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': '✅ Thành công: Đã kết nối mạng Pharos Testnet',
        'connect_error': '❌ Không thể kết nối RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ File pvkey.txt không tồn tại',
        'pvkey_empty': '❌ Không tìm thấy private key hợp lệ',
        'pvkey_error': '❌ Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': '⚠ Cảnh báo: Dòng',
        'stop_wallet': 'Dừng xử lý ví {wallet}: Quá nhiều giao dịch thất bại liên tiếp',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
    },
    'en': {
        'title': '✨ MINT OMNIHUB NFT - PHAROS TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'no_balance': 'Insufficient balance (need at least {required:.6f} PHRS for transaction)',
        'select_contract': 'Select NFTs to mint:\n{options}\n  4. Mint NFTs OmniHub x Pharos | Pharos Testnet | PHRS Omni',
        'invalid_contract': 'Invalid contract, please select a number from 1 to 4',
        'contract_info': 'Contract: {title} | Address: {address} | Price: {price:.6f} PHRS',
        'nft_balance': 'NFT Balance (contract {title}): {count}',
        'has_nft': 'This wallet has minted {count} NFT(s) from contract {title}.\n    Do you want to mint another? (y/n): ',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'waiting_tx': 'Waiting for transaction confirmation...',
        'success': '✅ Successfully minted NFT from {title}!',
        'failure': '❌ Failed to mint NFT',
        'timeout': '⚠ Transaction receipt not received after {timeout} seconds, check on explorer...',
        'address': 'Wallet address',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'PHRS Balance',
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
        'warning_line': '⚠ Warning: Line',
        'stop_wallet': 'Stopping wallet {wallet}: Too many consecutive failed transactions',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'no_proxies': 'No proxies found in proxies.txt',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
    }
}

# Hàm hiển thị viền đẹp
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

# Hàm hiển thị phân cách
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

# Hàm hiển thị danh sách ví tổng hợp
def print_wallets_summary(private_keys: list, language: str = 'en'):
    print_border(
        LANG[language]['processing_wallets'].format(count=len(private_keys)),
        Fore.MAGENTA
    )
    print()

# Kiểm tra private key hợp lệ
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

# Đọc private keys từ pvkey.txt
def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}")
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
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key[:10]}...{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Đọc proxies từ proxies.txt
def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Dùng không proxy.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm proxy vào đây, mỗi proxy trên một dòng\n# Ví dụ: socks5://user:pass@host:port hoặc http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not line.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Dùng không proxy.{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

# Lấy IP công khai qua proxy
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

# Kết nối Web3
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

# Hàm kiểm tra số dư NFT
def check_nft_balance(w3: Web3, address: str, contract_address: str, language: str = 'en') -> int:
    nft_contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=ERC721_ABI)
    try:
        balance = nft_contract.functions.balanceOf(address).call()
        return balance
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return 0

# Hàm đợi receipt thủ công
async def wait_for_receipt(w3: Web3, tx_hash: str, timeout: int, language: str = 'en'):
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
        
        await asyncio.sleep(5)  # Kiểm tra mỗi 5 giây

# Hàm mint NFT
async def mint_nft(w3: Web3, private_key: str, wallet_index: int, contract: dict, proxy: str = None, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address
    contract_address = contract["address"]
    price = contract["price"]
    title = contract["title"]

    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            # Display proxy info
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

            # Kiểm tra số dư NFT hiện tại
            print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
            nft_balance = check_nft_balance(w3, sender_address, contract_address, language)
            print(f"{Fore.YELLOW}  - {LANG[language]['nft_balance'].format(title=title, count=nft_balance)}{Style.RESET_ALL}")

            proceed = True
            if nft_balance >= 1:
                print(f"{Fore.YELLOW}  - {LANG[language]['has_nft'].format(count=nft_balance, title=title)}{Style.RESET_ALL}")
                choice = input(f"{Fore.GREEN}  > {Style.RESET_ALL}")
                proceed = choice.lower() == 'y'

            if not proceed:
                print(f"{Fore.GREEN}  ✔ {'Bỏ qua mint NFT' if language == 'vi' else 'Skipping NFT mint'}{Style.RESET_ALL}")
                return True

            # Kiểm tra số dư PHRS
            eth_balance = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
            print(f"{Fore.YELLOW}  - {LANG[language]['balance']}: {eth_balance:.6f} PHRS{Style.RESET_ALL}")

            amount_in_wei = int(Web3.to_wei(price, 'ether'))
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))  # Tăng nhẹ gas price

            print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
            payload = "0xa0712d680000000000000000000000000000000000000000000000000000000000000001"
            nonce = w3.eth.get_transaction_count(sender_address, 'pending')

            tx = {
                'from': sender_address,
                'to': Web3.to_checksum_address(contract_address),
                'value': amount_in_wei,
                'data': payload,
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'gasPrice': gas_price
            }

            try:
                estimated_gas = w3.eth.estimate_gas(tx)
                tx['gas'] = int(estimated_gas * 1.2)  # Tăng 20%
                print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {tx['gas']}{Style.RESET_ALL}")
            except Exception as e:
                tx['gas'] = CONFIG['DEFAULT_GAS']
                print(f"{Fore.YELLOW}  ⚠ Không thể ước lượng gas: {str(e)}. Dùng gas mặc định: {CONFIG['DEFAULT_GAS']}{Style.RESET_ALL}")

            total_required = amount_in_wei + (tx['gas'] * gas_price)
            total_required_eth = float(w3.from_wei(total_required, 'ether'))
            if eth_balance < total_required_eth:
                print(f"{Fore.RED}  ✖ {LANG[language]['no_balance'].format(required=total_required_eth)}{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            print(f"{Fore.CYAN}  > {LANG[language]['waiting_tx']}{Style.RESET_ALL}")
            receipt = await wait_for_receipt(w3, tx_hash, TIMEOUT, language)

            if receipt is None:
                print(f"{Fore.YELLOW}  {LANG[language]['timeout'].format(timeout=TIMEOUT)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - Tx: {tx_link}{Style.RESET_ALL}")
                return True
            elif receipt.status == 1:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['success'].format(title=title)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - {LANG[language]['address']}: {sender_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - Tx: {tx_link}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
                return False

        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} | Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  ⚠ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} | Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
            return False

# Hàm xử lý từng ví
async def process_wallet(index: int, profile_num: int, private_key: str, proxy: str, w3: Web3, language: str):
    account = Account.from_key(private_key)
    print(f"{Fore.YELLOW}  {LANG[language]['address']}: {account.address}{Style.RESET_ALL}")

    contracts_with_price = CONTRACTS_TO_MINT
    successful_mints = 0

    # Hiển thị danh sách contract để người dùng chọn
    options = "\n".join([f"  {idx + 1}. {contract['title']}" for idx, contract in enumerate(contracts_with_price)])
    print(f"\n{Fore.CYAN}{LANG[language]['select_contract'].format(options=options)}{Style.RESET_ALL}")
    while True:
        try:
            choice = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if 1 <= choice <= 4:
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_contract']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_contract']}{Style.RESET_ALL}")

    if choice == 4:  # Mint tất cả NFT
        for contract in contracts_with_price:
            print(f"\n{Fore.YELLOW}  - {LANG[language]['contract_info'].format(title=contract['title'], address=contract['address'], price=contract['price'])}{Style.RESET_ALL}")
            if await mint_nft(w3, private_key, profile_num, contract, proxy, language):
                successful_mints += 1
            # Tạm nghỉ giữa các giao dịch để tránh spam
            delay = random.uniform(5, 15)
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
    else:
        selected_contract = contracts_with_price[choice - 1]
        print(f"\n{Fore.YELLOW}  - {LANG[language]['contract_info'].format(title=selected_contract['title'], address=selected_contract['address'], price=selected_contract['price'])}{Style.RESET_ALL}")
        if await mint_nft(w3, private_key, profile_num, selected_contract, proxy, language):
            successful_mints += 1

    print_separator(Fore.GREEN if successful_mints > 0 else Fore.RED)
    return successful_mints

# Hàm chính
async def run_mintomnihub(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    proxies = load_proxies('proxies.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    successful_mints = 0
    total_wallets = len(private_keys)
    failed_attempts = 0
    CONFIG['TOTAL_WALLETS'] = total_wallets
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], total_wallets)

    # In danh sách ví tổng hợp
    print_wallets_summary(private_keys, language)

    random.shuffle(private_keys)
    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    async def limited_task(index, profile_num, private_key, proxy):
        nonlocal successful_mints, failed_attempts
        async with semaphore:
            mints = await process_wallet(index, profile_num, private_key, proxy, w3, language)
            successful_mints += mints
            if mints > 0:
                failed_attempts = 0
            else:
                failed_attempts += 1
                if failed_attempts >= 3:
                    print(f"{Fore.RED}  ✖ {LANG[language]['stop_wallet'].format(wallet=profile_num)}{Style.RESET_ALL}")
                    return
            if index < total_wallets - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)

    tasks = []
    for i, (profile_num, private_key) in enumerate(private_keys):
        proxy = proxies[i % len(proxies)] if proxies else None
        tasks.append(limited_task(i, profile_num, private_key, proxy))

    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(
        f"{LANG[language]['completed'].format(successful=successful_mints, total=successful_mints + (total_wallets - successful_mints))}",
        Fore.GREEN
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_mintomnihub('vi'))
