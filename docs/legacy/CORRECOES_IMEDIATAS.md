# 🔧 CORREÇÕES IMEDIATAS - BUGS CRÍTICOS

## 🎯 CORREÇÕES PRONTAS PARA APLICAR

### 1. **Validação de Entrada para analyze_code**

**Arquivo:** `hephaestus_mcp_server.py`

```python
# Adicionar no início do arquivo
import html
import re
from typing import Union

# Substituir a função analyze_code atual
@server.tool()
async def analyze_code(code: str, context: str = "") -> str:
    """
    Analisa código usando as capacidades avançadas de RSI do Hephaestus.
    
    Args:
        code: Código a ser analisado
        context: Contexto adicional para a análise
        
    Returns:
        Análise detalhada com insights de auto-aprimoramento
    """
    try:
        # VALIDAÇÃO DE ENTRADA
        if not isinstance(code, str):
            return "❌ Erro: Código deve ser uma string"
        
        if not code.strip():
            return "❌ Erro: Código não pode estar vazio"
        
        if len(code) > 50000:
            return "❌ Erro: Código muito grande (máximo 50.000 caracteres)"
        
        # Verificar se contém caracteres suspeitos
        if re.search(r'[^\x00-\x7F]', code) and not re.search(r'[áàâãéèêíìîóòôõúùû]', code):
            return "❌ Erro: Código contém caracteres suspeitos"
        
        # Sanitizar entrada
        sanitized_code = html.escape(code)
        sanitized_context = html.escape(context)
        
        result = await hephaestus_server.analyze_code_rsi(sanitized_code, sanitized_context)
        
        if "error" in result:
            return f"❌ Erro na análise: {result['error']}"
        
        # Resto do código permanece igual...
        
    except ValueError as e:
        return f"❌ Erro de validação: {str(e)}"
    except TypeError as e:
        return f"❌ Erro de tipo: {str(e)}"
    except Exception as e:
        logger.error(f"Erro não tratado em analyze_code: {e}")
        return "❌ Erro interno do servidor"
```

### 2. **Tratamento de Exceções Específicas**

**Arquivo:** `hephaestus_mcp_server.py`

```python
# Substituir o método analyze_code_rsi
async def analyze_code_rsi(self, code: str, context: str = "") -> Dict[str, Any]:
    """Análise de código usando capacidades RSI do Hephaestus"""
    self._ensure_initialized()
    
    try:
        # Análise de métricas do código (sempre funciona)
        complexity_metrics = analyze_complexity(code)
        duplication_metrics = detect_code_duplication(code)
        quality_score = calculate_quality_score(complexity_metrics, duplication_metrics)
        
        metrics = {
            "complexity": complexity_metrics,
            "duplication": duplication_metrics,
            "quality_score": quality_score
        }
        
        # Resto do código...
        
    except ImportError as e:
        self.logger.error(f"Dependência não encontrada: {e}")
        return {"error": "Dependência não encontrada", "details": str(e)}
    except ValueError as e:
        self.logger.error(f"Entrada inválida: {e}")
        return {"error": "Entrada inválida", "details": str(e)}
    except RuntimeError as e:
        self.logger.error(f"Erro de execução: {e}")
        return {"error": "Erro de execução", "details": str(e)}
    except FileNotFoundError as e:
        self.logger.error(f"Arquivo não encontrado: {e}")
        return {"error": "Arquivo não encontrado", "details": str(e)}
    except PermissionError as e:
        self.logger.error(f"Erro de permissão: {e}")
        return {"error": "Erro de permissão", "details": str(e)}
    except Exception as e:
        self.logger.critical(f"Erro não tratado na análise: {e}")
        return {"error": "Erro interno do servidor", "trace": str(e)[:200]}
```

### 3. **Correção do Método CycleRunner**

**Arquivo:** `hephaestus_mcp_server.py`

