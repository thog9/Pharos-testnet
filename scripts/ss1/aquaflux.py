import os
import sys
import asyncio
import random
import json
import time
import re
from web3 import Web3
from eth_utils import to_hex
from eth_account import Account
from eth_account.messages import encode_defunct
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from colorama import init, Fore, Style

# Khởi tạo colorama
init(autoreset=True)

# Constants
NETWORK_URL = "https://testnet.dplabs-internal.com"
CHAIN_ID = 688688
EXPLORER_URL = "https://testnet.pharosscan.xyz/tx/0x"
AQUAFLUX_NFT_ADDRESS = "0xCc8cF44E196CaB28DBA2d514dc7353af0eFb370E"
BASE_API = "https://api.aquaflux.pro/api/v1"
SYMBOL = "PHRS"
BORDER_WIDTH = 80
CONFIG = {
    "PAUSE_BETWEEN": [10, 20],
    "MAX_CONCURRENT": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.001
}

# Contract ABI
AQUAFLUX_CONTRACT_ABI = [
    {
        "type": "function",
        "name": "claimTokens",
        "stateMutability": "nonpayable",
        "inputs": [],
        "outputs": []
    },
    {
        "type": "function",
        "name": "combineCS",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "outputs": []
    },
    {
        "type": "function",
        "name": "combinePC",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "outputs": []
    },
    {
        "type": "function",
        "name": "combinePS",
        "stateMutability": "nonpayable",
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "outputs": []
    },
    {
        "type": "function",
        "name": "hasClaimedStandardNFT",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "hasClaimedPremiumNFT",
        "stateMutability": "view",
        "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}]
    },
    {
        "type": "function",
        "name": "mint",
        "stateMutability": "nonpayable",
        "inputs": [
            {"internalType": "enum AquafluxNFT.NFTType", "name": "nftType", "type": "uint8"},
            {"internalType": "uint256", "name": "expiresAt", "type": "uint256"},
            {"internalType": "bytes", "name": "signature", "type": "bytes"}
        ],
        "outputs": []
    }
]

