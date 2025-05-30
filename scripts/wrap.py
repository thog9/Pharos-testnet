import os
import sys
import time
import asyncio
import random
import traceback
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from colorama import init, Fore, Style
from typing import List, Dict
import aiohttp
from aiohttp_socks import ProxyConnector

# Initialize colorama
init(autoreset=True)

# Network Configuration
NETWORK_URL = "https://testnet.dplabs-internal.com"
CHAIN_ID = 688688
EXPLORER_URL = "https://testnet.pharosscan.xyz/tx/0x"
WPHRS_ADDRESS = Web3.to_checksum_address("0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364")
IP_CHECK_URL = "https://api.ipify.org?format=json"
BORDER_WIDTH = 80
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}

# Token Configurations
TOKENS = {
    "PHRS": {"address": "0x0000000000000000000000000000000000000000", "decimals": 18},
    "WPHRS": {"address": WPHRS_ADDRESS, "decimals": 18},
}

# Configuration
CONFIG = {
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 5,
    "GAS_MULTIPLIER": 1.5,
    "DEFAULT_GAS_LIMIT": 200000,
    "MINIMUM_BALANCE": 0.001,
    "TIMEOUT": 300,
    "PAUSE_BETWEEN_ATTEMPTS": [60, 180],
    "PAUSE_BETWEEN_SWAPS": [10, 30],
    "MAX_CONCURRENCY": 5,
    "APPROVE_SPENDER": Web3.to_checksum_address("0x1a4de519154ae51200b0ad7c90f7fac75547888a"),
    "REQUIRE_APPROVAL": False,
}

# ABI for WPHRS Contract
WPHRS_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "wad", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'WRAP PHRS - PHAROS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ: {balance:.6f} {symbol} < {required:.6f} {symbol}',
        'preparing_tx': 'Chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'wrap_success': 'Wrap {amount:.6f} PHRS → WPHRS thành công!',
        'unwrap_success': 'Unwrap {amount:.6f} WPHRS → PHRS thành công!',
        'failure': 'Thất bại',
        'address': 'Địa chỉ',
        'amount': 'Số dư',
        'gas': 'Gas',
        'gas_price': 'Gas Price',
        'total_cost': 'Tổng chi phí',
        'block': 'Khối',
        'balance': 'Số dư: {phrs:.6f} PHRS | WPHRS: {wphrs:.6f}',
        'balance_info': 'Số dư',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'connect_success': 'Thành công: Đã kết nối mạng Pharos Testnet',
        'connect_error': 'Không thể kết nối RPC',
        'web3_error': 'Kết nối Web3 thất bại',
        'pvkey_not_found': 'File pvkey.txt không tồn tại',
        'pvkey_empty': 'Không tìm thấy private key hợp lệ',
        'pvkey_error': 'Không thể đọc pvkey.txt',
        'invalid_key': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'gas_estimation_failed': 'Không thể ước lượng gas: {error}',
        'default_gas_used': 'Sử dụng gas mặc định: {gas}',
        'tx_rejected': 'Giao dịch bị từ chối bởi hợp đồng hoặc mạng: {error}',
        'input_amount': 'Nhập số PHRS (0.000001 - 999): ',
        'input_error': 'Số phải từ 0.000001 đến 999 / Nhập lại số hợp lệ!',
        'cycles': 'SỐ VÒNG LẶP',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'timeout': '⏰ Giao dịch chưa xác nhận sau {timeout} giây, kiểm tra trên explorer',
        'wallet_failed': 'Ví thất bại: {error}',
        'choose_action': 'Chọn hành động (1: PHRS → WPHRS | 2: WPHRS → PHRS | 3: Wrap | Unwrap): ',
        'wrap_only': 'Wrap PHRS → WPHRS',
        'unwrap_only': 'Unwrap WPHRS → PHRS',
        'wrap_and_unwrap': 'Wrap rồi Unwrap',
        'invalid_action': 'Hành động không hợp lệ! Vui lòng chọn 1, 2 hoặc 3.',
        'approving': 'Đang phê duyệt WPHRS cho {spender}...',
        'approval_success': 'Phê duyệt WPHRS thành công!',
    },
    'en': {
        'title': 'WRAP PHRS - PHAROS TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance: {balance:.6f} {symbol} < {required:.6f} {symbol}',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'wrap_success': 'Successfully wrapped {amount:.6f} PHRS → WPHRS!',
        'unwrap_success': 'Successfully unwrapped {amount:.6f} WPHRS → PHRS!',
        'failure': 'Failed',
        'address': 'Address',
        'amount': 'Balance',
        'gas': 'Gas',
        'gas_price': 'Gas Price',
        'total_cost': 'Total Cost',
        'block': 'Block',
        'balance': 'Balance: {phrs:.6f} PHRS | WPHRS: {wphrs:.6f}',
        'balance_info': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'connect_success': 'Success: Connected to Pharos Testnet',
        'connect_error': 'Failed to connect to RPC',
        'web3_error': 'Web3 connection failed',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found',
        'pvkey_error': 'Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'gas_estimation_failed': 'Failed to estimate gas: {error}',
        'default_gas_used': 'Using default gas: {gas}',
        'tx_rejected': 'Transaction rejected by contract or network: {error}',
        'input_amount': 'Enter PHRS amount (0.000001 - 999): ',
        'input_error': 'Amount must be 0.000001-999 / Enter a valid number!',
        'cycles': 'NUMBER OF CYCLES',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'timeout': '⏰ Transaction not confirmed after {timeout} seconds, check on explorer',
        'wallet_failed': 'Wallet failed: {error}',
        'choose_action': 'Choose action (1: PHRS → WPHRS | 2: WPHRS → PHRS | 3: Wrap | Unwrap): ',
        'wrap_only': 'Wrap PHRS → WPHRS',
        'unwrap_only': 'Unwrap WPHRS → PHRS',
        'wrap_and_unwrap': 'Wrap then Unwrap',
        'invalid_action': 'Invalid action! Please choose 1, 2, or 3.',
        'approving': 'Approving WPHRS for {spender}...',
        'approval_success': 'WPHRS approval successful!',
    }
}