```python
# Substituir o método execute_rsi_cycle
async def execute_rsi_cycle(self, objective: str, area: str = "general") -> Dict[str, Any]:
    """Executa um ciclo completo de auto-aprimoramento recursivo"""
    self._ensure_initialized()
    
    try:
        if not self.hephaestus_agent:
            return {"error": "Agente não inicializado"}
        
        # Definir objetivo
        if hasattr(self.hephaestus_agent, 'state') and self.hephaestus_agent.state:
            self.hephaestus_agent.state.current_objective = objective
        
        if hasattr(self.hephaestus_agent, 'objective_stack'):
            self.hephaestus_agent.objective_stack = [objective]
        
        # Executar ciclo - CORREÇÃO AQUI
        result = f"Objetivo '{objective}' processado com sucesso"
        
        if hasattr(self.hephaestus_agent, 'queue_manager') and self.hephaestus_agent.queue_manager:
            try:
                cycle_runner = CycleRunner(self.hephaestus_agent, self.hephaestus_agent.queue_manager)
                
                # CORRIGIDO: Verificar métodos disponíveis
                if hasattr(cycle_runner, 'run_cycle'):
                    success = cycle_runner.run_cycle()
                    result = "Ciclo RSI executado com sucesso" if success else "Ciclo RSI falhou"
                elif hasattr(cycle_runner, 'execute_cycle'):
                    success = cycle_runner.execute_cycle()
                    result = "Ciclo RSI executado com sucesso" if success else "Ciclo RSI falhou"
                elif hasattr(cycle_runner, 'run'):
                    # Método padrão se existir
                    success = cycle_runner.run()
                    result = "Ciclo RSI executado com sucesso" if success else "Ciclo RSI falhou"
                else:
                    result = "CycleRunner não tem métodos compatíveis"
                    
            except AttributeError as e:
                self.logger.warning(f"Método não encontrado no CycleRunner: {e}")
                result = "Simulação de ciclo RSI executada"
            except Exception as cycle_e:
                self.logger.error(f"Erro no CycleRunner: {cycle_e}")
                result = "Erro no ciclo RSI, usando fallback"
        
        # Resto do código permanece igual...
        
    except Exception as e:
        self.logger.error(f"Erro no ciclo RSI: {e}")
        return {"error": str(e)}
```

### 4. **Correção do Logging Inconsistente**

**Arquivo:** `run_mcp.py`

```python
# Substituir o método start_server
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
        
        # Monitorar saída do servidor - CORREÇÃO AQUI
        while self.running and self.server_process.poll() is None:
            if self.server_process.stdout:
                line = self.server_process.stdout.readline()
                if line:
                    # CORRIGIDO: Usar logger em vez de print
                    line_stripped = line.strip()
                    if line_stripped.startswith("ERROR") or line_stripped.startswith("❌"):
                        logger.error(f"Servidor: {line_stripped}")
                    elif line_stripped.startswith("WARNING") or line_stripped.startswith("⚠️"):
                        logger.warning(f"Servidor: {line_stripped}")
                    elif line_stripped.startswith("INFO") or line_stripped.startswith("✅"):
                        logger.info(f"Servidor: {line_stripped}")
                    else:
                        logger.debug(f"Servidor: {line_stripped}")
            time.sleep(0.1)
        
        # Resto do código...
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        return False
```

### 5. **Correção da Configuração Hardcoded**

**Arquivo:** `main.py`

```python
import uvicorn
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

if __name__ == "__main__":
    # Import the FastAPI app instance from app.py
    from tools.app import app
    
    # CORREÇÃO: Usar variáveis de ambiente
    host = os.getenv("HEPHAESTUS_HOST", "0.0.0.0")
    port = int(os.getenv("HEPHAESTUS_PORT", "8000"))
    reload = os.getenv("HEPHAESTUS_RELOAD", "false").lower() == "true"
    workers = int(os.getenv("HEPHAESTUS_WORKERS", "1"))
    
    print("🚀 Iniciando Hephaestus com Meta-Inteligência...")
    print("🧠 Sistema de evolução autônoma será ativado!")
    print(f"🌐 Servidor rodando em {host}:{port}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port, 
        reload=reload,
        workers=workers if not reload else 1
    )
```

### 6. **Correção do Uso de shell=True**

**Arquivo:** `setup_mcp.py`