# Từ ngôn ngữ
LNG = {
    'vi': {
        'title': '✨ AQUAFLUX NFT BOT - PHAROS TESTNET ✨',
        'info': 'ℹ Thông tin: Tìm thấy {count} ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt!',
        'select_action': 'CHỌN HÀNH ĐỘNG',
        'claim_tokens': '1. Claim Tokens',
        'combine_tokens': '2. Combine Tokens',
        'mint_nft': '3. Mint NFT',
        'select_nft_type': 'CHỌN LOẠI NFT',
        'standard_nft': '1. Standard NFT',
        'premium_nft': '2. Premium NFT',
        'choice_prompt': 'Nhập lựa chọn (1/2/3): ',
        'nft_choice_prompt': 'Nhập lựa chọn (1/2): ',
        'start_processing': 'BẮT ĐẦU {action} CHO {wallet_count} VÍ',
        'processing_wallet': 'Xử lý ví {index}: {address}',
        'balance_check': 'Số dư PHRS',
        'insufficient_balance': 'Số dư không đủ (cần {required:.6f} PHRS)',
        'login_success': '> Đăng nhập ví thành công!',
        'login_failed': 'Đăng nhập ví thất bại: {error}',
        'binding_check': 'Kiểm tra liên kết X...',
        'not_bound': 'Chưa liên kết X, không thể mint Premium NFT',
        'action_claim': 'Claim tokens',
        'action_combine': 'Combine tokens',
        'action_mint': 'Mint {nft_type}',
        'success': '✔ {action} thành công! Tx: {tx_link}',
        'failure': '✘ Thất bại: {error} - Tx: {tx_link}',
        'timeout': '✘ Giao dịch không xác nhận sau {timeout}s, kiểm tra: {tx_link}',
        'sender': ' - Địa chỉ: {address}',
        'block': 'Khối: {block}',
        'balance': 'Số dư PHRS',
        'pausing': 'Tạm dừng {seconds}s...',
        'completed': '✔ HOÀN THÀNH! {txs_txs}/{tx_total} GIAO DỊCH THÀNH CÔNG',
        'error': '✘ Lỗi: {error}',
        'invalid_choice': 'Lựa chọn không hợp lệ!',
        'connect_success': '✔ Thành công: Kết nối mạng Pharos Testnet | Chain ID: {chain_id} | RPC: {rpc}',
        'connect_error': '✘ Không thể kết nối RPC',
        'pvkey_not_found': '✘ File pvkey.txt không tồn tại',
        'pvkey_empty': '✘ Không tìm thấy private key hợp lệ',
        'pvkey_error': '✘ Đọc pvkey.txt thất bại: {error}',
        'proxy_error': '✘ Đọc proxies.txt thất bại: {error}',
        'already_minted': '{nft_type} đã được mint',
        'already_combined': 'Token đã được combine',
        'using_proxy': '🔄 🔄 Dùng Proxy - [{proxy}] với IP công khai - [{ip}]'
    },
    'en': {
        'title': '✨ AQUAFLUX NFT BOT - PHAROS TESTNET ✨',
        'info': 'ℹ Info: Found {count} wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt!',
        'select_action': 'SELECT ACTION',
        'claim_tokens': '1. Claim Tokens',
        'combine_tokens': '2. Combine Tokens',
        'mint_nft': '3. Mint NFT',
        'select_nft_type': 'SELECT NFT TYPE',
        'standard_nft': '1. Standard NFT',
        'premium_nft': '2. Premium NFT',
        'choice_prompt': 'Enter choice (1/2/3): ',
        'nft_choice_prompt': 'Enter choice (1/2): ',
        'start_processing': 'STARTING {action} FOR {wallet_count} WALLETS',
        'processing_wallet': 'Processing wallet {index}: {address}',
        'balance_check': 'Balance PHRS',
        'insufficient_balance': 'Insufficient balance (need {required:.6f} PHRS)',
        'login_success': '> Wallet login successful!',
        'login_failed': 'Wallet login failed: {error}',
        'binding_check': 'Checking X binding...',
        'not_bound': 'X not bound, cannot mint Premium NFT',
        'action_claim': 'Claim tokens',
        'action_combine': 'Combine tokens',
        'action_mint': 'Mint {nft_type}',
        'success': '✔ {action} successful! Tx: {tx_link}',
        'failure': '✘ Failed: {error} - Tx: {tx_link}',
        'timeout': '✘ Transaction not confirmed after {timeout}s, check: {tx_link}',
        'sender': ' - Address: {address}',
        'block': 'Block: {block}',
        'balance': 'Balance PHRS',
        'pausing': 'Pausing {seconds}s...',
        'completed': '✔ COMPLETED! {txs_txs}/{tx_total} TRANSACTIONS SUCCESSFUL',
        'error': '✘ Error: {error}',
        'invalid_choice': 'Invalid choice!',
        'connect_success': '✔ Success: Connected to Pharos Testnet | Chain ID: {chain_id} | RPC: {rpc}',
        'connect_error': '✘ Cannot connect to RPC',
        'pvkey_not_found': '✘ File pvkey.txt not found',
        'pvkey_empty': '✘ No valid private keys found',
        'pvkey_error': '✘ Failed to read pvkey.txt: {error}',
        'proxy_error': '✘ Failed to read proxies.txt: {error}',
        'already_minted': '{nft_type} already minted',
        'already_combined': 'Tokens already combined',
        'using_proxy': '🔄 🔄 Using Proxy - [{proxy}] with public IP - [{ip}]'
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
    print(f"{color}  {message}{Style.RESET_ALL}")

def print_wallets_summary(count: int, language: str = 'vi'):
    print_message(LNG[language]['info'].format(count=count), Fore.YELLOW)

def display_all_wallets_balances(w3: Web3, private_keys: list, language: str = 'vi'):
    print_border(LNG[language]['balance'], Fore.CYAN)
    print(f"{Fore.CYAN}  Wallet | {SYMBOL}{Style.RESET_ALL}")
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
                        print(f"{Fore.YELLOW}  {LNG[language]['error'].format(error=f'Line {i}: Invalid private key - {key}')}{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  {LNG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  {LNG[language]['pvkey_error'].format(error=str(e))}{Style.RESET_ALL}")
        sys.exit(1)

def load_proxies(file_path: str = "proxies.txt", language: str = 'vi') -> list:
    try:
        if not os.path.exists(file_path):
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not proxy.startswith('#'):
                    proxies.append(proxy)
        
        if proxies:
            print_message(LNG[language]['found_proxies'].format(count=len(proxies)), Fore.YELLOW)
        return proxies
    except Exception as e:
        print(f"{Fore.RED}  {LNG[language]['proxy_error'].format(error=str(e))}{Style.RESET_ALL}")
        return []

def extract_ip_from_proxy(proxy: str) -> str:
    # Trích xuất IP từ proxy URL (hỗ trợ socks5, http, https)
    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$', proxy)
    return match.group(1) if match else proxy

def connect_web3(language: str = 'vi'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if w3.is_connected():
            print(f"{Fore.GREEN}  {LNG[language]['connect_success'].format(chain_id=w3.eth.chain_id, rpc=NETWORK_URL)}{Style.RESET_ALL}")
            return w3
        else:
            print(f"{Fore.RED}  {LNG[language]['connect_error']}{Style.RESET_ALL}")
            sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}  {LNG[language]['error'].format(error=f'Web3 connection failed: {str(e)}')}{Style.RESET_ALL}")
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
        print(f"{Fore.YELLOW}  {LNG[language]['error'].format(error=str(e))}{Style.RESET_ALL}")
        return -1

class AquaFlux:
    def __init__(self):
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}

    def get_next_proxy_for_account(self, address: str):
        if not self.proxies:
            return None
        if address not in self.account_proxies:
            proxy = self.proxies[self.proxy_index % len(self.proxies)]
            self.account_proxies[address] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[address]

    async def wallet_login(self, account: str, address: str, proxy: str, language: str = 'vi'):
        url = f"{BASE_API}/users/wallet-login"
        timestamp = int(time.time()) * 1000
        message = f"Sign in to AquaFlux with timestamp: {timestamp}"
        encoded_message = encode_defunct(text=message)
        signed_message = Account.sign_message(encoded_message, private_key=account)
        signature = to_hex(signed_message.signature)
        payload = {
            "address": address,
            "message": message,
            "signature": signature
        }
        data = json.dumps(payload)
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://playground.aquaflux.pro",
            "Referer": "https://playground.aquaflux.pro/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(CONFIG['MAX_RETRIES']):
            try:
                if proxy:
                    connector = ProxyConnector.from_url(proxy)
                    async with ClientSession(connector=connector) as session:
                        async with session.post(url, headers=headers, data=data) as response:
                            response.raise_for_status()
                            result = await response.json()
                            self.access_tokens[address] = result["data"]["accessToken"]
                            print_message(LNG[language]['login_success'], Fore.GREEN)
                            return True
                else:
                    async with ClientSession() as session:
                        async with session.post(url, headers=headers, data=data) as response:
                            response.raise_for_status()
                            result = await response.json()
                            self.access_tokens[address] = result["data"]["accessToken"]
                            print_message(LNG[language]['login_success'], Fore.GREEN)
                            return True
            except Exception as e:
                if attempt < CONFIG['MAX_RETRIES'] - 1:
                    await asyncio.sleep(5)
                    continue
                print_message(LNG[language]['login_failed'].format(error=str(e)), Fore.RED)
                return False

    async def check_binding_status(self, address: str, proxy: str, language: str = 'vi'):
        url = f"{BASE_API}/users/twitter/binding-status"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://playground.aquaflux.pro",
            "Referer": "https://playground.aquaflux.pro/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {self.access_tokens.get(address, '')}"
        }
        for attempt in range(CONFIG['MAX_RETRIES']):
            try:
                if proxy:
                    connector = ProxyConnector.from_url(proxy)
                    async with ClientSession(connector=connector) as session:
                        async with session.get(url, headers=headers) as response:
                            response.raise_for_status()
                            return await response.json()
                else:
                    async with ClientSession() as session:
                        async with session.get(url, headers=headers) as response:
                            response.raise_for_status()
                            return await response.json()
            except Exception as e:
                if attempt < CONFIG['MAX_RETRIES'] - 1:
                    await asyncio.sleep(5)
                    continue
                print_message(LNG[language]['error'].format(error=f'Failed to check X binding: {str(e)}'), Fore.RED)
                return None

    async def get_signature(self, address: str, nft_type: int, proxy: str, language: str = 'vi'):
        url = f"{BASE_API}/users/get-signature"
        data = json.dumps({"walletAddress": address, "requestedNftType": nft_type})
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://playground.aquaflux.pro",
            "Referer": "https://playground.aquaflux.pro/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {self.access_tokens.get(address, '')}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(CONFIG['MAX_RETRIES']):
            try:
                if proxy:
                    connector = ProxyConnector.from_url(proxy)
                    async with ClientSession(connector=connector) as session:
                        async with session.post(url, headers=headers, data=data) as response:
                            if response.status == 403:
                                result = await response.json()
                                err_msg = result.get("message", "Unknown error")
                                print_message(LNG[language]['error'].format(error=err_msg), Fore.RED)
                                return None
                            response.raise_for_status()
                            return await response.json()
                else:
                    async with ClientSession() as session:
                        async with session.post(url, headers=headers, data=data) as response:
                            if response.status == 403:
                                result = await response.json()
                                err_msg = result.get("message", "Unknown error")
                                print_message(LNG[language]['error'].format(error=err_msg), Fore.RED)
                                return None
                            response.raise_for_status()
                            return await response.json()
            except Exception as e:
                if attempt < CONFIG['MAX_RETRIES'] - 1:
                    await asyncio.sleep(5)
                    continue
                print_message(LNG[language]['error'].format(error=f'Failed to get signature: {str(e)}'), Fore.RED)
                return None

    async def perform_claim_tokens(self, w3: Web3, account: str, address: str, proxy: str, language: str = 'vi'):
        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(AQUAFLUX_NFT_ADDRESS), abi=AQUAFLUX_CONTRACT_ABI)
            claim_data = contract.functions.claimTokens()
            estimated_gas = claim_data.estimate_gas({"from": address})
            max_priority_fee = w3.to_wei(1, "gwei")
            max_fee = max_priority_fee
            claim_tx = claim_data.build_transaction({
                "from": Web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": w3.eth.get_transaction_count(address, "pending"),
                "chainId": w3.eth.chain_id,
            })
            signed_tx = w3.eth.account.sign_transaction(claim_tx, account)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=300, language=language)
            if receipt is None:
                print_message(LNG[language]['timeout'].format(timeout=300, tx_link=tx_link), Fore.YELLOW)
                return False
            elif receipt.status == 1:
                print_message(LNG[language]['success'].format(action=LNG[language]['action_claim'], tx_link=tx_link), Fore.GREEN)
                print_message(LNG[language]['sender'].format(address=address), Fore.YELLOW)
                return True
            else:
                print_message(LNG[language]['failure'].format(error='Transaction reverted', tx_link=tx_link), Fore.RED)
                return False
        except Exception as e:
            print_message(LNG[language]['failure'].format(error=str(e), tx_link=tx_link if 'tx_hash' in locals() else 'Not sent'), Fore.RED)
            return False

    async def perform_combine_tokens(self, w3: Web3, account: str, address: str, proxy: str, language: str = 'vi'):
        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(AQUAFLUX_NFT_ADDRESS), abi=AQUAFLUX_CONTRACT_ABI)
            combine_option = random.choice(["combineCS", "combinePC", "combinePS"])
            amount_to_wei = w3.to_wei(100, "ether")
            combine_data = getattr(contract.functions, combine_option)(amount_to_wei)
            estimated_gas = combine_data.estimate_gas({"from": address})
            max_priority_fee = w3.to_wei(1, "gwei")
            max_fee = max_priority_fee
            combine_tx = combine_data.build_transaction({
                "from": Web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": w3.eth.get_transaction_count(address, "pending"),
                "chainId": w3.eth.chain_id,
            })
            signed_tx = w3.eth.account.sign_transaction(combine_tx, account)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=300, language=language)
            if receipt is None:
                print_message(LNG[language]['timeout'].format(timeout=300, tx_link=tx_link), Fore.YELLOW)
                return False
            elif receipt.status == 1:
                print_message(LNG[language]['success'].format(action=LNG[language]['action_combine'], tx_link=tx_link), Fore.GREEN)
                print_message(LNG[language]['sender'].format(address=address), Fore.YELLOW)
                return True
            else:
                print_message(LNG[language]['failure'].format(error='Transaction reverted', tx_link=tx_link), Fore.RED)
                return False
        except Exception as e:
            print_message(LNG[language]['failure'].format(error=str(e), tx_link=tx_link if 'tx_hash' in locals() else 'Not sent'), Fore.RED)
            return False

    async def perform_mint_nft(self, w3: Web3, account: str, address: str, nft_type: str, proxy: str, language: str = 'vi'):
        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(AQUAFLUX_NFT_ADDRESS), abi=AQUAFLUX_CONTRACT_ABI)
            nft_type_id = 0 if nft_type == "Standard NFT" else 1
            if nft_type == "Premium NFT":
                print_message(LNG[language]['binding_check'], Fore.YELLOW)
                binding_status = await self.check_binding_status(address, proxy, language)
                if not binding_status or not binding_status.get("data", {}).get("isBound", False):
                    print_message(LNG[language]['not_bound'], Fore.RED)
                    return False
            
            status = await self.check_nft_status(w3, address, nft_type, language)
            if status:
                print_message(LNG[language]['already_minted'].format(nft_type=nft_type), Fore.YELLOW)
                return False
            
            data = await self.get_signature(address, nft_type_id, proxy, language)
            if not data:
                return False
            expires_at = data["data"]["expiresAt"]
            signature = data["data"]["signature"]
            mint_data = contract.functions.mint(nft_type_id, expires_at, signature)
            estimated_gas = mint_data.estimate_gas({"from": address})
            max_priority_fee = w3.to_wei(1, "gwei")
            max_fee = max_priority_fee
            mint_tx = mint_data.build_transaction({
                "from": Web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": w3.eth.get_transaction_count(address, "pending"),
                "chainId": w3.eth.chain_id,
            })
            signed_tx = w3.eth.account.sign_transaction(mint_tx, account)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=300, language=language)
            if receipt is None:
                print_message(LNG[language]['timeout'].format(timeout=300, tx_link=tx_link), Fore.YELLOW)
                return False
            elif receipt.status == 1:
                print_message(LNG[language]['success'].format(action=LNG[language]['action_mint'].format(nft_type=nft_type), tx_link=tx_link), Fore.GREEN)
                print_message(LNG[language]['sender'].format(address=address), Fore.YELLOW)
                return True
            else:
                print_message(LNG[language]['failure'].format(error='Transaction reverted', tx_link=tx_link), Fore.RED)
                return False
        except Exception as e:
            print_message(LNG[language]['failure'].format(error=str(e), tx_link=tx_link if 'tx_hash' in locals() else 'Not sent'), Fore.RED)
            return False

