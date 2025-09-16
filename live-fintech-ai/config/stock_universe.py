"""
COMPREHENSIVE STOCK UNIVERSE
All major stocks across all sectors for real-time analysis
"""

# Major Technology Stocks
TECH_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "TSLA", "NVDA", 
    "NFLX", "ADBE", "CRM", "ORCL", "IBM", "INTC", "AMD", "QCOM",
    "AVGO", "TXN", "INTU", "NOW", "TEAM", "ZM", "DOCU", "OKTA",
    "SNOW", "PLTR", "U", "NET", "DDOG", "MDB", "CRWD", "ZS",
    "PANW", "FTNT", "CYBR", "SPLK", "WDAY", "VEEV", "TWLO"
]

# Financial Stocks
FINANCIAL_STOCKS = [
    "JPM", "BAC", "WFC", "C", "GS", "MS", "USB", "PNC", "TFC", "COF",
    "AXP", "BLK", "SCHW", "SPGI", "ICE", "CME", "MCO", "MSCI",
    "V", "MA", "PYPL", "SQ", "AFRM", "SOFI", "LC", "UPST"
]

# Healthcare & Biotech
HEALTHCARE_STOCKS = [
    "JNJ", "PFE", "UNH", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "GILD", "BIIB", "REGN", "VRTX", "ILMN", "MRNA", "BNTX",
    "MODERNA", "ZTS", "ELV", "CVS", "HUM", "ANTM", "CI"
]

# Consumer & Retail
CONSUMER_STOCKS = [
    "WMT", "HD", "PG", "KO", "PEP", "NKE", "MCD", "SBUX", "DIS",
    "CMCSA", "VZ", "T", "NFLX", "ROKU", "SPOT", "UBER", "LYFT",
    "ABNB", "DASH", "SHOP", "ETSY", "W", "CHWY", "PINS", "SNAP"
]

# Energy & Materials
ENERGY_MATERIALS_STOCKS = [
    "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "KMI",
    "OKE", "WMB", "EPD", "ET", "MPLX", "LIN", "APD", "ECL", "SHW",
    "DD", "DOW", "CF", "MOS", "NEM", "GOLD", "AEM"
]

# Industrial & Aerospace
INDUSTRIAL_STOCKS = [
    "BA", "HON", "UPS", "UNP", "CAT", "DE", "MMM", "GE", "RTX",
    "LMT", "NOC", "GD", "TDG", "CTAS", "FDX", "CSX", "NSC"
]

# Real Estate & REITs
REAL_ESTATE_STOCKS = [
    "AMT", "PLD", "CCI", "EQIX", "SPG", "O", "WELL", "EXR", "AVB",
    "EQR", "UDR", "CPT", "MAA", "ESS", "VTR", "PEAK", "SUI"
]

# Emerging & Growth Stocks
GROWTH_STOCKS = [
    "TSLA", "RIVN", "LCID", "F", "GM", "RACE", "NKLA", "RIDE",
    "PLTR", "RBLX", "HOOD", "COIN", "MSTR", "SQ", "TDOC", "PTON"
]

# International & ADRs
INTERNATIONAL_STOCKS = [
    "TSM", "ASML", "SAP", "TM", "NVO", "UL", "SNY", "DEO", "BP",
    "SHEL", "RIO", "BHP", "VALE", "ING", "DB", "CS", "UBS"
]

# Crypto-Related
CRYPTO_STOCKS = [
    "COIN", "MSTR", "RIOT", "MARA", "CAN", "BITF", "HUT", "ARBK",
    "BTBT", "EBON", "SOS", "NCTY", "GREE", "SPRT"
]

# Combine all stocks
ALL_STOCKS = (
    TECH_STOCKS + FINANCIAL_STOCKS + HEALTHCARE_STOCKS + 
    CONSUMER_STOCKS + ENERGY_MATERIALS_STOCKS + INDUSTRIAL_STOCKS +
    REAL_ESTATE_STOCKS + GROWTH_STOCKS + INTERNATIONAL_STOCKS + 
    CRYPTO_STOCKS
)

# Remove duplicates and sort
ALL_STOCKS = sorted(list(set(ALL_STOCKS)))

# Stock categories for filtering
STOCK_CATEGORIES = {
    "Technology": TECH_STOCKS,
    "Financial": FINANCIAL_STOCKS,
    "Healthcare": HEALTHCARE_STOCKS,
    "Consumer": CONSUMER_STOCKS,
    "Energy & Materials": ENERGY_MATERIALS_STOCKS,
    "Industrial": INDUSTRIAL_STOCKS,
    "Real Estate": REAL_ESTATE_STOCKS,
    "Growth": GROWTH_STOCKS,
    "International": INTERNATIONAL_STOCKS,
    "Crypto-Related": CRYPTO_STOCKS
}

print(f"📊 Total stocks available: {len(ALL_STOCKS)}")
print(f"📈 Categories: {len(STOCK_CATEGORIES)}")
print(f"🎯 Sample stocks: {ALL_STOCKS[:10]}")

# Most active stocks for real-time monitoring
MOST_ACTIVE_STOCKS = [
    "AAPL", "TSLA", "NVDA", "AMZN", "GOOGL", "MSFT", "META", "NFLX",
    "AMD", "INTC", "PLTR", "RIVN", "COIN", "MSTR", "ROKU", "UBER",
    "PYPL", "SQ", "SHOP", "SNAP", "PINS", "ZOOM", "DOCU", "CRWD"
]

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE STOCK UNIVERSE LOADED")
    print(f"📊 Total available stocks: {len(ALL_STOCKS)}")
    for category, stocks in STOCK_CATEGORIES.items():
        print(f"   {category}: {len(stocks)} stocks")
    print(f"\n🎯 Most Active (for real-time): {len(MOST_ACTIVE_STOCKS)} stocks")
    print(f"📈 Sample: {MOST_ACTIVE_STOCKS[:5]}")
