#!/usr/bin/env python3
"""
Script para rodar o main.py com logs direcionados para arquivo
"""
import sys
import os
import subprocess
import signal
from datetime import datetime

def main():
    # Criar diretório de logs
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Gerar timestamp para os logs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Arquivos de log
    stdout_log = f"{log_dir}/hephaestus_stdout_{timestamp}.log"
    stderr_log = f"{log_dir}/hephaestus_stderr_{timestamp}.log"
    combined_log = f"{log_dir}/hephaestus_combined_{timestamp}.log"
    
    print(f"🚀 Iniciando Hephaestus com logs...")
    print(f"📄 Logs de saída: {stdout_log}")
    print(f"❌ Logs de erro: {stderr_log}")
    print(f"🔄 Logs combinados: {combined_log}")
    print(f"\n💡 Para monitorar em tempo real, execute:")
    print(f"   tail -f {combined_log}")
    print(f"\n🛑 Para parar o sistema: Ctrl+C")
    print("="*60)
    
    # Abrir arquivos de log
    with open(stdout_log, 'w') as stdout_file, \
         open(stderr_log, 'w') as stderr_file, \
         open(combined_log, 'w') as combined_file:
        
        # Executar main.py
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        def signal_handler(signum, frame):
            print(f"\n🛑 Recebido sinal {signum}, parando Hephaestus...")
            process.terminate()
            process.wait()
            print("✅ Hephaestus parado.")
            sys.exit(0)
        
        # Configurar handler para Ctrl+C
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Ler e redirecionar logs em tempo real
            while True:
                # Ler stdout
                stdout_line = process.stdout.readline()
                if stdout_line:
                    stdout_line = stdout_line.rstrip()
                    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Escrever para arquivos
                    stdout_file.write(f"[{timestamp_str}] {stdout_line}\n")
                    stdout_file.flush()
                    
                    combined_file.write(f"[STDOUT] [{timestamp_str}] {stdout_line}\n")
                    combined_file.flush()
                    
                    # Mostrar no terminal também
                    print(f"[STDOUT] {stdout_line}")
                
                # Ler stderr
                stderr_line = process.stderr.readline()
                if stderr_line:
                    stderr_line = stderr_line.rstrip()
                    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Escrever para arquivos
                    stderr_file.write(f"[{timestamp_str}] {stderr_line}\n")
                    stderr_file.flush()
                    
                    combined_file.write(f"[STDERR] [{timestamp_str}] {stderr_line}\n")
                    combined_file.flush()
                    
                    # Mostrar no terminal também
                    print(f"[STDERR] {stderr_line}")
                
                # Verificar se o processo terminou
                if process.poll() is not None:
                    # Ler qualquer saída restante
                    remaining_stdout, remaining_stderr = process.communicate()
                    
                    if remaining_stdout:
                        stdout_file.write(remaining_stdout)
                        combined_file.write(f"[STDOUT] {remaining_stdout}")
                        print(f"[STDOUT] {remaining_stdout}")
                    
                    if remaining_stderr:
                        stderr_file.write(remaining_stderr)
                        combined_file.write(f"[STDERR] {remaining_stderr}")
                        print(f"[STDERR] {remaining_stderr}")
                    
                    break
        
        except KeyboardInterrupt:
            print("\n🛑 Interrupção detectada, parando Hephaestus...")
            process.terminate()
            process.wait()
        
        except Exception as e:
            print(f"❌ Erro executando Hephaestus: {e}")
            process.terminate()
            process.wait()
            return 1
        
        return process.returncode

if __name__ == "__main__":
    sys.exit(main())