async def process_wallet(w3: Web3, aquaflux: AquaFlux, account: str, index: int, action: str, nft_type: str, proxy: str, semaphore: asyncio.Semaphore, language: str = 'vi'):
    async with semaphore:
        address = Account.from_key(account).address
        print_separator()
        
        if proxy:
            ip = extract_ip_from_proxy(proxy)
            print_message(LNG[language]['using_proxy'].format(proxy=proxy, ip=ip), Fore.CYAN)
        
        balance = check_balance(w3, address, language)
        if balance < CONFIG['MINIMUM_BALANCE']:
            print_message(LNG[language]['insufficient_balance'].format(required=CONFIG['MINIMUM_BALANCE']), Fore.RED)
            return False
        
        if action in ["claim_tokens", "mint_nft"]:
            if not await aquaflux.wallet_login(account, address, proxy, language):
                return False
        
        if action == "claim_tokens":
            success = await aquaflux.perform_claim_tokens(w3, account, address, proxy, language)
        elif action == "combine_tokens":
            success = await aquaflux.perform_combine_tokens(w3, account, address, proxy, language)
        elif action == "mint_nft":
            print_message(LNG[language]['action_mint'].format(nft_type=nft_type), Fore.YELLOW)
            success = await aquaflux.perform_mint_nft(w3, account, address, nft_type, proxy, language)
        else:
            success = False
        
        pause_duration = random.randint(CONFIG['PAUSE_BETWEEN'][0], CONFIG['PAUSE_BETWEEN'][1])
        print_message(LNG[language]['pausing'].format(seconds=pause_duration), Fore.YELLOW)
        await asyncio.sleep(pause_duration)
        return success

