import pandas as pd


def get_crypto_tickers():
    """Get list of top cryptocurrency tickers supported by Yahoo Finance."""
    # List of top cryptocurrencies (as many as possible supported by Yahoo Finance)
    crypto_tickers = [
        # Top cryptocurrencies by market capitalization
        "BTC-USD",    # Bitcoin
        "ETH-USD",    # Ethereum
        "USDT-USD",   # Tether
        "BNB-USD",    # Binance Coin
        "USDC-USD",   # USD Coin
        "XRP-USD",    # XRP
        "ADA-USD",    # Cardano
        "SOL-USD",    # Solana
        "DOGE-USD",   # Dogecoin
        "DOT-USD",    # Polkadot
        "SHIB-USD",   # Shiba Inu
        "MATIC-USD",  # Polygon
        "TRX-USD",    # TRON
        "UNI-USD",    # Uniswap
        "AVAX-USD",   # Avalanche
        "LTC-USD",    # Litecoin
        "LEO-USD",    # UNUS SED LEO
        "ATOM-USD",   # Cosmos
        "LINK-USD",   # Chainlink
        "XMR-USD",    # Monero
        "ETC-USD",    # Ethereum Classic
        "XLM-USD",    # Stellar
        "BCH-USD",    # Bitcoin Cash
        "ALGO-USD",   # Algorand
        "NEAR-USD",   # NEAR Protocol
        "TON-USD",    # Toncoin
        "OKB-USD",    # OKB
        "FTT-USD",    # FTX Token
        "CRO-USD",    # Crypto.com Coin
        "QNT-USD",    # Quant
        "LUNC-USD",   # Terra Classic
        "VET-USD",    # VeChain
        "FIL-USD",    # Filecoin
        "ICP-USD",    # Internet Computer
        "HBAR-USD",   # Hedera
        "APE-USD",    # ApeCoin
        "EGLD-USD",   # MultiversX (Elrond)
        "FLOW-USD",   # Flow
        "EOS-USD",    # EOS
        "XTZ-USD",    # Tezos
        "AAVE-USD",   # Aave
        "THETA-USD",  # Theta Network
        "MANA-USD",   # Decentraland
        "AXS-USD",    # Axie Infinity
        "SAND-USD",   # The Sandbox
        "CHZ-USD",    # Chiliz
        "KLAY-USD",   # Klaytn
        "ZEC-USD",    # Zcash
        "KAVA-USD",   # Kava
        "HT-USD",     # Huobi Token
        "MIOTA-USD",  # IOTA
        "GRT-USD",    # The Graph
        "SNX-USD",    # Synthetix
        "ENJ-USD",    # Enjin Coin
        "CRV-USD",    # Curve DAO Token
        "BAT-USD",    # Basic Attention Token
        "1INCH-USD",  # 1inch
        "OMG-USD",    # OMG Network
        "COMP-USD",   # Compound
        "DASH-USD",   # Dash
        "RVN-USD",    # Ravencoin
        "LRC-USD",    # Loopring
        "ZIL-USD",    # Zilliqa
        "ANKR-USD",   # Ankr
        "HOT-USD",    # Holo
        "CEL-USD",    # Celsius
        "HNT-USD",    # Helium
        "STORJ-USD",  # Storj
        "SC-USD",     # Siacoin
        "BTT-USD",    # BitTorrent
        "XDC-USD",    # XDC Network
        "ONT-USD",    # Ontology
        "ICX-USD",    # ICON
        "IOST-USD",   # IOST
        "NANO-USD",   # Nano
        "QTUM-USD",   # Qtum
        "CKB-USD",    # Nervos Network
        "ZEN-USD",    # Horizen
        "KSM-USD",    # Kusama
        "UMA-USD",    # UMA
        "YFI-USD",    # yearn.finance
        "BAL-USD",    # Balancer
        "SRM-USD",    # Serum
        "GLM-USD",    # Golem
        "CVC-USD",    # Civic
        "REN-USD",    # Ren
        "SXP-USD",    # Solar
        "SKL-USD",    # SKALE Network
        "CELR-USD",   # Celer Network
        "POLY-USD",   # Polymath
        "STMX-USD",   # StormX
        "WRX-USD",    # WazirX
        "DENT-USD",   # Dent
        "WIN-USD",    # WINkLink
        "SNT-USD",    # Status
        "REEF-USD",   # Reef
        "TROY-USD",   # TROY
        "CHR-USD",    # Chromia
        "FET-USD",    # Fetch.ai
        "AR-USD",     # Arweave
        "DGB-USD",    # DigiByte
        "FUN-USD",    # FunFair
        "COTI-USD",   # COTI
        "RLC-USD",    # iExec RLC
        "LPT-USD",    # Livepeer
        "MFT-USD",    # Mainframe
        "PERL-USD",   # Perlin
        "ONG-USD",    # Ontology Gas
    ]
    return crypto_tickers


def get_commodity_tickers():
    """Get list of commodity tickers supported by Yahoo Finance."""
    # List of commodity tickers and their descriptions
    commodities = [
        # Precious Metals
        "GC=F",   # Gold Futures
        "SI=F",   # Silver Futures
        "PL=F",   # Platinum Futures
        "PA=F",   # Palladium Futures
        "HG=F",   # Copper Futures

        # Energy
        "CL=F",   # Crude Oil WTI Futures
        "BZ=F",   # Brent Crude Oil Futures
        "NG=F",   # Natural Gas Futures
        "HO=F",   # Heating Oil Futures
        "RB=F",   # RBOB Gasoline Futures

        # Agricultural
        "ZC=F",   # Corn Futures
        "ZW=F",   # Wheat Futures
        "ZS=F",   # Soybean Futures
        "KC=F",   # Coffee Futures
        "CT=F",   # Cotton Futures
        "CC=F",   # Cocoa Futures
        "SB=F",   # Sugar Futures

        # Livestock
        "LE=F",   # Live Cattle Futures
        "HE=F",   # Lean Hogs Futures

        # Cryptocurrencies
        "BTC-USD",  # Bitcoin
        "ETH-USD",  # Ethereum
    ]
    return commodities


def get_sp500_tickers():
    """Get list of current S&P 500 tickers."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    tickers = tables[0]["Symbol"].tolist()
    return [ticker.replace(".", "-") for ticker in tickers]


