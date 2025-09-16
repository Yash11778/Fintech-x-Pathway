"""
Real-Time Demo Script
Demonstrates the live price updates and market events
Perfect for hackathon presentation
"""

import asyncio
import time
from datetime import datetime
from services.realtime_stock_service import get_real_time_service

async def demonstrate_real_time_updates():
    """Demonstrate real-time price updates with commentary"""
    service = get_real_time_service()
    
    print("🚀" + "="*60)
    print("   LIVE FINTECH AI ASSISTANT - REAL-TIME DEMO")
    print("🚀" + "="*60)
    print()
    
    print("🎯 PROBLEM SOLVED:")
    print("   ❌ Before: Static prices that never change")
    print("   ✅ After: Dynamic prices updating every 2-3 seconds!")
    print()
    
    # Show initial prices
    print("📊 INITIAL STOCK PRICES:")
    initial_prices = await service.get_real_time_prices()
    for symbol, stock in list(initial_prices.items())[:8]:
        print(f"   {symbol}: ${stock.price:.2f}")
    
    print(f"\n⏱️  LIVE UPDATES - Watching prices change in real-time...")
    print("    (Prices update every 2-8 seconds to simulate real market)")
    print()
    
    # Monitor for 30 seconds
    for round_num in range(1, 7):
        await asyncio.sleep(5)
        
        print(f"🔄 UPDATE #{round_num} - {datetime.now().strftime('%H:%M:%S')}")
        current_prices = await service.get_real_time_prices()
        
        changes_count = 0
        for symbol, stock in list(current_prices.items())[:8]:
            initial_price = initial_prices[symbol].price
            price_diff = stock.price - initial_price
            percent_diff = (price_diff / initial_price) * 100
            
            if abs(percent_diff) > 0.01:  # Show if changed by more than 0.01%
                changes_count += 1
                emoji = "📈" if percent_diff > 0 else "📉"
                print(f"   {emoji} {symbol}: ${stock.price:.2f} ({percent_diff:+.2f}%)")
        
        if changes_count == 0:
            print("   📊 Waiting for next price update cycle...")
        else:
            print(f"   ✅ {changes_count} stocks updated!")
        print()
    
    # Simulate major market event
    print("📰 SIMULATING BREAKING NEWS EVENT:")
    print("   'Tesla announces major breakthrough in autonomous driving!'")
    await service.simulate_market_event("TSLA", 7.5)  # 7.5% jump
    
    await asyncio.sleep(2)
    tsla_price = await service.get_stock_price("TSLA")
    print(f"   🚀 TSLA jumped to ${tsla_price.price:.2f} ({tsla_price.change_percent:+.2f}%)")
    print()
    
    # Show market summary
    summary = service.get_market_summary()
    print("📊 CURRENT MARKET SUMMARY:")
    print(f"   Sentiment: {summary['sentiment']}")
    print(f"   Gainers: {summary['gainers']} | Losers: {summary['losers']}")
    print(f"   Average Change: {summary['avg_change']:+.2f}%")
    print()
    
    print("🎉 DEMONSTRATION COMPLETE!")
    print("✅ Dashboard is now showing REAL-TIME price updates")
    print("✅ Prices change every 2-3 seconds like a real trading platform")
    print("✅ Perfect for live hackathon demo!")
    print("🚀" + "="*60)

if __name__ == "__main__":
    try:
        asyncio.run(demonstrate_real_time_updates())
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

# Also create a simple continuous demo
async def continuous_price_monitor():
    """Continuously monitor and display price changes"""
    service = get_real_time_service()
    
    print("🔴 LIVE PRICE MONITOR - Press Ctrl+C to stop")
    print("📊 Monitoring real-time price changes...")
    print()
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            prices = await service.get_real_time_prices()
            
            # Show a few stocks with their current status
            print(f"⏰ {current_time} | ", end="")
            for symbol, stock in list(prices.items())[:5]:
                change_emoji = "📈" if stock.change_percent > 0 else "📉" if stock.change_percent < 0 else "📊"
                print(f"{symbol}:${stock.price:.2f}({stock.change_percent:+.1f}%) {change_emoji} | ", end="")
            print()
            
            await asyncio.sleep(3)  # Update every 3 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Live monitor stopped")
