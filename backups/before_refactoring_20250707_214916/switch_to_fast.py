#!/usr/bin/env python3
"""
Script para trocar do sistema lento para o sistema rápido
"""
import os
import signal
import subprocess
import time
import sys

def main():
    print("🔄 SWITCHING TO FAST BOOT MODE")
    print("=" * 40)
    
    # 1. Parar processo atual
    print("🛑 Stopping slow boot system...")
    try:
        # Encontrar PID do processo atual
        result = subprocess.run(
            ["pgrep", "-f", "python.*main.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"   Killing PID {pid}")
                    os.kill(int(pid), signal.SIGTERM)
            
            # Aguardar um pouco
            time.sleep(2)
            
            # Verificar se ainda está rodando
            result = subprocess.run(
                ["pgrep", "-f", "python.*main.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("   Force killing...")
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        os.kill(int(pid), signal.SIGKILL)
        
        print("✅ Old system stopped")
        
    except Exception as e:
        print(f"⚠️ Error stopping old system: {e}")
    
    # 2. Aguardar um momento
    time.sleep(1)
    
    # 3. Iniciar sistema rápido
    print("🚀 Starting FAST BOOT system...")
    
    try:
        # Executar main_fast.py
        process = subprocess.Popen([
            sys.executable, "main_fast.py"
        ])
        
        print(f"✅ Fast boot started (PID: {process.pid})")
        print("🌐 Server should be available at http://localhost:8000")
        print("⚡ Fast boot typically starts in 3-5 seconds")
        
        # Verificar se iniciou corretamente
        time.sleep(3)
        
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Fast boot confirmed: {data['status']}")
            else:
                print(f"⚠️ Response code: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Health check failed: {e}")
            print("   (This is normal, components might still be loading)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to start fast boot: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())