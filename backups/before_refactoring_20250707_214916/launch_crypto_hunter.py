#!/usr/bin/env python3
"""
Launch script for Crypto Hunter 24/7 - Production ready deployment.
"""

import asyncio
import sys
import os
import signal
import logging
from pathlib import Path
from datetime import datetime
import psutil
import json

class CryptoHunterLauncher:
    """Production launcher for Crypto Hunter 24/7."""
    
    def __init__(self):
        self.pid_file = "crypto_hunter.pid"
        self.log_file = "crypto_hunter_launcher.log"
        self.stats_file = "crypto_hunter_stats.json"
        self.running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CryptoHunterLauncher')
    
    def is_already_running(self) -> bool:
        """Check if Crypto Hunter is already running."""
        if not os.path.exists(self.pid_file):
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                if 'crypto_hunter' in ' '.join(proc.cmdline()).lower():
                    return True
        except:
            pass
        
        # Clean up stale PID file
        os.remove(self.pid_file)
        return False
    
    def write_pid(self):
        """Write current process PID to file."""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    
    def cleanup_pid(self):
        """Remove PID file."""
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)
    
    def save_stats(self, stats: dict):
        """Save runtime stats to file."""
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
    
    def load_stats(self) -> dict:
        """Load previous stats if available."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    async def run_crypto_hunter(self):
        """Run the crypto hunter with error recovery."""
        from crypto_hunter_24_7 import CryptoHunter247
        
        restart_count = 0
        max_restarts = 5
        
        while self.running and restart_count < max_restarts:
            try:
                self.logger.info(f"Starting Crypto Hunter 24/7 (Attempt {restart_count + 1})")
                
                async with CryptoHunter247() as hunter:
                    # Configure for production
                    hunter.PROFIT_THRESHOLD = 0.0001  # 0.01%
                    hunter.HIGH_PROFIT_THRESHOLD = 0.005  # 0.5%
                    hunter.SCAN_INTERVAL = 10  # 10 seconds
                    
                    await hunter.hunt_24_7()
                
                # If we get here, it was a clean shutdown
                break
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal")
                break
            except Exception as e:
                restart_count += 1
                self.logger.error(f"Error in Crypto Hunter: {e}")
                
                if restart_count < max_restarts:
                    self.logger.info(f"Restarting in 30 seconds... ({restart_count}/{max_restarts})")
                    await asyncio.sleep(30)
                else:
                    self.logger.error("Max restarts reached. Stopping.")
                    break
    
    async def launch(self):
        """Main launch function."""
        if self.is_already_running():
            print("❌ Crypto Hunter 24/7 is already running!")
            print("   Use 'python launch_crypto_hunter.py stop' to stop it first.")
            return
        
        self.running = True
        self.write_pid()
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            self.logger.info("Received shutdown signal")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            print("🚀 LAUNCHING CRYPTO HUNTER 24/7")
            print("=" * 50)
            print(f"🕐 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📁 PID file: {self.pid_file}")
            print(f"📄 Log file: {self.log_file}")
            print(f"📊 Stats file: {self.stats_file}")
            print("\n⚠️  Press Ctrl+C to stop gracefully")
            print("🔍 Monitoring will begin in 5 seconds...")
            
            await asyncio.sleep(5)
            
            await self.run_crypto_hunter()
            
        except KeyboardInterrupt:
            print("\n🛑 Shutting down gracefully...")
        finally:
            self.cleanup_pid()
            print("✅ Crypto Hunter 24/7 stopped")
    
    def stop(self):
        """Stop running Crypto Hunter."""
        if not os.path.exists(self.pid_file):
            print("❌ Crypto Hunter 24/7 is not running")
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                print(f"🛑 Stopping Crypto Hunter 24/7 (PID: {pid})")
                
                # Send SIGTERM for graceful shutdown
                proc.terminate()
                
                # Wait for graceful shutdown
                try:
                    proc.wait(timeout=30)
                    print("✅ Crypto Hunter 24/7 stopped gracefully")
                except psutil.TimeoutExpired:
                    # Force kill if needed
                    proc.kill()
                    print("⚠️  Crypto Hunter 24/7 force stopped")
            else:
                print("❌ Process not found")
            
            self.cleanup_pid()
            
        except Exception as e:
            print(f"❌ Error stopping Crypto Hunter: {e}")
    
    def status(self):
        """Show status of Crypto Hunter."""
        if self.is_already_running():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            proc = psutil.Process(pid)
            
            print("🟢 Crypto Hunter 24/7 is RUNNING")
            print(f"📍 PID: {pid}")
            print(f"🕐 Started: {datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"💾 Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
            print(f"⚡ CPU: {proc.cpu_percent():.1f}%")
            
            # Show recent stats if available
            stats = self.load_stats()
            if stats:
                print("\n📊 Recent Statistics:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
        else:
            print("🔴 Crypto Hunter 24/7 is NOT running")
    
    def show_logs(self, lines: int = 50):
        """Show recent log entries."""
        if os.path.exists(self.log_file):
            print(f"📄 Last {lines} lines from {self.log_file}:")
            print("-" * 60)
            
            with open(self.log_file, 'r') as f:
                log_lines = f.readlines()
                for line in log_lines[-lines:]:
                    print(line.strip())
        else:
            print("❌ Log file not found")

def show_help():
    """Show help information."""
    print("🤖 CRYPTO HUNTER 24/7 - LAUNCHER")
    print("=" * 40)
    print("Commands:")
    print("  start    - Start Crypto Hunter 24/7")
    print("  stop     - Stop Crypto Hunter 24/7")
    print("  restart  - Restart Crypto Hunter 24/7")
    print("  status   - Show current status")
    print("  logs     - Show recent logs")
    print("  help     - Show this help")
    print()
    print("Examples:")
    print("  python launch_crypto_hunter.py start")
    print("  python launch_crypto_hunter.py status")
    print("  python launch_crypto_hunter.py logs")

async def main():
    """Main function."""
    launcher = CryptoHunterLauncher()
    
    if len(sys.argv) < 2:
        command = "start"
    else:
        command = sys.argv[1].lower()
    
    if command == "start":
        await launcher.launch()
    elif command == "stop":
        launcher.stop()
    elif command == "restart":
        launcher.stop()
        await asyncio.sleep(2)
        await launcher.launch()
    elif command == "status":
        launcher.status()
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        launcher.show_logs(lines)
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)