# Display functions
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}", flush=True)
    print(f"{color}│{padded_text}│{Style.RESET_ALL}", flush=True)
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}", flush=True)

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}", flush=True)

def print_message(message: str, color=Fore.YELLOW):
    print(f"{color}{message}{Style.RESET_ALL}", flush=True)

def print_wallets_summary(private_keys: list, language: str = 'en'):
    print_border(
        LANG[language]['processing_wallets'].format(count=len(private_keys)),
        Fore.MAGENTA
    )
    print()

def display_token_balances(w3: Web3, address: str, language: str = 'en'):
    phrs_balance = check_balance(w3, address, None, language)
    wphrs_balance = check_balance(w3, address, TOKENS["WPHRS"]["address"], language)
    print_message(f"    - {LANG[language]['balance'].format(phrs=phrs_balance, wphrs=wphrs_balance)}", Fore.YELLOW)

def display_all_wallets_balances(w3: Web3, private_keys: List[str], language: str = 'en'):
    print_border(LANG[language]['balance_info'], Fore.CYAN)
    print(f"{Fore.CYAN}  Wallet | {'PHRS':<10} | {'WPHRS':<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * 6} | {'-' * 10} | {'-' * 10}{Style.RESET_ALL}")
    
    for i, key in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        phrs_balance = check_balance(w3, address, None, language)
        wphrs_balance = check_balance(w3, address, TOKENS["WPHRS"]["address"], language)
        print(f"{Fore.YELLOW}  {i:<6} | {phrs_balance:>10.6f} | {wphrs_balance:>10.6f}{Style.RESET_ALL}")
    
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

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}", flush=True)
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
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key}{Style.RESET_ALL}", flush=True)
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}", flush=True)
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}", flush=True)
        sys.exit(1)

def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['no_proxies']}{Style.RESET_ALL}", flush=True)
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
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['no_proxies']}{Style.RESET_ALL}", flush=True)
            return []
        
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}", flush=True)
        return proxies
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}", flush=True)
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
                    print_message(f"⚠ {LANG[language]['invalid_proxy'].format(proxy=proxy)}", Fore.YELLOW)
                    return LANG[language]['unknown']
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}", Fore.YELLOW)
                    return LANG[language]['unknown']
        else:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}", Fore.YELLOW)
                    return LANG[language]['unknown']
    except Exception as e:
        print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}", Fore.YELLOW)
        return LANG[language]['unknown']

