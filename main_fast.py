#!/usr/bin/env python3
"""
HEPHAESTUS FAST BOOT - Inicialização Otimizada
Versão acelerada com carregamento assíncrono e lazy loading
"""

import asyncio
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
from datetime import datetime

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variáveis globais para componentes
hephaestus_agent_instance = None
components_loaded = {}

@asynccontextmanager
async def fast_lifespan(app: FastAPI):
    """Lifespan otimizado com carregamento assíncrono"""
    global hephaestus_agent_instance
    
    logger.info("🚀 FAST BOOT: Starting Hephaestus...")
    start_time = time.time()
    
    try:
        # 1. Carregamento básico PRIMEIRO
        logger.info("📦 Loading essential components...")
        from hephaestus.utils.config_loader import load_config
        config = load_config()
        
        # 2. Inicializar FastAPI rapidamente
        logger.info("🌐 FastAPI ready for requests")
        
        # 3. Carregar componentes em background
        async def load_components():
            try:
                logger.info("🧠 Loading Meta-Intelligence (background)...")
                
                from hephaestus.core.agent import HephaestusAgent
                from hephaestus.utils.queue_manager import QueueManager
                
                # Queue manager
                queue_manager = QueueManager()
                
                # Agent principal
                hephaestus_agent_instance = HephaestusAgent(
                    logger_instance=logger,
                    config=config,
                    continuous_mode=True,
                    queue_manager=queue_manager,
                    disable_signal_handlers=True
                )
                
                components_loaded['agent'] = True
                logger.info("✅ Core agent loaded")
                
                # Componentes opcionais (não críticos)
                try:
                    from hephaestus.intelligence.model_optimizer import get_model_optimizer
                    model_config = config.get("models", {}).get("architect_default", {})
                    optimizer = get_model_optimizer(model_config, logger)
                    components_loaded['optimizer'] = True
                    logger.info("✅ Model optimizer loaded")
                except Exception as e:
                    logger.warning(f"⚠️ Model optimizer failed: {e}")
                
                total_time = time.time() - start_time
                logger.info(f"🎉 FAST BOOT COMPLETE: {total_time:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ Background loading failed: {e}")
        
        # Iniciar carregamento em background
        asyncio.create_task(load_components())
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Fast lifespan error: {e}")
        yield
    
    finally:
        logger.info("🛑 Fast shutdown")

# FastAPI com configuração mínima
app = FastAPI(
    title="Hephaestus Fast",
    description="Meta-Intelligence API - Fast Boot Mode",
    version="4.0.0-fast",
    lifespan=fast_lifespan
)

# CORS básico
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint básico"""
    return {
        "message": "Hephaestus Fast Boot",
        "status": "running",
        "components_loaded": components_loaded,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check otimizado"""
    return {
        "status": "healthy" if components_loaded.get('agent') else "loading",
        "components": components_loaded,
        "fast_boot": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def status():
    """Status detalhado"""
    global hephaestus_agent_instance
    
    agent_status = "not_loaded"
    if hephaestus_agent_instance:
        agent_status = "loaded"
    
    return {
        "fast_boot_mode": True,
        "agent_status": agent_status,
        "components_loaded": components_loaded,
        "meta_intelligence_active": components_loaded.get('optimizer', False),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/agent/execute")
async def execute_agent(objective: str):
    """Executar agente (se carregado)"""
    global hephaestus_agent_instance
    
    if not hephaestus_agent_instance:
        return {
            "status": "error",
            "message": "Agent not loaded yet. Please wait for background loading to complete."
        }
    
    try:
        # Executar objetivo
        result = await hephaestus_agent_instance.process_objective(objective)
        return {
            "status": "success",
            "objective": objective,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("🚀 HEPHAESTUS FAST BOOT MODE")
    print("⚡ Optimized for rapid startup")
    print("🌐 Starting server...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )