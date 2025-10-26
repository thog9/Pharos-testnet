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
IP_CHECK_URL = "https://api.ipify.org?format=json"
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
    "MINIMUM_BALANCE": 0.001,
    "DEFAULT_GAS": 1000000
}

# Timer Contract Payload
TIMER_PAYLOAD = "0x608060405260405161052438038061052483398181016040528101906100259190610188565b60003411610068576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040161005f90610212565b60405180910390fd5b600034111561011f5760008173ffffffffffffffffffffffffffffffffffffffff163460405161009790610263565b60006040518083038185875af1925050503d80600081146100d4576040519150601f19603f3d011682016040523d82523d6000602084013e6100d9565b606091505b505090508061011d576040517f08c379a0000000000000000000000000000000000000000000000000000000008152600401610114906102c4565b60405180910390fd5b505b506102e4565b600080fd5b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b60006101558261012a565b9050919050565b6101658161014a565b811461017057600080fd5b50565b6000815190506101828161015c565b92915050565b60006020828403121561019e5761019d610125565b5b60006101ac84828501610173565b91505092915050565b600082825260208201905092915050565b7f4465706c6f796d656e7420726571756972657320612066656500000000000000600082015250565b60006101fc6019836101b5565b9150610207826101c6565b602082019050919050565b6000602082019050818103600083015261022b816101ef565b9050919050565b600081905092915050565b50565b600061024d600083610232565b91506102588261023d565b600082019050919050565b600061026e82610240565b9150819050919050565b7f466565207472616e73666572206661696c656400000000000000000000000000600082015250565b60006102ae6013836101b5565b91506102b982610278565b602082019050919050565b600060208201905081810360008301526102dd816102a1565b9050919050565b610231806102f36000396000f3fe608060405234801561001057600080fd5b50600436106100415760003560e01c80632baeceb714610046578063a87d942c14610050578063d09de08a1461006e575b600080fd5b61004e610078565b005b6100586100ca565b604051610065919061013e565b60405180910390f35b6100766100d3565b005b60008081548092919061008a90610188565b91905055507f1a00a27c962d5410357331e1a8cffff62058bd0161ad624818df31152f1eeb456000546040516100c0919061013e565b60405180910390a1565b60008054905090565b6000808154809291906100e5906101b2565b91905055507f3cf8b50771c17d723f2cb711ca7dadde485b222e13c84ba0730a14093fad6d5c60005460405161011b919061013e565b60405180910390a1565b6000819050919050565b61013881610125565b82525050565b6000602082019050610153600083018461012f565b92915050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052601160045260246000fd5b600061019382610125565b915060008214156101a7576101a6610159565b5b600182039050919050565b60006101bd82610125565b91507fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff8214156101f0576101ef610159565b5b60018201905091905056fea2646970667358221220526250c31d8148ffcfa6d06ab24c6dfbf02441f204c5578890519ec2fdd071c564736f6c63430008090033000000000000000000000000fda77b68d08988e91932a3a4ff4d49d4771536f8"

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': '✨ TRIỂN KHAI HỢP ĐỒNG TIMER - PHAROS TESTNET ✨',
        'info': 'ℹ Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ (cần ít nhất {required:.6f} PHRS cho giao dịch)',
        'preparing_tx': 'Đang chuẩn bị giao dịch...',
        'estimating_gas': 'Đang ước lượng gas...',
        'sending_tx': 'Đang gửi giao dịch...',
        'success_timer': '✅ Triển khai Timer Contract thành công!',
        'failure': '❌ Triển khai hợp đồng thất bại',
        'address': 'Địa chỉ ví',
        'contract_address': 'Địa chỉ hợp đồng',
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
        'debugging_tx': 'Debug giao dịch...',
        'gas_estimation_failed': 'Không thể ước lượng gas: {error}',
        'default_gas_used': 'Sử dụng gas mặc định: {gas}',
        'tx_rejected': 'Giao dịch bị từ chối bởi mạng',
        'stop_wallet': 'Dừng xử lý ví {wallet}: Quá nhiều giao dịch thất bại liên tiếp',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
    },
    'en': {
        'title': '✨ DEPLOY TIMER CONTRACT - PHAROS TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance (need at least {required:.6f} PHRS for transaction)',
        'preparing_tx': 'Preparing transaction...',
        'estimating_gas': 'Estimating gas...',
        'sending_tx': 'Sending transaction...',
        'success_timer': '✅ Successfully deployed Timer Contract!',
        'failure': '❌ Failed to deploy contract',
        'address': 'Wallet address',
        'contract_address': 'Contract Address',
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
        'debugging_tx': 'Debugging transaction...',
        'gas_estimation_failed': 'Failed to estimate gas: {error}',
        'default_gas_used': 'Using default gas: {gas}',
        'tx_rejected': 'Transaction rejected by network',
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
                if proxy and not proxy.startswith('#'):
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

# Triển khai Timer Contract
async def deploy_contract(w3: Web3, private_key: str, wallet_index: int, proxy: str = None, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

            print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
            eth_balance = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
            if eth_balance < CONFIG['MINIMUM_BALANCE']:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=CONFIG['MINIMUM_BALANCE'])}: {eth_balance:.6f} PHRS{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
            nonce = w3.eth.get_transaction_count(sender_address)
            gas_price = w3.eth.gas_price
            await asyncio.sleep(0.5)

            tx_params = {
                'nonce': nonce,
                'from': sender_address,
                'to': '',
                'data': TIMER_PAYLOAD,
                'value': Web3.to_wei(0.05, 'ether'),  
                'chainId': CHAIN_ID,
                'gasPrice': gas_price
            }

            print(f"{Fore.CYAN}  > {LANG[language]['estimating_gas']}{Style.RESET_ALL}")
            try:
                estimated_gas = w3.eth.estimate_gas(tx_params)
                gas_limit = int(estimated_gas * 1.2)
                tx_params['gas'] = gas_limit
                print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
            except Exception as e:
                tx_params['gas'] = CONFIG['DEFAULT_GAS']
                print(f"{Fore.YELLOW}  - {LANG[language]['gas_estimation_failed'].format(error=str(e))}. {LANG[language]['default_gas_used'].format(gas=CONFIG['DEFAULT_GAS'])}{Style.RESET_ALL}")

            required_balance = w3.from_wei(tx_params['gas'] * tx_params['gasPrice'] + tx_params['value'], 'ether')
            if eth_balance < required_balance:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=required_balance)}: {eth_balance:.6f} PHRS{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))

            if receipt.status == 1:
                contract_address = receipt.get('contractAddress', 'N/A')
                print(f"{Fore.GREEN}  ✔ {LANG[language]['success_timer']} │ Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['address']}: {sender_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['contract_address']}: {contract_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['balance']}: {eth_balance:.6f} PHRS{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']} │ Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.RED}    - {LANG[language]['tx_rejected']}{Style.RESET_ALL}")
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
    result = await deploy_contract(w3, private_key, profile_num, proxy, language)
    print_separator(Fore.GREEN if result else Fore.RED)
    return result

# Hàm chính
async def run_easynode(language: str = 'vi'):
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

    successful_deploys = 0
    total_wallets = len(private_keys)
    failed_attempts = 0
    CONFIG['TOTAL_WALLETS'] = total_wallets
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], total_wallets)

    # In danh sách ví tổng hợp
    print_wallets_summary(private_keys, language)

    random.shuffle(private_keys)
    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    async def limited_task(index, profile_num, private_key, proxy):
        nonlocal successful_deploys, failed_attempts
        async with semaphore:
            result = await process_wallet(index, profile_num, private_key, proxy, w3, language)
            if result:
                successful_deploys += 1
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
        f"{LANG[language]['completed'].format(successful=successful_deploys, total=total_wallets)}",
        Fore.GREEN
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_easynode('vi'))