def connect_web3(language: str = 'en'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if not w3.is_connected():
            print(f"{Fore.RED}  ✖ {LANG[language]['connect_error']}{Style.RESET_ALL}", flush=True)
            sys.exit(1)
        print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} │ Chain ID: {w3.eth.chain_id}{Style.RESET_ALL}", flush=True)
        return w3
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}", flush=True)
        sys.exit(1)

async def wait_for_receipt(w3: Web3, tx_hash: str, max_wait_time: int = CONFIG["TIMEOUT"], language: str = 'en'):
    start_time = asyncio.get_event_loop().time()
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt
        except Exception as e:
            # Suppress "Transaction with hash ... not found" errors
            if "not found" not in str(e).lower():
                print_message(f"⚠ Lỗi khi lấy receipt: {str(e)}", Fore.YELLOW)
        
        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time > max_wait_time:
            return None
        
        await asyncio.sleep(5)

def check_balance(w3: Web3, address: str, token_address=None, language: str = 'en') -> float:
    if token_address is None:  # Native PHRS
        try:
            balance = w3.eth.get_balance(address)
            return float(w3.from_wei(balance, 'ether'))
        except Exception as e:
            print_message(f"⚠ {LANG[language]['error']}: {str(e)}", Fore.YELLOW)
            return -1
    else:
        try:
            token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=WPHRS_ABI)
            balance = token_contract.functions.balanceOf(address).call()
            decimals = TOKENS["WPHRS"]["decimals"]
            return balance / (10 ** decimals)
        except Exception as e:
            print_message(f"⚠ {LANG[language]['error']}: {str(e)}", Fore.YELLOW)
            return -1