async def run_aquaflux(language: str = 'vi'):
    print()
    print_border(LNG[language]['title'], Fore.CYAN)
    print()
    
    aquaflux = AquaFlux()
    aquaflux.proxies = load_proxies(language=language)
    private_keys = load_private_keys(language=language)
    print_wallets_summary(len(private_keys), language)
    print()
    w3 = connect_web3(language)
    print()
    
    display_all_wallets_balances(w3, private_keys, language)
    
    print_border(LNG[language]['select_action'], Fore.CYAN)
    print_message(LNG[language]['claim_tokens'], Fore.YELLOW)
    print_message(LNG[language]['combine_tokens'], Fore.YELLOW)
    print_message(LNG[language]['mint_nft'], Fore.YELLOW)
    choice = input(f"{Fore.YELLOW}  {LNG[language]['choice_prompt']}{Style.RESET_ALL}").strip()
    
    action = None
    nft_type = None
    if choice == '1':
        action = "claim_tokens"
        action_name = LNG[language]['action_claim']
    elif choice == '2':
        action = "combine_tokens"
        action_name = LNG[language]['action_combine']
    elif choice == '3':
        action = "mint_nft"
        print_border(LNG[language]['select_nft_type'], Fore.CYAN)
        print_message(LNG[language]['standard_nft'], Fore.YELLOW)
        print_message(LNG[language]['premium_nft'], Fore.YELLOW)
        nft_choice = input(f"{Fore.YELLOW}  {LNG[language]['nft_choice_prompt']}{Style.RESET_ALL}").strip()
        if nft_choice == '1':
            nft_type = "Standard NFT"
            action_name = LNG[language]['action_mint'].format(nft_type=nft_type)
        elif nft_choice == '2':
            nft_type = "Premium NFT"
            action_name = LNG[language]['action_mint'].format(nft_type=nft_type)
        else:
            print_message(LNG[language]['invalid_choice'], Fore.RED)
            sys.exit(1)
    else:
        print_message(LNG[language]['invalid_choice'], Fore.RED)
        sys.exit(1)
    
    print_border(LNG[language]['start_processing'].format(action=action_name, wallet_count=len(private_keys)), Fore.CYAN)
    
    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENT'])
    tasks = []
    for i, key in enumerate(private_keys, 1):
        proxy = aquaflux.get_next_proxy_for_account(Account.from_key(key).address)
        tasks.append(process_wallet(w3, aquaflux, key, i, action, nft_type, proxy, semaphore, language))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success_count = sum(1 for r in results if r is True)
    print_border(LNG[language]['completed'].format(txs_txs=success_count, tx_total=len(private_keys)), Fore.GREEN)

if __name__ == "__main__":
    asyncio.run(run_aquaflux())