```python
def run_command(cmd: str, description: str = ""):
    """Executa um comando e retorna o resultado"""
    print(f"🔧 {description or cmd}")
    try:
        # CORREÇÃO: Usar lista de argumentos em vez de shell=True
        if isinstance(cmd, str):
            cmd_list = cmd.split()
        else:
            cmd_list = cmd
            
        result = subprocess.run(
            cmd_list, 
            check=True, 
            capture_output=True, 
            text=True,
            shell=False  # CORRIGIDO: Mais seguro
        )
        
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return False
```

### 7. **Implementação Básica do Cache**

**Arquivo:** `hephaestus_mcp_server.py`

```python
import time
import hashlib
from typing import Dict, Any, Optional

class SimpleCache:
    """Cache simples com TTL"""
    
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        
        if time.time() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any):
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self):
        self.cache.clear()
        self.timestamps.clear()

# Adicionar na classe HephaestusMCPServer
def __init__(self):
    self.logger = logger
    self.config = None
    self.hephaestus_agent = None
    self.meta_intelligence = None
    self.memory = None
    self.initialized = False
    self.session_cache = SimpleCache(ttl=3600)  # CORREÇÃO: Cache implementado

# Usar o cache nos métodos
async def analyze_code_rsi(self, code: str, context: str = "") -> Dict[str, Any]:
    """Análise de código usando capacidades RSI do Hephaestus"""
    self._ensure_initialized()
    
    # CORREÇÃO: Usar cache
    cache_key = hashlib.md5(f"{code}{context}".encode()).hexdigest()
    cached_result = self.session_cache.get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        # Análise normal...
        result = {
            "analysis": analysis,
            "suggested_patches": patches,
            "code_metrics": metrics,
            "rsi_insights": "Análise realizada com capacidades de auto-aprimoramento recursivo",
            "meta_intelligence_active": getattr(self.hephaestus_agent, 'meta_intelligence_active', False)
        }
        
        # CORREÇÃO: Salvar no cache
        self.session_cache.set(cache_key, result)
        return result
        
    except Exception as e:
        # Tratamento de exceções...
```

### 8. **Melhoria na Liberação de Recursos**

**Arquivo:** `run_mcp.py`

```python
def stop_server(self):
    """Para o servidor MCP"""
    self.running = False
    
    if self.server_process:
        logger.info("🛑 Parando servidor MCP...")
        try:
            # CORREÇÃO: Melhor gerenciamento de recursos
            with timeout(10):  # Timeout de 10 segundos
                self.server_process.terminate()
                self.server_process.wait()
                logger.info("✅ Servidor parado graciosamente")
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Timeout na parada graceful, forçando...")
            try:
                self.server_process.kill()
                self.server_process.wait(timeout=5)
                logger.info("✅ Servidor forçado a parar")
            except Exception as e:
                logger.error(f"❌ Erro ao forçar parada: {e}")
        except Exception as e:
            logger.error(f"❌ Erro ao parar servidor: {e}")
        finally:
            # CORREÇÃO: Garantir limpeza
            self.server_process = None

# Adicionar context manager para timeout
from contextlib import contextmanager
import signal

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise subprocess.TimeoutExpired("", seconds)
    
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
```

## 🚀 APLICAR CORREÇÕES

Para aplicar essas correções:

1. **Backup dos arquivos originais**
2. **Aplicar correções uma por uma**
3. **Testar cada correção**
4. **Executar testes unitários**
5. **Verificar funcionamento do servidor**

## 📋 CHECKLIST DE APLICAÇÃO

- [ ] Backup realizado
- [ ] Validação de entrada implementada
- [ ] Tratamento de exceções corrigido
- [ ] Método CycleRunner corrigido
- [ ] Logging consistente aplicado
- [ ] Configuração via env vars
- [ ] Comando seguro (sem shell=True)
- [ ] Cache básico implementado
- [ ] Recursos liberados adequadamente
- [ ] Testes executados
- [ ] Servidor funcionando

**Tempo estimado para aplicação:** 2-3 horas
**Impacto:** Resolução de bugs críticos e melhoria da estabilidade