class WPHRSSwap:
    def __init__(self, w3: Web3, private_key: str):
        self.w3 = w3
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Pharos Testnet")
        
        if not is_valid_private_key(private_key):
            raise ValueError("Invalid PRIVATE_KEY format")
        
        self.account: LocalAccount = Account.from_key(private_key)
        self.address = self.account.address
        self.wphrs_contract = self.w3.eth.contract(address=WPHRS_ADDRESS, abi=WPHRS_ABI)

    def get_gas_params(self, multiplier=CONFIG["GAS_MULTIPLIER"]):
        for attempt in range(CONFIG["MAX_RETRIES"]):
            try:
                latest_block = self.w3.eth.get_block('latest')
                base_fee = latest_block['baseFeePerGas']
                priority_fee = self.w3.eth.max_priority_fee
                max_fee_per_gas = int(base_fee * multiplier + priority_fee)
                return {
                    'maxFeePerGas': max_fee_per_gas,
                    'maxPriorityFeePerGas': priority_fee
                }
            except Exception as e:
                if attempt < CONFIG["MAX_RETRIES"] - 1:
                    print_message(f"⚠ Error getting gas parameters (attempt {attempt+1}/{CONFIG['MAX_RETRIES']}): {str(e)}. Retrying in {CONFIG['RETRY_DELAY']} seconds...", Fore.YELLOW)
                    time.sleep(CONFIG["RETRY_DELAY"])
                else:
                    raise Exception(f"Failed to get gas parameters after {CONFIG['MAX_RETRIES']} attempts: {str(e)}")

    async def approve_token(self, amount_in_phrs: float, proxy: str, language: str) -> bool:
        if not CONFIG["REQUIRE_APPROVAL"]:
            return True  # Skip approval if not required
        
        token_symbol = "WPHRS"
        token_decimals = TOKENS[token_symbol]["decimals"]
        amount_in_wei = int(amount_in_phrs * (10 ** token_decimals))
        
        allowance = self.wphrs_contract.functions.allowance(self.address, CONFIG["APPROVE_SPENDER"]).call()
        if allowance >= amount_in_wei:
            print_message(f"    - Approval skipped (sufficient allowance: {allowance / (10 ** token_decimals):.6f} {token_symbol})", Fore.YELLOW)
            return True
        
        nonce = self.w3.eth.get_transaction_count(self.address, 'pending')
        tx = self.wphrs_contract.functions.approve(
            CONFIG["APPROVE_SPENDER"],
            amount_in_wei
        ).build_transaction({
            'from': self.address,
            'nonce': nonce,
        })
        
        try:
            gas_estimate = self.w3.eth.estimate_gas(tx)
            gas_limit = int(gas_estimate * 1.2)
        except Exception as e:
            gas_limit = CONFIG["DEFAULT_GAS_LIMIT"]
            print_message(f"⚠ Gas estimation failed for approval: {str(e)}. Using default gas: {gas_limit}", Fore.YELLOW)
        
        tx.update({
            'gas': gas_limit,
            **self.get_gas_params()
        })
        
        for attempt in range(CONFIG["MAX_RETRIES"]):
            try:
                signed_tx = self.account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash_hex = tx_hash.hex()
                tx_link = f"{EXPLORER_URL}{tx_hash_hex}"
                print_message(f"Approval transaction sent: {tx_link}", Fore.YELLOW)
                
                receipt = await wait_for_receipt(self.w3, tx_hash, max_wait_time=CONFIG["TIMEOUT"], language=language)
                if receipt is None:
                    print_message(f"{LANG[language]['timeout'].format(timeout=CONFIG['TIMEOUT'])} - Tx: {tx_link}", Fore.YELLOW)
                    return False
                elif receipt.status == 1:
                    total_cost = self.w3.from_wei(receipt['gasUsed'] * tx['maxFeePerGas'], 'ether')
                    print_message(f"✔ {LANG[language]['approval_success']} │ Tx: {tx_link}", Fore.GREEN)
                    print_message(f"    - {LANG[language]['block']}: {receipt['blockNumber']}", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['gas']}: {receipt['gasUsed']}", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['gas_price']}: {self.w3.from_wei(tx['maxFeePerGas'], 'gwei'):.6f} Gwei", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['total_cost']}: {total_cost:.12f} PHRS", Fore.YELLOW)
                    return True
                else:
                    print_message(f"✖ Approval failed: {tx_link}", Fore.RED)
                    return False
            except Exception as e:
                if attempt < CONFIG["MAX_RETRIES"] - 1:
                    print_message(f"✖ Approval failed (attempt {attempt+1}/{CONFIG['MAX_RETRIES']}): {str(e)}. Retrying in {CONFIG['RETRY_DELAY']} seconds...", Fore.RED)
                    await asyncio.sleep(CONFIG["RETRY_DELAY"])
                    nonce = self.w3.eth.get_transaction_count(self.address, 'pending')
                    tx['nonce'] = nonce
                    continue
                print_message(f"✖ Approval failed after {CONFIG['MAX_RETRIES']} attempts: {str(e)}. Check: {tx_link if 'tx_hash_hex' in locals() else 'Not sent'}", Fore.RED)
                return False
        return False

    async def wrap_phrs(self, amount_in_phrs: float, proxy: str, language: str) -> bool:
        print_message(f"> {LANG[language]['checking_balance']}", Fore.CYAN)
        phrs_balance = check_balance(self.w3, self.address, None, language)
        wphrs_balance = check_balance(self.w3, self.address, TOKENS["WPHRS"]["address"], language)
        print_message(f"    - {LANG[language]['balance'].format(phrs=phrs_balance, wphrs=wphrs_balance)}", Fore.YELLOW)
        
        if phrs_balance < amount_in_phrs + CONFIG["MINIMUM_BALANCE"]:
            print_message(f"✖ {LANG[language]['insufficient_balance'].format(balance=phrs_balance, symbol='PHRS', required=amount_in_phrs + CONFIG['MINIMUM_BALANCE'])}", Fore.RED)
            return False
        
        print_message(f"> {LANG[language]['preparing_tx']}", Fore.CYAN)
        amount_in_wei = self.w3.to_wei(amount_in_phrs, 'ether')
        
        nonce = self.w3.eth.get_transaction_count(self.address, 'pending')
        tx = self.wphrs_contract.functions.deposit().build_transaction({
            'from': self.address,
            'value': amount_in_wei,
            'nonce': nonce,
        })
        
        try:
            gas_estimate = self.w3.eth.estimate_gas(tx)
            gas_limit = int(gas_estimate * 1.2)
            print_message(f"    - Gas ước lượng: {gas_estimate} | Gas limit sử dụng: {gas_limit}", Fore.YELLOW)
        except Exception as e:
            gas_limit = CONFIG["DEFAULT_GAS_LIMIT"]
            print_message(f"⚠ {LANG[language]['gas_estimation_failed'].format(error=str(e))}. {LANG[language]['default_gas_used'].format(gas=gas_limit)}", Fore.YELLOW)
        
        tx.update({
            'gas': gas_limit,
            **self.get_gas_params()
        })
        
        for attempt in range(CONFIG["MAX_RETRIES"]):
            try:
                print_message(f"> {LANG[language]['sending_tx']}", Fore.CYAN)
                signed_tx = self.account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash_hex = tx_hash.hex()
                tx_link = f"{EXPLORER_URL}{tx_hash_hex}"
                print_message(f"Wrap transaction sent: {tx_link}", Fore.YELLOW)
                
                receipt = await wait_for_receipt(self.w3, tx_hash, max_wait_time=CONFIG["TIMEOUT"], language=language)
                if receipt is None:
                    print_message(f"{LANG[language]['timeout'].format(timeout=CONFIG['TIMEOUT'])} - Tx: {tx_link}", Fore.YELLOW)
                    return False
                elif receipt.status == 1:
                    total_cost = self.w3.from_wei(receipt['gasUsed'] * tx['maxFeePerGas'], 'ether')
                    print_message(f"✔ {LANG[language]['wrap_success'].format(amount=amount_in_phrs)} │ Tx: {tx_link}", Fore.GREEN)
                    print_message(f"    - {LANG[language]['address']}: {self.address}", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['block']}: {receipt['blockNumber']}", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['gas']}: {receipt['gasUsed']}", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['gas_price']}: {self.w3.from_wei(tx['maxFeePerGas'], 'gwei'):.6f} Gwei", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['total_cost']}: {total_cost:.12f} PHRS", Fore.YELLOW)
                    display_token_balances(self.w3, self.address, language)
                    return True
                else:
                    try:
                        tx_data = self.w3.eth.get_transaction(tx_hash)
                        self.w3.eth.call(tx_data, block_number=receipt.blockNumber)
                    except Exception as revert_error:
                        print_message(f"✖ {LANG[language]['tx_rejected'].format(error=str(revert_error))} │ Tx: {tx_link}", Fore.RED)
                        return False
            except Exception as e:
                if attempt < CONFIG["MAX_RETRIES"] - 1:
                    print_message(f"✖ Wrap failed (attempt {attempt+1}/{CONFIG['MAX_RETRIES']}): {str(e)}. Retrying in {CONFIG['RETRY_DELAY']} seconds...", Fore.RED)
                    await asyncio.sleep(CONFIG["RETRY_DELAY"])
                    nonce = self.w3.eth.get_transaction_count(self.address, 'pending')
                    tx['nonce'] = nonce
                    continue
                print_message(f"✖ Wrap failed after {CONFIG['MAX_RETRIES']} attempts: {str(e)}. Check: {tx_link if 'tx_hash_hex' in locals() else 'Not sent'}", Fore.RED)
                return False
        return False

    async def unwrap_wphrs(self, amount_in_phrs: float, proxy: str, language: str) -> bool:
        print_message(f"> {LANG[language]['checking_balance']}", Fore.CYAN)
        phrs_balance = check_balance(self.w3, self.address, None, language)
        wphrs_balance = check_balance(self.w3, self.address, TOKENS["WPHRS"]["address"], language)
        print_message(f"    - {LANG[language]['balance'].format(phrs=phrs_balance, wphrs=wphrs_balance)}", Fore.YELLOW)
        
        if phrs_balance < CONFIG["MINIMUM_BALANCE"]:
            print_message(f"✖ {LANG[language]['insufficient_balance'].format(balance=phrs_balance, symbol='PHRS', required=CONFIG['MINIMUM_BALANCE'])}", Fore.RED)
            return False
        if wphrs_balance < amount_in_phrs:
            print_message(f"✖ {LANG[language]['insufficient_balance'].format(balance=wphrs_balance, symbol='WPHRS', required=amount_in_phrs)}", Fore.RED)
            return False
        
        if CONFIG["REQUIRE_APPROVAL"]:
            print_message(f"> {LANG[language]['approving'].format(spender=CONFIG['APPROVE_SPENDER'])}", Fore.CYAN)
            if not await self.approve_token(amount_in_phrs, proxy, language):
                return False
        
        print_message(f"> {LANG[language]['preparing_tx']}", Fore.CYAN)
        amount_in_wei = self.w3.to_wei(amount_in_phrs, 'ether')
        
        nonce = self.w3.eth.get_transaction_count(self.address, 'pending')
        tx = self.wphrs_contract.functions.withdraw(amount_in_wei).build_transaction({
            'from': self.address,
            'nonce': nonce,
        })
        
        try:
            gas_estimate = self.w3.eth.estimate_gas(tx)
            gas_limit = int(gas_estimate * 1.2)
            print_message(f"    - Gas ước lượng: {gas_estimate} | Gas limit sử dụng: {gas_limit}", Fore.YELLOW)
        except Exception as e:
            gas_limit = CONFIG["DEFAULT_GAS_LIMIT"]
            print_message(f"⚠ {LANG[language]['gas_estimation_failed'].format(error=str(e))}. {LANG[language]['default_gas_used'].format(gas=gas_limit)}", Fore.YELLOW)
        
        tx.update({
            'gas': gas_limit,
            **self.get_gas_params()
        })
        
        for attempt in range(CONFIG["MAX_RETRIES"]):
            try:
                print_message(f"> {LANG[language]['sending_tx']}", Fore.CYAN)
                signed_tx = self.account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash_hex = tx_hash.hex()
                tx_link = f"{EXPLORER_URL}{tx_hash_hex}"
                print_message(f"Unwrap transaction sent: {tx_link}", Fore.YELLOW)
                
                receipt = await wait_for_receipt(self.w3, tx_hash, max_wait_time=CONFIG["TIMEOUT"], language=language)
                if receipt is None:
                    print_message(f"{LANG[language]['timeout'].format(timeout=CONFIG['TIMEOUT'])} - Tx: {tx_link}", Fore.YELLOW)
                    return False
                elif receipt.status == 1:
                    total_cost = self.w3.from_wei(receipt['gasUsed'] * tx['maxFeePerGas'], 'ether')
                    print_message(f"✔ {LANG[language]['unwrap_success'].format(amount=amount_in_phrs)} │ Tx: {tx_link}", Fore.GREEN)
                    print_message(f"    - {LANG[language]['address']}: {self.address}", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['block']}: {receipt['blockNumber']}", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['gas']}: {receipt['gasUsed']}", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['gas_price']}: {self.w3.from_wei(tx['maxFeePerGas'], 'gwei'):.6f} Gwei", Fore.YELLOW)
                    print_message(f"    - {LANG[language]['total_cost']}: {total_cost:.12f} PHRS", Fore.YELLOW)
                    display_token_balances(self.w3, self.address, language)
                    return True
                else:
                    try:
                        tx_data = self.w3.eth.get_transaction(tx_hash)
                        self.w3.eth.call(tx_data, block_number=receipt.blockNumber)
                    except Exception as revert_error:
                        print_message(f"✖ {LANG[language]['tx_rejected'].format(error=str(revert_error))} │ Tx: {tx_link}", Fore.RED)
                        return False
            except Exception as e:
                if attempt < CONFIG["MAX_RETRIES"] - 1:
                    print_message(f"✖ Unwrap failed (attempt {attempt+1}/{CONFIG['MAX_RETRIES']}): {str(e)}. Retrying in {CONFIG['RETRY_DELAY']} seconds...", Fore.RED)
                    await asyncio.sleep(CONFIG["RETRY_DELAY"])
                    nonce = self.w3.eth.get_transaction_count(self.address, 'pending')
                    tx['nonce'] = nonce
                    continue
                print_message(f"✖ Unwrap failed after {CONFIG['MAX_RETRIES']} attempts: {str(e)}. Check: {tx_link if 'tx_hash_hex' in locals() else 'Not sent'}", Fore.RED)
                return False
        return False

