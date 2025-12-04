import os
import sys
import asyncio
from colorama import init, Fore, Style
import inquirer

# Khởi tạo colorama
init(autoreset=True)

# Độ rộng viền cố định
BORDER_WIDTH = 80

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."  # Cắt dài và thêm "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

# Hàm hiển thị banner
def _banner():
    banner = r"""


██████╗░██╗░░██╗░█████╗░██████╗░░█████╗░░██████╗  ████████╗███████╗░██████╗████████╗███╗░░██╗███████╗████████╗
██╔══██╗██║░░██║██╔══██╗██╔══██╗██╔══██╗██╔════╝  ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝████╗░██║██╔════╝╚══██╔══╝
██████╔╝███████║███████║██████╔╝██║░░██║╚█████╗░  ░░░██║░░░█████╗░░╚█████╗░░░░██║░░░██╔██╗██║█████╗░░░░░██║░░░
██╔═══╝░██╔══██║██╔══██║██╔══██╗██║░░██║░╚═══██╗  ░░░██║░░░██╔══╝░░░╚═══██╗░░░██║░░░██║╚████║██╔══╝░░░░░██║░░░
██║░░░░░██║░░██║██║░░██║██║░░██║╚█████╔╝██████╔╝  ░░░██║░░░███████╗██████╔╝░░░██║░░░██║░╚███║███████╗░░░██║░░░
╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═════╝░  ░░░╚═╝░░░╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚══╝╚══════╝░░░╚═╝░░░


    """
    print(f"{Fore.GREEN}{banner:^80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
    print_border("PHAROS TESTNET", Fore.GREEN)
    print(f"{Fore.YELLOW}│ {'Liên hệ / Contact'}: {Fore.CYAN}https://t.me/thog099{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}│ {'Replit'}: {Fore.CYAN}Thog{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}│ {'Channel Telegram'}: {Fore.CYAN}https://t.me/thogairdrops{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

# Hàm xóa màn hình
def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Các hàm chạy script
async def run_checkin(language: str):
    from scripts.ss1.checkin import run_checkin as checkin_run
    await checkin_run(language)

async def run_sendtx(language: str):
    from scripts.ss1.sendtx import run_sendtx as sendtx_run
    await sendtx_run(language)

async def run_swap(language: str):
    from scripts.ss1.swap import run_swap as swap_run
    await swap_run(language)

async def run_liquidity(language: str):
    from scripts.ss1.liquidity import run_liquidity as liquidity_run
    await liquidity_run(language)

async def run_deploytoken(language: str):
    from scripts.ss1.deploytoken import run_deploytoken as deploytoken_run
    await deploytoken_run(language)

async def run_sendtoken(language: str):
    from scripts.ss1.sendtoken import run_sendtoken as sendtoken_run
    await sendtoken_run(language)

async def run_nftcollection(language: str):
    from scripts.ss1.nftcollection import run_nftcollection as nftcollection_run
    await nftcollection_run(language)

async def run_mintair(language: str):
    from scripts.ss1.mintair import run_mintair as mintair_run
    await mintair_run(language)

async def run_social(language: str):
    from scripts.ss1.social import run_social as social_run
    await social_run(language)

async def run_wrap(language: str):
    from scripts.ss1.wrap import run_wrap as wrap_run
    await wrap_run(language)

async def run_easynode(language: str):
    from scripts.ss1.easynode import run_easynode as easynode_run
    await easynode_run(language)

async def run_mintomnihub(language: str):
    from scripts.ss1.mintomnihub import run_mintomnihub as mintomnihub_run
    await mintomnihub_run(language)

async def run_mintbadgegrandline(language: str):
    from scripts.ss1.mintbadgegrandline import run_mintbadgegrandline as mintbadgegrandline_run
    await mintbadgegrandline_run(language)

async def run_mintgotchipus(language: str):
    from scripts.ss1.mintgotchipus import run_mintgotchipus as mintgotchipus_run
    await mintgotchipus_run(language)

async def run_conftnft(language: str):
    from scripts.ss1.conftnft import run_conftnft as conftnft_run
    await conftnft_run(language)

async def run_domain(language: str):
    from scripts.ss1.domain import run_domain as domain_run
    await domain_run(language)

async def run_primussend(language: str):
    from scripts.ss1.primussend import run_primussend as primussend_run
    await primussend_run(language)

async def run_pnsdomain(language: str):
    from scripts.ss1.pnsdomain import run_pnsdomain as pnsdomain_run
    await pnsdomain_run(language)

#Atlantic

async def run_faucet(language: str):
    from scripts.atlantic.faucet import run_faucet as faucet_run
    await faucet_run(language)

async def run_faucetfaro(language: str):
    from scripts.atlantic.faucetfaro import run_faucetfaro as faucetfaro_run
    await faucetfaro_run(language)

async def run_checkin(language: str):
    from scripts.atlantic.checkin import run_checkin as checkin_run
    await checkin_run(language)

async def run_subscribe(language: str):
    from scripts.atlantic.subscribe import run_subscribe as subscribe_run
    await subscribe_run(language)

async def run_mintbadgegrandline(language: str):
    from scripts.atlantic.mintbadgegrandline import run_mintbadgegrandline as mintbadgegrandline_run
    await mintbadgegrandline_run(language)

async def run_redeem(language: str):
    from scripts.atlantic.redeem import run_redeem as redeem_run
    await redeem_run(language)

async def run_faroswap(language: str):
    from scripts.atlantic.faroswap import run_faroswap as faroswap_run
    await faroswap_run(language)

async def run_faroliquidity(language: str):
    from scripts.atlantic.faroliquidity import run_faroliquidity as faroliquidity_run
    await faroliquidity_run(language)

async def run_supplyzenith(language: str):
    from scripts.atlantic.supplyzenith import run_supplyzenith as supplyzenith_run
    await supplyzenith_run(language)

async def run_borrowzenith(language: str):
    from scripts.atlantic.borrowzenith import run_borrowzenith as borrowzenith_run
    await borrowzenith_run(language)
    

async def cmd_exit(language: str):
    messages = {"vi": "Đang thoát...", "en": "Exiting..."}
    print_border(messages[language], Fore.GREEN)
    sys.exit(0)

# Danh sách lệnh menu
SCRIPT_MAP = {
    "checkin": run_checkin,
    "sendtx": run_sendtx,
    "swap": run_swap,
    "liquidity": run_liquidity,
    "deploytoken": run_deploytoken,
    "sendtoken": run_sendtoken,
    "nftcollection": run_nftcollection,
    "mintair": run_mintair,
    "social": run_social,
    "wrap": run_wrap,
    "easynode": run_easynode,
    "mintomnihub": run_mintomnihub,
    "mintbadgegrandline": run_mintbadgegrandline,
    "mintgotchipus": run_mintgotchipus,
    "conftnft": run_conftnft,
    "domain": run_domain,
    "primussend": run_primussend,
    "pnsdomain": run_pnsdomain,
#Atlantic
    "faucet": run_faucet,
    "faucetfaro": run_faucetfaro,
    "subscribe": run_subscribe,
    "redeem": run_redeem,
    "faroswap": run_faroswap,
    "faroliquidity": run_faroliquidity,
    "supplyzenith": run_supplyzenith,
    "borrowzenith": run_borrowzenith,
    "exit": cmd_exit
}

# Danh sách script và thông báo theo ngôn ngữ
def get_available_scripts(language, season):
    season_label = {"ss1": "Season 1 & Season 2", "atlantic": "Atlantic"}
    scripts = {
        'vi': {
            'ss1': [
                {"name": "1. Check-in Hàng ngày", "value": "checkin"},
                {"name": "2. Deploy Token smart-contract", "value": "deploytoken"},
                {"name": "3. Gửi Token ERC20 ngẫu nhiên hoặc File (addressERC20.txt)", "value": "sendtoken"},
                {"name": "4. Deploy NFT smart-contract", "value": "nftcollection"},
                {"name": "5. Gửi TX ngẫu nhiên hoặc File (address.txt)", "value": "sendtx"},
                {"name": "6. Swap tokens [ PHRS | USDC | USDT ] → Zenith DEX", "value": "swap"},
                {"name": "7. Thêm thanh khoản [ PHRS | USDC | USDT ] → Zenith DEX", "value": "liquidity"},
                {"name": "8. Deploy Smart Contract Mintair", "value": "mintair"},
                {"name": "9. Deploy Smart Contract EasyNode", "value": "easynode"},
                {"name": "10. Verify Social Pharos [ Connect X - Discord ]", "value": "social"},
                {"name": "11. Wrap | Unwrap [ PHRS <-> WPHRS ]", "value": "wrap"},
                {"name": "12. Mint OmniHub NFT Studio", "value": "mintomnihub"},
                {"name": "13. Mint NFT Badge → Grandline", "value": "mintbadgegrandline"},
                {"name": "14. Mint NFT Pharos Gotchipus", "value": "mintgotchipus"},
                {"name": "15. Mint NFT Community Member of Pharos → CoNFT", "value": "conftnft"},
                {"name": "16. Mint Domain → CoNFT", "value": "domain", "locked": True},
                {"name": "17. Gửi TIP ngẫu nhiên hoặc File (username.txt) → Primus Labs", "value": "primussend"},
                {"name": "18. Mint Domain Pharos → PNS", "value": "pnsdomain"},
                {"name": "X. Thoát", "value": "exit"},
            ],
            'atlantic': [
                {"name": "1. Faucet PHRS → Pharos Network ", "value": "faucet"},
                {"name": "2. Faucet PHRS → FaroSwap", "value": "faucetfaro"},
                {"name": "3. Check-in Hàng ngày", "value": "checkin"},
                {"name": "4. Subscribe USDT | CASH+ → Asseto Finance ", "value": "subscribe", "locked": True},
                {"name": "5. Redeem CASH+ | USDT → Asseto Finance", "value": "redeem", "locked": True},
                {"name": "6. Swap Tokens → FaroSwap", "value": "faroswap", "locked": True},
                {"name": "7. Add Liquidity USDC/USDT → FaroSwap", "value": "faroliquidity", "locked": True},
                {"name": "8. Supply WBTC/WETH → Zenith Lending", "value": "supplyzenith", "locked": True},
                {"name": "9. Borrow WBTC/WETH → Zenith Lending", "value": "borrowzenith", "locked": True},
                {"name": "10. Mint NFT Badge → Grandline", "value": "mintbadgegrandline"},
                
                {"name": "X. Thoát", "value": "exit"},
            ]
        },
        'en': {
            'ss1': [
                {"name": "1. Daily Check-in", "value": "checkin"},
                {"name": "2. Deploy Token smart-contract", "value": "deploytoken"},
                {"name": "3. Send Token ERC20 random or File (addressERC20.txt)", "value": "sendtoken"},
                {"name": "4. Deploy NFT smart-contract", "value": "nftcollection"},
                {"name": "5. Send TX random or File (address.txt)", "value": "sendtx"},
                {"name": "6. Swap tokens [ PHRS | USDC | USDT ] → Zenith DEX", "value": "swap"},
                {"name": "7. Add Liquidity [ PHRS | USDC | USDT ] → Zenith DEX", "value": "liquidity"},
                {"name": "8. Deploy Smart Contract Mintair", "value": "mintair"},
                {"name": "9. Deploy Smart Contract EasyNode", "value": "easynode"},
                {"name": "10. Verify Social Pharos [ Connect X - Discord ]", "value": "social"},
                {"name": "11. Wrap | Unwrap [ PHRS <-> WPHRS ]", "value": "wrap"},
                {"name": "12. Mint OmniHub NFT Studio", "value": "mintomnihub"},
                {"name": "13. Mint NFT Badge → Grandline", "value": "mintbadgegrandline"},
                {"name": "14. Mint NFT Pharos Gotchipus", "value": "mintgotchipus"},
                {"name": "15. Mint NFT Community Member of Pharos → CoNFT", "value": "conftnft"},
                {"name": "16. Mint Domain → CoNFT", "value": "domain", "locked": True},
                {"name": "17. Send TIPs random or File (username.txt) → Primus Labs", "value": "primussend"},
                {"name": "18. Mint Domain Pharos → PNS", "value": "pnsdomain"},
                {"name": "X. Exit", "value": "exit"},
            ],
            'atlantic': [
                {"name": "1. Faucet PHRS → Pharos Network ", "value": "faucet"},
                {"name": "2. Faucet PHRS → FaroSwap", "value": "faucetfaro"},
                {"name": "3. Daily Check-in", "value": "checkin"},
                {"name": "4. Subscribe USDT | CASH+ → Asseto Finance ", "value": "subscribe", "locked": True},
                {"name": "5. Redeem CASH+ | USDT → Asseto Finance", "value": "redeem", "locked": True},
                {"name": "6. Swap Tokens → FaroSwap", "value": "faroswap", "locked": True},
                {"name": "7. Add Liquidity USDC/USDT → FaroSwap", "value": "faroliquidity", "locked": True},
                {"name": "8. Supply WBTC/WETH → Zenith Lending", "value": "supplyzenith", "locked": True},
                {"name": "9. Borrow WBTC/WETH → Zenith Lending", "value": "borrowzenith", "locked": True},
                {"name": "10. Mint NFT Badge → Grandline", "value": "mintbadgegrandline"},
                {"name": "X. Exit", "value": "exit"},
            ]
        }
    }
    return scripts[language][season]

def run_script(script_func, language):
    """Chạy script bất kể nó là async hay không."""
    if asyncio.iscoroutinefunction(script_func):
        asyncio.run(script_func(language))
    else:
        script_func(language)

def select_language():
    while True:
        _clear()
        _banner()
        print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
        print_border("CHỌN NGÔN NGỮ / SELECT LANGUAGE", Fore.YELLOW)
        questions = [
            inquirer.List('language',
                          message=f"{Fore.CYAN}Vui lòng chọn / Please select:{Style.RESET_ALL}",
                          choices=[("1. Tiếng Việt", 'vi'), ("2. English", 'en')],
                          carousel=True)
        ]
        answer = inquirer.prompt(questions)
        if answer and answer['language'] in ['vi', 'en']:
            return answer['language']
        print(f"{Fore.RED}❌ {'Lựa chọn không hợp lệ / Invalid choice':^76}{Style.RESET_ALL}")

def select_season():
    while True:
        _clear()
        _banner()
        print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
        print_border("CHỌN MÙA / SELECT SEASON", Fore.YELLOW)
        questions = [
            inquirer.List('season',
                          message=f"{Fore.CYAN}Vui lòng chọn mùa / Please select season:{Style.RESET_ALL}",
                          choices=[("1. Season 1 & Season 2", 'ss1'), ("2. Atlantic", 'atlantic')],
                          carousel=True)
        ]
        answer = inquirer.prompt(questions)
        if answer and answer['season'] in ['ss1', 'atlantic']:
            return answer['season']
        print(f"{Fore.RED}❌ {'Lựa chọn không hợp lệ / Invalid choice':^76}{Style.RESET_ALL}")

def main():
    _clear()
    _banner()
    language = select_language()
    season = select_season()

    messages = {
        "vi": {
            "running": f"Đang thực thi: {{}} (Mùa: {season.upper()})",
            "completed": f"Đã hoàn thành: {{}} (Mùa: {season.upper()})",
            "error": "Lỗi: {}",
            "press_enter": "Nhấn Enter để tiếp tục...",
            "menu_title": f"MENU CHÍNH - PHAROS TESTNET - MÙA {season.upper()}",
            "select_script": "Chọn script để chạy",
            "locked": "🔒 Script này bị khóa! Vui lòng vào group hoặc donate để mở khóa.",
            "no_script": "Chưa có script nào cho mùa này!"
        },
        "en": {
            "running": f"Running: {{}} (Season: {season.upper()})",
            "completed": f"Completed: {{}} (Season: {season.upper()})",
            "error": "Error: {}",
            "press_enter": "Press Enter to continue...",
            "menu_title": f"MAIN MENU - PHAROS TESTNET - SEASON {season.upper()}",
            "select_script": "Select script to run",
            "locked": "🔒 This script is locked! Please join our group or donate to unlock.",
            "no_script": "No scripts available for this season!"
        }
    }

    while True:
        _clear()
        _banner()
        print(f"{Fore.YELLOW}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
        print_border(messages[language]["menu_title"], Fore.YELLOW)
        print(f"{Fore.CYAN}│ {messages[language]['select_script'].center(BORDER_WIDTH - 4)} │{Style.RESET_ALL}")

        available_scripts = get_available_scripts(language, season)
        questions = [
            inquirer.List('script',
                          message=f"{Fore.CYAN}{messages[language]['select_script']}{Style.RESET_ALL}",
                          choices=[script["name"] for script in available_scripts],
                          carousel=True)
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            continue

        selected_script_name = answers['script']
        selected_script = next(script for script in available_scripts if script["name"] == selected_script_name)
        selected_script_value = selected_script["value"]

        if selected_script.get("locked"):
            _clear()
            _banner()
            print_border("SCRIPT BỊ KHÓA / LOCKED", Fore.RED)
            print(f"{Fore.YELLOW}{messages[language]['locked']}")
            print('')
            print(f"{Fore.CYAN}→ Telegram: https://t.me/thogairdrops")
            print(f"{Fore.CYAN}→ Donate: https://buymecafe.vercel.app{Style.RESET_ALL}")
            print('')
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
            continue

        if selected_script_value == "none":
            _clear()
            _banner()
            print_border(messages[language]["no_script"], Fore.RED)
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
            continue

        script_func = SCRIPT_MAP.get(selected_script_value)
        if script_func is None:
            print(f"{Fore.RED}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(f"Chưa triển khai / Not implemented: {selected_script_name}", Fore.RED)
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
            continue

        try:
            print(f"{Fore.CYAN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["running"].format(selected_script_name), Fore.CYAN)
            run_script(script_func, language)
            print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["completed"].format(selected_script_name), Fore.GREEN)
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
        except Exception as e:
            print(f"{Fore.RED}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["error"].format(str(e)), Fore.RED)
            print('')
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")

if __name__ == "__main__":
    main()


