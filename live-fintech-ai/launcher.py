"""
Live Fintech AI™ Launcher
Start the AI-powered trading co-pilot with streaming intelligence
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Live Fintech AI™ application"""
    
    print("🚀 Starting Live Fintech AI™ - Real-Time Trading Co-Pilot")
    print("=" * 60)
    print("🤖 AI-Powered Streaming Intelligence Platform")
    print("⚡ Pathway-Powered Real-Time Data Processing")
    print("📊 Continuous Learning & Anomaly Detection")
    print("💼 Portfolio AI & Market Insights")
    print("=" * 60)
    
    # Get the directory of this script
    current_dir = Path(__file__).parent
    
    # Path to the main application
    app_path = current_dir / "live_fintech_ai.py"
    
    if not app_path.exists():
        print("❌ Error: live_fintech_ai.py not found!")
        print(f"Expected location: {app_path}")
        return
    
    try:
        print("🔄 Initializing AI models and streaming pipeline...")
        print("🌐 Starting web interface...")
        print("\n📈 Live Fintech AI™ will open in your browser")
        print("🔴 Press Ctrl+C to stop the application")
        print("\n" + "=" * 60 + "\n")
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_path),
            "--server.address", "localhost",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main()