async def process_wallet(index: int, private_key: str, proxy: str, w3: Web3, amount: float, cycles: int, action: str, language: str) -> int:
    total_wallets = CONFIG.get('TOTAL_WALLETS', 1)
    
    account = Account.from_key(private_key)
    print_message(f"{LANG[language]['address']}: {account.address}", Fore.YELLOW)
    print()
    
    successful_txs = 0
    total_txs = cycles if action in ['1', '2'] else cycles * 2
    
    try:
        swap = WPHRSSwap(w3, private_key)
        for cycle in range(1, cycles + 1):
            print_message(f"> Cycle {cycle}/{cycles}", Fore.CYAN)
            
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print_message(f"🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}", Fore.CYAN)
            
            if action == '1':  # Wrap only
                print_message(f"> {LANG[language]['wrap_only']}", Fore.CYAN)
                if await swap.wrap_phrs(amount, proxy, language):
                    successful_txs += 1
            
            elif action == '2':  # Unwrap only
                print_message(f"> {LANG[language]['unwrap_only']}", Fore.CYAN)
                if await swap.unwrap_wphrs(amount, proxy, language):
                    successful_txs += 1
            
            elif action == '3':  # Wrap then Unwrap
                print_message(f"> {LANG[language]['wrap_only']}", Fore.CYAN)
                if await swap.wrap_phrs(amount, proxy, language):
                    successful_txs += 1
                
                print()
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_SWAPS'][0], CONFIG['PAUSE_BETWEEN_SWAPS'][1])
                print_message(f"ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
                print()
                
                print_message(f"> {LANG[language]['unwrap_only']}", Fore.CYAN)
                if await swap.unwrap_wphrs(amount, proxy, language):
                    successful_txs += 1
            
            if cycle < cycles:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_SWAPS'][0], CONFIG['PAUSE_BETWEEN_SWAPS'][1])
                print_message(f"ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
            print()
        
        print_separator(Fore.GREEN if successful_txs > 0 else Fore.RED)
        return successful_txs
    except Exception as e:
        print_message(f"✖ {LANG[language]['wallet_failed'].format(error=str(e))}", Fore.RED)
        print_message(f"    - Chi tiết lỗi: {traceback.format_exc()}", Fore.RED)
        print_separator(Fore.RED)
        return 0

async def run_wrap(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()
    
    private_keys = load_private_keys('pvkey.txt', language)
    proxies = load_proxies('proxies.txt', language)
    random.shuffle(private_keys)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}", flush=True)
    print()
    
    if not private_keys:
        return
    
    w3 = connect_web3(language)
    print()
    
    # Display balance table for all wallets
    display_all_wallets_balances(w3, private_keys, language)
    print_separator()
    
    while True:
        print_border(LANG[language]['choose_action'], Fore.YELLOW)
        action = input(f"{Fore.GREEN}➤ {Style.RESET_ALL}").strip()
        if action in ['1', '2', '3']:
            break
        print(f"{Fore.RED}✖ {LANG[language]['invalid_action']}{Style.RESET_ALL}", flush=True)
    
    while True:
        print_border(LANG[language]['input_amount'], Fore.YELLOW)
        try:
            amount = float(input(f"{Fore.GREEN}➤ {Style.RESET_ALL}"))
            if 0.000001 <= amount <= 999:
                break
            print(f"{Fore.RED}✖ {LANG[language]['input_error']}{Style.RESET_ALL}", flush=True)
        except ValueError:
            print(f"{Fore.RED}✖ {LANG[language]['input_error']}{Style.RESET_ALL}", flush=True)
    
    while True:
        try:
            print_border(LANG[language]['cycles'], Fore.YELLOW)
            cycles = input(f"{Fore.GREEN}➤ {'Nhập số (mặc định 1): ' if language == 'vi' else 'Enter number (default 1): '}{Style.RESET_ALL}")
            cycles = int(cycles) if cycles else 1
            if cycles > 0:
                break
            print(f"{Fore.RED}✖ {'Số phải lớn hơn 0 / Number must be > 0'}{Style.RESET_ALL}", flush=True)
        except ValueError:
            print(f"{Fore.RED}✖ {'Nhập số hợp lệ / Enter a valid number'}{Style.RESET_ALL}", flush=True)
    
    print_separator()
    total_txs = len(private_keys) * cycles if action in ['1', '2'] else len(private_keys) * cycles * 2
    successful_txs = 0
    CONFIG['TOTAL_WALLETS'] = len(private_keys)
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], len(private_keys))
    
    # Display wallets summary before processing
    print_wallets_summary(private_keys, language)
    
    async def limited_task(index, private_key, proxy):
        nonlocal successful_txs
        async with semaphore:
            result = await process_wallet(index, private_key, proxy, w3, amount, cycles, action, language)
            successful_txs += result
            if index < len(private_keys) - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                print_message(f"ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
    
    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    tasks = []
    for i, private_key in enumerate(private_keys):
        proxy = proxies[i % len(proxies)] if proxies else None
        tasks.append(limited_task(i, private_key, proxy))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print_message(f"✖ Lỗi xử lý ví {i+1}: {str(result)}", Fore.RED)
    
    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_txs, total=total_txs)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_wrap('vi'))
