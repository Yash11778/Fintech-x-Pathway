"""
PATHWAY REAL-TIME LAUNCHER
Launch the enhanced real-time stock dashboard
"""

import subprocess
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check required dependencies"""
    required = ['streamlit', 'yfinance', 'plotly', 'pandas']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} - OK")
        except ImportError:
            missing.append(package)
            logger.warning(f"❌ {package} - MISSING")
    
    return missing

def install_dependencies(missing):
    """Install missing dependencies"""
    if not missing:
        return True
        
    logger.info(f"Installing: {', '.join(missing)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        logger.info("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        logger.error("❌ Failed to install dependencies")
        return False

def launch_dashboard():
    """Launch the real-time dashboard"""
    dashboard_path = "real_time_pathway_dashboard.py"
    
    if not os.path.exists(dashboard_path):
        logger.error(f"Dashboard not found: {dashboard_path}")
        return False
    
    logger.info("🚀 Launching Real-Time Pathway Dashboard...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", dashboard_path,
            "--server.port", "8501",
            "--server.headless", "false"
        ])
        return True
    except Exception as e:
        logger.error(f"Failed to launch: {e}")
        return False

def main():
    print("🚀 PATHWAY REAL-TIME STOCK ANALYZER")
    print("=" * 50)
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        if not install_dependencies(missing):
            print("❌ Failed to install required packages")
            return
    
    print("✅ All dependencies ready!")
    print("🎯 Launching real-time dashboard...")
    print("📱 URL: http://localhost:8501")
    print("=" * 50)
    
    launch_dashboard()

if __name__ == "__main__":
    main()
