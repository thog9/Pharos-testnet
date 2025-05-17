# Pharos Testnet Scripts 🚀

This collection of Python scripts empowers you to interact seamlessly with the Pharos Testnet, a cutting-edge blockchain test network for decentralized applications. The core script, main.py, offers an intuitive command-line interface (CLI) to perform a variety of operations, from deploying smart contracts to swapping tokens. Built with web3.py, these scripts leverage asynchronous execution and provide a modern, bilingual (English/Vietnamese) user experience.

🔗 Faucet: [Pharos Testnet Faucet](https://testnet.pharosnetwork.xyz/)

## ✨ Features Overview

### General Features

- **Multi-Account Support**: Reads private keys from `pvkey.txt` to perform actions across multiple accounts.
- **Colorful CLI**: Uses `colorama` for visually appealing output with colored text and borders.
- **Asynchronous Execution**: Built with `asyncio` for efficient blockchain interactions.
- **Error Handling**: Comprehensive error catching for blockchain transactions and RPC issues.
- **Bilingual Support**: Supports both English and Vietnamese output based on user selection.

### Included Scripts

1. **Daily Check-in**: Perform daily check-ins to earn rewards on the Pharos Testnet.
2. **Deploy Token Smart Contract**: Deploy an ERC20 token smart contract to the Pharos Testnet.
3. **Send ERC20 Tokens**: Transfer ERC20 tokens to random addresses or those listed in addressERC20.txt.
4. **Deploy NFT Smart Contract**: Deploy an NFT smart contract for creating unique digital assets.
5. **Send Transactions (TX)**: Send transactions to random addresses or those in address.txt.
6. **Swap Tokens**: Swap tokens (PHRS, USDC, USDT) via Zenith DEX on the Pharos Testnet.
7. **Add Liquidity**: Provide liquidity for token pairs (PHRS, USDC, USDT) on Zenith DEX.


## 🛠️ Prerequisites

Before running the scripts, ensure you have the following installed:

- Python 3.8+
- `pip` (Python package manager)
- **Dependencies**: Install via `pip install -r requirements.txt` (ensure `web3.py`, `colorama`, `asyncio`, `eth-account`, `aiohttp_socks` and `inquirer` are included).
- **pvkey.txt**: Add private keys (one per line) for wallet automation.
- **Pharos Testnet RPC**: Access via a public RPC endpoint (e.g., https://testnet.dplabs-internal.com or Pharos-specific RPC).
- **proxies.txt** (optional): Add proxy addresses for network requests, if needed.


## 📦 Installation

1. **Clone this repository:**
- Open cmd or Shell, then run the command:
```sh
git clone https://github.com/thog9/Pharos-testnet.git
```
```sh
cd Pharos-testnet
```
2. **Install Dependencies:**
- Open cmd or Shell, then run the command:
```sh
pip install -r requirements.txt
```
3. **Prepare Input Files:**
- Open the `pvkey.txt`: Add your private keys (one per line) in the root directory.
```sh
nano pvkey.txt 
```

- Create `address.txt`, `addressERC20.txt`, `contractNFT.txt`, `contractERC20.txt`, or `proxies.txt` for specific operations:
```sh
nano address.txt
nano addressERC20.txt
nano contractNFT.txt
nano contractERC20.txt
nano proxies.txt
```
4. **Run:**
- Open cmd or Shell, then run command:
```sh
python main.py
```
- Choose a language (Vietnamese/English).

## 📬 Contact
Connect with us for support or updates:

- **Telegram**: [thog099](https://t.me/thog099)
- **Channel**: [CHANNEL](https://t.me/thogairdrops)
- **Group**: [GROUP CHAT](https://t.me/thogchats)
- **X**: [Thog](https://x.com/thog099) 

----

## ☕ Support Us
Love these scripts? Fuel our work with a coffee!

🔗 BUYMECAFE: [BUY ME CAFE](https://buymecafe.vercel.app/)

