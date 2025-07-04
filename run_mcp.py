#!/usr/bin/env python3
"""
Script robusto para executar o Servidor MCP Hephaestus
=====================================================

Este script resolve problemas de asyncio e garante que o servidor
funcione corretamente em diferentes ambientes.
"""

import os
import sys
import time
import signal
import subprocess
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MCPRunner")

class MCPServerRunner:
    """Executa o servidor MCP de forma robusta"""
    
    def __init__(self):
        self.server_process = None
        self.running = False
        
    def check_dependencies(self):
        """Verifica se as dependências estão instaladas"""
        logger.info("🔍 Verificando dependências...")
        
        try:
            import mcp.server.fastmcp
            logger.info("✅ Dependências MCP encontradas")
            return True
        except ImportError:
            logger.error("❌ Dependências MCP não encontradas!")
            logger.info("📦 Instalando dependências MCP...")
            
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp", "fastmcp"])
                logger.info("✅ Dependências MCP instaladas")
                return True
            except subprocess.CalledProcessError:
                logger.error("❌ Falha ao instalar dependências MCP")
                return False
    
    def setup_environment(self):
        """Configura o ambiente necessário"""
        logger.info("🔧 Configurando ambiente...")
        
        # Verificar se estamos no diretório correto
        if not Path("hephaestus_mcp_server.py").exists():
            logger.error("❌ Arquivo hephaestus_mcp_server.py não encontrado!")
            logger.error("Execute este script na raiz do projeto Hephaestus")
            return False
        
        # Criar diretórios necessários
        Path("logs").mkdir(exist_ok=True)
        Path("reports/memory").mkdir(parents=True, exist_ok=True)
        
        # Configurar PYTHONPATH
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Configurar variável de ambiente
        os.environ["PYTHONPATH"] = f"{os.environ.get('PYTHONPATH', '')}:{current_dir}"
        
        logger.info("✅ Ambiente configurado")
        return True
    
    def signal_handler(self, signum, frame):
        """Manipula sinais para parada graceful"""
        logger.info(f"🛑 Recebido sinal {signum}, parando servidor...")
        self.stop_server()
        sys.exit(0)
    
    def start_server(self, transport="stdio"):
        """Inicia o servidor MCP"""
        logger.info(f"🚀 Iniciando servidor MCP (transporte: {transport})")
        
        try:
            # Importar e executar o servidor diretamente
            sys.path.insert(0, os.getcwd())
            
            # Executar em processo separado para evitar conflitos asyncio
            cmd = [sys.executable, "hephaestus_mcp_server.py", transport]
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.running = True
            logger.info("✅ Servidor iniciado com sucesso!")
            
            # Monitorar saída do servidor
            while self.running and self.server_process.poll() is None:
                if self.server_process.stdout:
                    line = self.server_process.stdout.readline()
                    if line:
                        # Repassar logs do servidor
                        print(line.strip())
                time.sleep(0.1)
            
            # Verificar se o processo terminou
            if self.server_process.poll() is not None:
                return_code = self.server_process.returncode
                if return_code != 0:
                    logger.error(f"❌ Servidor falhou com código {return_code}")
                    return False
                else:
                    logger.info("✅ Servidor finalizado normalmente")
                    return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar servidor: {e}")
            return False
    
    def stop_server(self):
        """Para o servidor MCP"""
        self.running = False
        
        if self.server_process:
            logger.info("🛑 Parando servidor MCP...")
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                logger.info("✅ Servidor parado")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Servidor não respondeu, forçando parada...")
                self.server_process.kill()
                self.server_process.wait()
                logger.info("✅ Servidor forçado a parar")
            except Exception as e:
                logger.error(f"❌ Erro ao parar servidor: {e}")
    
    def run(self, transport="stdio", restart_on_failure=True):
        """Executa o servidor com reinicialização automática"""
        logger.info("🚀 Iniciando Runner do Servidor MCP Hephaestus")
        logger.info("=" * 50)
        
        # Verificar dependências
        if not self.check_dependencies():
            return False
        
        # Configurar ambiente
        if not self.setup_environment():
            return False
        
        # Configurar manipuladores de sinal
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Loop principal
        attempt = 1
        while True:
            logger.info(f"🎯 Tentativa {attempt} de iniciar servidor...")
            
            success = self.start_server(transport)
            
            if success:
                logger.info("✅ Servidor finalizado com sucesso")
                break
            
            if not restart_on_failure:
                logger.error("❌ Servidor falhou e reinicialização está desabilitada")
                break
            
            logger.warning(f"⚠️ Tentativa {attempt} falhou, tentando novamente em 5 segundos...")
            time.sleep(5)
            attempt += 1
            
            if attempt > 5:
                logger.error("❌ Muitas tentativas falharam, desistindo...")
                break
        
        return True

def main():
    """Função principal"""
    # Verificar argumentos
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    restart = "--no-restart" not in sys.argv
    
    if transport not in ["stdio", "sse"]:
        logger.error(f"❌ Transporte inválido: {transport}")
        logger.info("Uso: python run_mcp.py [stdio|sse] [--no-restart]")
        return False
    
    # Executar servidor
    runner = MCPServerRunner()
    return runner.run(transport, restart)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 